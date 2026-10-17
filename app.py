import time
import datetime
import sqlite3
import base64
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from ai_engine import AILearningEngine

try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False

# 1. Cấu hình Trang Streamlit
st.set_page_config(
    page_title="PHUCgpt - Tận Tụy Hôm Nay, Dẫn Đầu Ngày Mai",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# LOGO CHÍNH THỨC CỦA PHÚC (CHÚ GẤU LEO NÚI TRI THỨC Y CHANG 100%)
OFFICIAL_LOGO_URL = "https://raw.githubusercontent.com/nguocmatlentroihandoivodoi-ai-study-assistant/main/logo.png"

# 2. Khởi tạo Database SQLite
def init_db():
    conn = sqlite3.connect('phucgpt_app_v5.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, provider TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, title TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, role TEXT, content TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS todos (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, task TEXT, done INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS study_time (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, subject TEXT, date TEXT, minutes INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS group_chats (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, content TEXT, timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS custom_events (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, event_date TEXT, title TEXT, type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_notes (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, title TEXT, content TEXT, updated_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_drawings (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, title TEXT, image_data TEXT, updated_at TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# 3. Khởi tạo Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "bg_theme" not in st.session_state:
    st.session_state.bg_theme = "Hồng Pastel Mộng Mơ"
if "custom_bg_base64" not in st.session_state:
    st.session_state.custom_bg_base64 = None
if "language" not in st.session_state:
    st.session_state.language = "Tiếng Việt 🇻🇳"

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "timer_start_time" not in st.session_state:
    st.session_state.timer_start_time = 0
if "timer_accumulated" not in st.session_state:
    st.session_state.timer_accumulated = 0

TRANSLATIONS_DICT = {
    "Tiếng Việt 🇻🇳": {
        "slogan": "PhucGPT: Tận tụy hôm nay, dẫn đầu ngày mai.",
        "tab_chat": "💬 Trợ lý PHUCgpt",
        "tab_timer": "⏱️ Đồng Hồ Bấm Giờ Học Real-time",
        "tab_calendar": "📅 Lịch & Sự Kiện / Sinh Nhật",
        "tab_todo": "📝 Kế hoạch To-Do List",
        "tab_group": "👥 Nhóm Chat Chung & Video Call",
        "tab_note": "🎨 Note & Bút Vẽ Đa Năng",
        "welcome": "🌸 Chào",
        "logout": "🚪 Đăng xuất",
        "new_chat": "✨ + Tạo đoạn chat mới",
        "search_chat": "🔍 Tìm kiếm đoạn chat cũ...",
        "chat_history": "📂 Lịch sử trò chuyện",
        "start_timer": "▶️ Bắt Đầu",
        "pause_timer": "⏸️ Tạm Dừng",
        "reset_timer": "🔄 Đặt Lại",
        "save_timer": "💾 Lưu Thời Gian Học",
        "add_task": "➕ Thêm vào danh sách",
        "join_video": "📹 Tham gia Phòng Video Call & Audio Call Nhóm Trực Tuyến ↗"
    },
    "English 🇬🇧": {
        "slogan": "PhucGPT: Dedicated today, leading tomorrow.",
        "tab_chat": "💬 PHUCgpt Assistant",
        "tab_timer": "⏱️ Real-time Study Stopwatch",
        "tab_calendar": "📅 Calendar & Events / Birthdays",
        "tab_todo": "📝 To-Do List Plan",
        "tab_group": "👥 Public Group & Video Call",
        "tab_note": "🎨 Notes & Multi-Pen Drawing",
        "welcome": "🌸 Welcome",
        "logout": "🚪 Log out",
        "new_chat": "✨ + New Chat Session",
        "search_chat": "🔍 Search chat history...",
        "chat_history": "📂 Chat History",
        "start_timer": "▶️ Start",
        "pause_timer": "⏸️ Pause",
        "reset_timer": "🔄 Reset",
        "save_timer": "💾 Save Study Time",
        "add_task": "➕ Add to list",
        "join_video": "📹 Join Online Video & Audio Group Call ↗"
    }
}

lang_key = st.session_state.language
t_dict = TRANSLATIONS_DICT.get(lang_key, TRANSLATIONS_DICT["Tiếng Việt 🇻🇳"])

bg_preset_styles = {
    "Hồng Pastel Mộng Mơ": "background: linear-gradient(-45deg, #FFF0F5, #FFE4E1, #FCE4EC, #F8BBD0); background-size: 400% 400%; animation: gradientBG 12s ease infinite;",
    "Dải Ngân Hà Hồng (Pink Galaxy)": "background: linear-gradient(-45deg, #2b1055, #7597de, #B19FF9, #FFB6C1); background-size: 400% 400%; animation: gradientBG 10s ease infinite;",
    "Sóng Biển Hồng (Soft Waves)": "background: linear-gradient(-45deg, #FFC0CB, #E6E6FA, #FFF0F5, #FFB6C1); background-size: 400% 400%; animation: gradientBG 15s ease infinite;",
    "Dark Mode Hồng Đêm": "background: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #e94560); background-size: 400% 400%; animation: gradientBG 10s ease infinite;",
    "Màu Hồng Tĩnh": "background-color: #FFF0F5;"
}

if st.session_state.custom_bg_base64:
    active_bg_css = f"background-image: url('data:image/png;base64,{st.session_state.custom_bg_base64}'); background-size: cover; background-attachment: fixed;"
else:
    active_bg_css = bg_preset_styles[st.session_state.bg_theme]

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@600;700&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    .stApp {{ {active_bg_css} }}

    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    [data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.96) !important;
        backdrop-filter: blur(12px);
        border-right: 2px solid #FF80AB !important;
    }}
    
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: #1A202C !important;
        font-weight: 600 !important;
    }}

    .login-card {{
        background: rgba(255, 255, 255, 0.98);
        padding: 30px;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(216, 27, 96, 0.2);
        border: 2px solid #FF80AB;
        text-align: center;
        max-width: 480px;
        margin: auto;
    }}

    .brand-title-fancy {{
        font-family: 'Fredoka', sans-serif;
        font-size: 46px;
        font-weight: 700;
        text-align: center;
        color: #D81B60;
        margin-top: 5px;
        margin-bottom: 0px;
    }}

    .brand-slogan-new {{
        color: #C2185B !important;
        font-size: 15px;
        font-weight: 700;
        font-style: italic;
        text-align: center;
        margin-bottom: 20px;
    }}
    
    [data-testid="stChatMessageUser"] {{ background: linear-gradient(135deg, #FF80AB 0%, #FF4081 100%) !important; color: white !important; border-radius: 20px 20px 4px 20px !important; }}
    [data-testid="stChatMessageBot"] {{ background-color: rgba(255, 255, 255, 0.96) !important; color: #1A202C !important; border: 1.5px solid #FF80AB !important; border-radius: 20px 20px 20px 4px !important; box-shadow: 0 4px 15px rgba(216, 27, 96, 0.08); }}
    
    .stButton>button {{ background: linear-gradient(135deg, #FF4081 0%, #D81B60 100%) !important; color: white !important; border-radius: 12px !important; border: none !important; font-weight: 700 !important; }}

    .timer-card {{
        font-size: 52px; font-weight: 800; color: #D81B60; text-align: center; 
        background: #FFFFFF; padding: 20px; border-radius: 24px; 
        border: 3px solid #FF80AB; box-shadow: 0 8px 25px rgba(216, 27, 96, 0.15);
    }}
    
    .logo-official-img {{
        max-width: 130px;
        border-radius: 20px;
        box-shadow: 0 8px 20px rgba(216, 27, 96, 0.2);
    }}
</style>
""", unsafe_allow_html=True)

# --- MÀN HÌNH ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="login-card">
            <div style="text-align:center;">
                <img src="{OFFICIAL_LOGO_URL}" class="logo-official-img" onerror="this.src='https://cdn-icons-png.flaticon.com/512/869/869840.png'">
            </div>
            <div class="brand-title-fancy">PHUCgpt</div>
            <div class="brand-slogan-new">"{t_dict['slogan']}"</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🔑 Đăng nhập / Liên kết ứng dụng")
        auth_choice = st.selectbox("Chọn nền tảng liên kết:", ["🌐 Google / Gmail", "📘 Facebook", "🍏 Apple / iCloud"])
        linked_email = st.text_input("Nhập Tên tài khoản / Email của bạn:")

        if st.button("🚀 Bắt đầu sử dụng ngay", use_container_width=True):
            if linked_email.strip() == "":
                st.warning("Vui lòng nhập tên tài khoản!")
            else:
                st.session_state.logged_in = True
                st.session_state.username = linked_email
                
                c = conn.cursor()
                c.execute("SELECT id FROM sessions WHERE username = ?", (linked_email,))
                first_sess = c.fetchone()
                if not first_sess:
                    c.execute("INSERT INTO sessions (username, title) VALUES (?, ?)", (linked_email, "Đoạn chat mới"))
                    conn.commit()
                    st.session_state.current_session_id = c.lastrowid
                else:
                    st.session_state.current_session_id = first_sess[0]
                st.rerun()
    st.stop()

ai_engine = AILearningEngine()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center;"><img src="{OFFICIAL_LOGO_URL}" class="logo-official-img" width="110" onerror="this.src=\'https://cdn-icons-png.flaticon.com/512/869/869840.png\'"></div>', unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>{t_dict['welcome']}, {st.session_state.username}</h3>", unsafe_allow_html=True)
    
    if st.button(t_dict["logout"], use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.current_session_id = None
        st.rerun()

    st.markdown("---")
    st.subheader("🌐 Ngôn ngữ (Language)")
    st.session_state.language = st.selectbox(
        "Ngôn ngữ hiển thị / Response Lang:", 
        ["Tiếng Việt 🇻🇳", "English 🇬🇧", "한국어 🇰🇷", "日本語 🇯🇵", "Français 🇫🇷", "Deutsch 🇩🇪", "Español 🇪🇸", "Русский 🇷🇺"]
    )

    st.markdown("---")
    st.subheader("🎨 Giao diện & Hình nền")
    selected_bg = st.selectbox("Hình nền sẵn có:", list(bg_preset_styles.keys()), index=list(bg_preset_styles.keys()).index(st.session_state.bg_theme))
    if selected_bg != st.session_state.bg_theme and not st.session_state.custom_bg_base64:
        st.session_state.bg_theme = selected_bg
        st.rerun()

    bg_file = st.file_uploader("🖼️ Tải ảnh nền từ máy:", type=["png", "jpg", "jpeg"])
    if bg_file:
        b64 = base64.b64encode(bg_file.getvalue()).decode('utf-8')
        st.session_state.custom_bg_base64 = b64
        st.rerun()

    if st.session_state.custom_bg_base64 and st.button("🔄 Đặt lại hình nền"):
        st.session_state.custom_bg_base64 = None
        st.rerun()

    st.markdown("---")
    if st.button(t_dict["new_chat"], use_container_width=True):
        c = conn.cursor()
        c.execute("INSERT INTO sessions (username, title) VALUES (?, ?)", (st.session_state.username, "Đoạn chat mới"))
        conn.commit()
        st.session_state.current_session_id = c.lastrowid
        st.rerun()

    search_query = st.text_input(t_dict["search_chat"])

    st.subheader(t_dict["chat_history"])
    c = conn.cursor()
    if search_query:
        c.execute("SELECT id, title FROM sessions WHERE username = ? AND title LIKE ?", (st.session_state.username, f"%{search_query}%"))
    else:
        c.execute("SELECT id, title FROM sessions WHERE username = ?", (st.session_state.username,))
    sessions = c.fetchall()

    for sess_id, sess_title in sessions:
        cols = st.columns([3, 1])
        with cols[0]:
            if st.button(f"💬 {sess_title[:15]}", key=f"sess_{sess_id}", use_container_width=True):
                st.session_state.current_session_id = sess_id
                st.rerun()
        with cols[1]:
            if st.button("🗑️", key=f"del_{sess_id}"):
                c.execute("DELETE FROM messages WHERE session_id = ?", (sess_id,))
                c.execute("DELETE FROM sessions WHERE id = ?", (sess_id,))
                conn.commit()
                st.rerun()

# --- KHUNG TABS CHÍNH ---
tab_chat, tab_timer, tab_calendar, tab_todo, tab_group, tab_note = st.tabs([
    t_dict["tab_chat"], 
    t_dict["tab_timer"], 
    t_dict["tab_calendar"], 
    t_dict["tab_todo"], 
    t_dict["tab_group"],
    t_dict["tab_note"]
])

# TAB 1: AI CHAT
with tab_chat:
    st.markdown(f"""
        <div style="text-align: center;">
            <div class="brand-title-fancy">PHUCgpt</div>
            <div class="brand-slogan-new">"{t_dict['slogan']}"</div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.current_session_id:
        c = conn.cursor()
        c.execute("SELECT role, content FROM messages WHERE session_id = ?", (st.session_state.current_session_id,))
        for role, content in c.fetchall():
            with st.chat_message(role):
                st.markdown(content)

    st.markdown("### 📎 Đính kèm tệp & Ghi âm")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Gửi ảnh hoặc Tệp tài liệu:", type=["png", "jpg", "jpeg", "pdf", "txt", "docx"])
    with col2:
        st.markdown("**🎙️ Ghi âm giọng nói:**")
        audio_bytes = audio_recorder(text="Bấm để ghi âm", recording_color="#FF4081", neutral_color="#E0E0E0", icon_size="2x")

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

    prompt = st.chat_input("Hỏi PHUCgpt bất kỳ câu hỏi, bài tập hoặc yêu cầu nào...")

    if prompt or uploaded_file or audio_bytes:
        user_msg = prompt if prompt else "[Yêu cầu kèm tệp/ghi âm]"
        
        c = conn.cursor()
        c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (st.session_state.current_session_id, "user", user_msg))
        conn.commit()

        with st.chat_message("user"):
            if uploaded_file and "image" in uploaded_file.type:
                st.image(uploaded_file, width=280)
            st.markdown(user_msg)

        c.execute("SELECT title FROM sessions WHERE id = ?", (st.session_state.current_session_id,))
        res_title = c.fetchone()
        if res_title and res_title[0] == "Đoạn chat mới":
            new_title = user_msg[:20] + "..." if len(user_msg) > 20 else user_msg
            c.execute("UPDATE sessions SET title = ? WHERE id = ?", (new_title, st.session_state.current_session_id))
            conn.commit()

        with st.chat_message("bot"):
            with st.spinner("PHUCgpt đang lắng nghe và suy ngẫm..."):
                response = ai_engine.generate_response(
                    prompt=user_msg, 
                    file_attachment=uploaded_file, 
                    file_type=uploaded_file.type if uploaded_file else None,
                    lang=st.session_state.language
                )
                st.markdown(response)
                c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (st.session_state.current_session_id, "bot", response))
                conn.commit()

# TAB 2: BẤM GIỜ
with tab_timer:
    st.subheader(t_dict["tab_timer"])
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        timer_subject = st.selectbox("Chọn môn học bấm giờ:", ["Ngữ Văn", "Toán Học", "Vật Lý", "Tiếng Anh", "Lịch Sử", "Hóa Học", "Sinh Học", "Khác"])
    
    if st.session_state.timer_running:
        elapsed = st.session_state.timer_accumulated + (time.time() - st.session_state.timer_start_time)
    else:
        elapsed = st.session_state.timer_accumulated

    mins, secs = divmod(int(elapsed), 60)
    hours, mins = divmod(mins, 60)
    st.markdown(f'<div class="timer-card">⏱️ {hours:02d}:{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button(t_dict["start_timer"], use_container_width=True):
            if not st.session_state.timer_running:
                st.session_state.timer_running = True
                st.session_state.timer_start_time = time.time()
                st.rerun()
    with b2:
        if st.button(t_dict["pause_timer"], use_container_width=True):
            if st.session_state.timer_running:
                st.session_state.timer_accumulated += time.time() - st.session_state.timer_start_time
                st.session_state.timer_running = False
                st.rerun()
    with b3:
        if st.button(t_dict["reset_timer"], use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.timer_accumulated = 0
            st.rerun()
    with b4:
        if st.button(t_dict["save_timer"], use_container_width=True):
            if st.session_state.timer_running:
                st.session_state.timer_accumulated += time.time() - st.session_state.timer_start_time
                st.session_state.timer_running = False
            
            saved_mins = max(1, int(st.session_state.timer_accumulated // 60))
            today_str = str(datetime.date.today())
            c = conn.cursor()
            c.execute("INSERT INTO study_time (username, subject, date, minutes) VALUES (?, ?, ?, ?)", (st.session_state.username, timer_subject, today_str, saved_mins))
            conn.commit()
            st.session_state.timer_accumulated = 0
            st.success(f"🎉 Đã lưu {saved_mins} phút học môn {timer_subject}!")
            st.rerun()

    if st.session_state.timer_running:
        time.sleep(1)
        st.rerun()

# TAB 3: LỊCH
with tab_calendar:
    st.subheader(t_dict["tab_calendar"])
    col_c1, col_c2 = st.columns([1, 1])
    with col_c1:
        selected_date = st.date_input("📆 Chọn ngày:", datetime.date.today())
        holidays_dict = {
            "01-01": "🎆 Tết Dương Lịch", "02-03": "🚩 Ngày thành lập Đảng CCSVN",
            "03-08": "💐 Quốc tế Phụ nữ", "03-26": "🔥 Ngày thành lập Đoàn TNCS",
            "04-30": "🇻🇳 Ngày Giải phóng miền Nam", "05-01": "🛠️ Quốc tế Lao động",
            "05-19": "⭐ Sinh nhật Bác Hồ", "09-02": "🇻🇳 Ngày Quốc khánh",
            "10-20": "🌸 Ngày Phụ nữ Việt Nam", "11-20": "👨‍🏫 Ngày Nhà giáo Việt Nam"
        }
        date_key = selected_date.strftime("%m-%d")
        if date_key in holidays_dict:
            st.success(f"🎉 **Ngày lễ:** {holidays_dict[date_key]}")

        c = conn.cursor()
        c.execute("SELECT title, type FROM custom_events WHERE username = ? AND event_date = ?", (st.session_state.username, str(selected_date)))
        for t, tp in c.fetchall():
            st.write(f"- [{tp}] **{t}**")

    with col_c2:
        st.markdown("### ⚙️ Thêm Sự Kiện / Sinh Nhật Cá Nhân")
        ev_title = st.text_input("Tên sự kiện / Sinh nhật:")
        ev_type = st.selectbox("Loại:", ["🎂 Sinh nhật", "📚 Kiểm tra / Thi cử", "🎉 Kỷ niệm", "📌 Khác"])
        ev_date = st.date_input("Ngày diễn ra:", datetime.date.today(), key="set_ev_d")
        if st.button("➕ Lưu Vào Lịch"):
            if ev_title.strip():
                c = conn.cursor()
                c.execute("INSERT INTO custom_events (username, event_date, title, type) VALUES (?, ?, ?, ?)", (st.session_state.username, str(ev_date), ev_title, ev_type))
                conn.commit()
                st.success("Đã thêm sự kiện!")
                st.rerun()

# TAB 4: TO-DO
with tab_todo:
    st.subheader(t_dict["tab_todo"])
    new_task = st.text_input("Thêm nhiệm vụ mới:")
    if st.button(t_dict["add_task"]):
        if new_task.strip():
            c = conn.cursor()
            c.execute("INSERT INTO todos (username, task, done) VALUES (?, ?, 0)", (st.session_state.username, new_task))
            conn.commit()
            st.rerun()

    st.markdown("---")
    c = conn.cursor()
    c.execute("SELECT id, task, done FROM todos WHERE username = ?", (st.session_state.username,))
    for task_id, task_text, is_done in c.fetchall():
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.write(f"{'✅ ~~' + task_text + '~~' if is_done else '📌 ' + task_text}")
        with col_b:
            if not is_done and st.button("Hoàn thành", key=f"done_{task_id}"):
                c.execute("UPDATE todos SET done = 1 WHERE id = ?", (task_id,))
                conn.commit()
                st.rerun()
            elif st.button("Xóa", key=f"del_td_{task_id}"):
                c.execute("DELETE FROM todos WHERE id = ?", (task_id,))
                conn.commit()
                st.rerun()

# TAB 5: NHÓM
with tab_group:
    st.subheader(t_dict["tab_group"])
    st.markdown(f'<a href="https://meet.jit.si/PHUCgpt_PhongHocNhomChung_DongHa" target="_blank"><button style="width:100%; background:#4CAF50; color:white; padding:15px; border-radius:12px; font-weight:bold; font-size:18px; border:none; cursor:pointer;">{t_dict["join_video"]}</button></a>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 💬 Trò chuyện nhóm chung")
    g_input = st.text_input("Nhập tin nhắn nhóm:")
    if st.button("Gửi tin nhắn"):
        if g_input.strip():
            c = conn.cursor()
            c.execute("INSERT INTO group_chats (sender, content, timestamp) VALUES (?, ?, ?)", (st.session_state.username, g_input, datetime.datetime.now().strftime("%H:%M")))
            conn.commit()
            st.rerun()

    c = conn.cursor()
    c.execute("SELECT sender, content, timestamp FROM group_chats ORDER BY id DESC LIMIT 20")
    for s, ct, ts in c.fetchall():
        st.markdown(f"**[{ts}] {s}**: {ct}")

# TAB 6: NOTE WORD THẬT 100% HIỂN THỊ TRỰC TIẾP LẬP TỨC
with tab_note:
    st.subheader("🎨 Trình Soạn Thảo Ghi Chú Word & Canvas Bảng Vẽ")
    
    note_mode = st.radio("Chọn chế độ Ghi Chú:", ["📝 Trình Soạn Thảo Word Lập Tức", "🖌️ Bảng Vẽ Trực Tiếp Canvas"], horizontal=True)
    
    if note_mode == "📝 Trình Soạn Thảo Word Lập Tức":
        st.markdown("### 🔤 Bảng Điều Khiển Định Dạng Word")
        
        col_w1, col_w2, col_w3 = st.columns(3)
        with col_w1:
            st_align = st.selectbox("Căn lề (Alignment):", ["Trái (Left)", "Giữa (Center)", "Phải (Right)"])
            st_font_size = st.slider("Cỡ chữ (Font Size):", 12, 36, 16)
        with col_w2:
            st_heading = st.selectbox("Kiểu tiêu đề:", ["Thường", "Tiêu đề lớn (H1)", "Tiêu đề vừa (H2)"])
            st_color = st.color_picker("🎨 Màu chữ:", "#D81B60")
        with col_w3:
            st_style = st.multiselect("Kiểu chữ:", ["In đậm (Bold)", "In nghiêng (Italic)", "Gạch chân"])
            st_table = st.checkbox("➕ Chèn Bảng Kẻ Ô Word")

        note_title = st.text_input("Tiêu đề Ghi chú:", placeholder="Nhập tiêu đề...")
        raw_text = st.text_area("Nội dung văn bản:", height=150, placeholder="Soạn nội dung ghi chú...")

        # Xử lý CSS/Markdown thật 100%
        align_css = "left" if "Trái" in st_align else ("center" if "Giữa" in st_align else "right")
        bold_css = "font-weight: bold;" if "In đậm (Bold)" in st_style else ""
        italic_css = "font-style: italic;" if "In nghiêng (Italic)" in st_style else ""
        underline_css = "text-decoration: underline;" if "Gạch chân" in st_style else ""
        
        preview_html = f"""
        <div style="text-align: {align_css}; font-size: {st_font_size}px; color: {st_color}; {bold_css} {italic_css} {underline_css} background: #FFFFFF; padding: 15px; border-radius: 10px; border: 1px solid #FF80AB; margin-top: 10px;">
            {raw_text if raw_text else "Văn bản xem trước..."}
        </div>
        """
        
        if st_table:
            preview_html += """
            <br>
            <table style="width:100%; border-collapse: collapse; border: 1px solid #FF80AB; background: white;">
              <tr style="background:#FFE4E1;">
                <th style="border: 1px solid #FF80AB; padding: 8px;">Cột 1</th>
                <th style="border: 1px solid #FF80AB; padding: 8px;">Cột 2</th>
              </tr>
              <tr>
                <td style="border: 1px solid #FF80AB; padding: 8px;">Dữ liệu A</td>
                <td style="border: 1px solid #FF80AB; padding: 8px;">Dữ liệu B</td>
              </tr>
            </table>
            """

        st.markdown("### 👁️ Hiển Thị Trực Tiếp (Live Preview):")
        st.markdown(preview_html, unsafe_allow_html=True)

        if st.button("💾 Lưu Ghi Chú Word Này"):
            if note_title.strip() and raw_text.strip():
                c = conn.cursor()
                now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                c.execute("INSERT INTO user_notes (username, title, content, updated_at) VALUES (?, ?, ?, ?)", 
                          (st.session_state.username, note_title, preview_html, now_str))
                conn.commit()
                st.success("Đã lưu Ghi chú thành công!")
                st.rerun()

    else:
        st.markdown("### 🖌️ Bảng Vẽ Trực Tiếp Canvas")
        if CANVAS_AVAILABLE:
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                drawing_mode = st.selectbox("Công cụ vẽ:", ["freedraw", "line", "rect", "circle"])
            with col_p2:
                stroke_width = st.slider("Nét bút:", 1, 20, 4)
            with col_p3:
                stroke_color = st.color_picker("🎨 Màu cọ:", "#D81B60")

            draw_title = st.text_input("Tiêu đề Bức vẽ:", placeholder="Nhập tiêu đề...")

            canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_color="#FFFFFF",
                height=300,
                drawing_mode=drawing_mode,
                key="canvas",
            )

            if st.button("💾 Lưu Bức Vẽ"):
                if draw_title.strip():
                    c = conn.cursor()
                    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                    c.execute("INSERT INTO user_drawings (username, title, image_data, updated_at) VALUES (?, ?, ?, ?)", 
                              (st.session_state.username, draw_title, "Saved Canvas", now_str))
                    conn.commit()
                    st.success("Đã lưu bức vẽ!")
                    st.rerun()

    st.markdown("---")
    st.subheader("📂 Danh Sách Ghi Chú Đã Lưu")
    c = conn.cursor()
    c.execute("SELECT id, title, content, updated_at FROM user_notes WHERE username = ? ORDER BY id DESC", (st.session_state.username,))
    for nid, ntitle, nct, nup in c.fetchall():
        with st.expander(f"📝 {ntitle} ({nup})"):
            st.markdown(nct, unsafe_allow_html=True)
            if st.button("🗑️ Xóa Note", key=f"del_n_{nid}"):
                c.execute("DELETE FROM user_notes WHERE id = ?", (nid,))
                conn.commit()
                st.rerun()
