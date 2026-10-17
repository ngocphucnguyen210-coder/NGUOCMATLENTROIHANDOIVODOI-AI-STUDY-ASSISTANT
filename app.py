import time
import datetime
import sqlite3
import base64
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from ai_engine import AILearningEngine

# 1. Cấu hình Trang Streamlit
st.set_page_config(
    page_title="PHUCgpt - Đồng Hành Thông Minh",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SVG Logo Chú Gấu Leo Núi Tri Thức Siêu Nét - Không Bao Giờ Lỗi Ảnh
DEFAULT_LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="110" height="110">
  <circle cx="100" cy="100" r="95" fill="#FFE4E1" stroke="#FF4081" stroke-width="4"/>
  <path d="M40 160 Q100 60 160 160 Z" fill="#F8BBD0" stroke="#D81B60" stroke-width="3"/>
  <circle cx="100" cy="85" r="35" fill="#FFFFFF" stroke="#D81B60" stroke-width="3"/>
  <circle cx="85" cy="75" r="5" fill="#2B2B2B"/>
  <circle cx="115" cy="75" r="5" fill="#2B2B2B"/>
  <ellipse cx="100" cy="88" rx="7" ry="5" fill="#FF80AB"/>
  <path d="M92 98 Q100 105 108 98" fill="none" stroke="#D81B60" stroke-width="3" stroke-linecap="round"/>
  <rect x="75" y="45" width="50" height="10" fill="#FF4081" rx="4"/>
  <polygon points="100,20 115,40 85,40" fill="#D81B60"/>
  <text x="100" y="180" font-family="'Plus Jakarta Sans', sans-serif" font-size="18" font-weight="bold" fill="#D81B60" text-anchor="middle">PHUCgpt</text>
</svg>
"""

# 2. Khởi tạo Database SQLite
def init_db():
    conn = sqlite3.connect('phucgpt_app_v2.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, provider TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, title TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, role TEXT, content TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS todos (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, task TEXT, done INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS study_time (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, subject TEXT, date TEXT, minutes INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS group_chats (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, content TEXT, timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS custom_events (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, event_date TEXT, title TEXT, type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_notes (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, title TEXT, content TEXT, pen_type TEXT, pen_color TEXT, updated_at TEXT)''')
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

# Session State Đồng hồ
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "timer_start_time" not in st.session_state:
    st.session_state.timer_start_time = 0
if "timer_accumulated" not in st.session_state:
    st.session_state.timer_accumulated = 0

# Cấu hình CSS Nền & Fix Lỗi Tương Phản Màu Chữ
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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    .stApp {{ {active_bg_css} }}

    @keyframes gradientBG {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* CSS FIX LỖI TƯƠNG PHẢN CHỮ SIDEBAR VÀ ĐĂNG NHẬP */
    [data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.96) !important;
        backdrop-filter: blur(12px);
        border-right: 2px solid #FF80AB !important;
    }}
    
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: #1A202C !important;
        font-weight: 600 !important;
    }}
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: #C2185B !important;
        font-weight: 800 !important;
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
    
    .login-card * {{
        color: #1A202C !important;
    }}

    .brand-title {{ font-size: 38px; font-weight: 800; color: #D81B60; text-align: center; margin-top: 5px; }}
    .brand-slogan {{ color: #AD1457; font-size: 15px; font-style: italic; text-align: center; margin-bottom: 15px; font-weight: 600; }}
    
    [data-testid="stChatMessageUser"] {{ background: linear-gradient(135deg, #FF80AB 0%, #FF4081 100%) !important; color: white !important; border-radius: 20px 20px 4px 20px !important; }}
    [data-testid="stChatMessageBot"] {{ background-color: rgba(255, 255, 255, 0.96) !important; color: #1A202C !important; border: 1.5px solid #FF80AB !important; border-radius: 20px 20px 20px 4px !important; box-shadow: 0 4px 15px rgba(216, 27, 96, 0.08); }}
    
    .stButton>button {{ background: linear-gradient(135deg, #FF4081 0%, #D81B60 100%) !important; color: white !important; border-radius: 12px !important; border: none !important; font-weight: 700 !important; }}

    .timer-card {{
        font-size: 52px; font-weight: 800; color: #D81B60; text-align: center; 
        background: #FFFFFF; padding: 20px; border-radius: 24px; 
        border: 3px solid #FF80AB; box-shadow: 0 8px 25px rgba(216, 27, 96, 0.15);
    }}
</style>
""", unsafe_allow_html=True)

# --- MÀN HÌNH ĐĂNG NHẬP FIX MÀU RÕ RÀNG ---
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="login-card">
            <div style="text-align:center;">{DEFAULT_LOGO_SVG}</div>
            <h1 style="color:#D81B60 !important; font-size:32px; font-weight:800; margin-top:10px;">PHUCgpt</h1>
            <p style="color:#AD1457 !important; font-style:italic; font-weight:600;">"Đồng hành thông minh, vun tròn vẹn Phúc"</p>
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

# --- SIDEBAR FIX TOÀN BỘ LOGO & TƯƠNG PHẢN ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center;">{DEFAULT_LOGO_SVG}</div>', unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>🌸 Chào, {st.session_state.username}</h3>", unsafe_allow_html=True)
    
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.current_session_id = None
        st.rerun()

    st.markdown("---")
    # TÙY CHỌN NGÔN NGỮ HỂN THỊ
    st.subheader("🌐 Ngôn ngữ (Language)")
    st.session_state.language = st.selectbox(
        "Chọn ngôn ngữ AI phản hồi:", 
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
    if st.button("✨ + Tạo đoạn chat mới", use_container_width=True):
        c = conn.cursor()
        c.execute("INSERT INTO sessions (username, title) VALUES (?, ?)", (st.session_state.username, "Đoạn chat mới"))
        conn.commit()
        st.session_state.current_session_id = c.lastrowid
        st.rerun()

    search_query = st.text_input("🔍 Tìm kiếm đoạn chat cũ...")

    st.subheader("📂 Lịch sử trò chuyện")
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

    st.markdown("---")
    st.subheader("🎙️ Giọng đọc AI Voice")
    voice_gender = st.selectbox("Giới tính:", ["Nữ", "Nam"])
    voice_region = st.selectbox("Vùng miền:", ["Miền Bắc 🇻🇳", "Miền Trung 🇻🇳", "Miền Nam 🇻🇳"])
    voice_config = f"{voice_gender} - {voice_region}"

# --- KHUNG TABS CHÍNH ---
tab_chat, tab_timer, tab_calendar, tab_todo, tab_group, tab_note = st.tabs([
    "💬 Trợ lý PHUCgpt", 
    "⏱️ Đồng Hồ Bấm Giờ Học Real-time", 
    "📅 Lịch & Sự Kiện / Sinh Nhật", 
    "📝 Kế hoạch To-Do List", 
    "👥 Nhóm Chat Chung & Video Call",
    "🎨 Note & Bút Vẽ Đa Năng"
])

# TAB 1: AI CHAT
with tab_chat:
    st.markdown(f"""
        <div style="text-align: center;">
            <div class="brand-title">PHUCgpt</div>
            <div class="brand-slogan">"Đồng hành thông minh, vun tròn vẹn Phúc"</div>
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
                    lang=st.session_state.language,
                    voice_config=voice_config
                )
                st.markdown(response)
                c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (st.session_state.current_session_id, "bot", response))
                conn.commit()

# TAB 2: ĐỒNG HỒ BẤM GIỜ TỰ ĐỘNG CHẠY REAL-TIME
with tab_timer:
    st.subheader("⏱️ Đồng Hồ Bấm Giờ Học Tự Động Real-time")
    
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        timer_subject = st.selectbox("Chọn môn học bấm giờ:", ["Ngữ Văn", "Toán Học", "Vật Lý", "Tiếng Anh", "Lịch Sử", "Hóa Học", "Sinh Học", "Khác"])
    
    # Tính thời gian đã trôi qua
    if st.session_state.timer_running:
        elapsed = st.session_state.timer_accumulated + (time.time() - st.session_state.timer_start_time)
    else:
        elapsed = st.session_state.timer_accumulated

    mins, secs = divmod(int(elapsed), 60)
    hours, mins = divmod(mins, 60)
    
    st.markdown(f'<div class="timer-card">⏱️ {hours:02d}:{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("▶️ Bắt Đầu", use_container_width=True):
            if not st.session_state.timer_running:
                st.session_state.timer_running = True
                st.session_state.timer_start_time = time.time()
                st.rerun()
    with b2:
        if st.button("⏸️ Tạm Dừng", use_container_width=True):
            if st.session_state.timer_running:
                st.session_state.timer_accumulated += time.time() - st.session_state.timer_start_time
                st.session_state.timer_running = False
                st.rerun()
    with b3:
        if st.button("🔄 Đặt Lại", use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.timer_accumulated = 0
            st.rerun()
    with b4:
        if st.button("💾 Lưu Thời Gian Học", use_container_width=True):
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

    # Tự động refresh cập nhật đồng hồ chạy từng giây khi bấm Bắt đầu
    if st.session_state.timer_running:
        time.sleep(1)
        st.rerun()

# TAB 3: LỊCH VẠN NĂNG & SỰ KIỆN
with tab_calendar:
    st.subheader("📅 Lịch Vạn Năng & Sự Kiện Lớn / Sinh Nhật")
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

# TAB 4: TO-DO LIST
with tab_todo:
    st.subheader("📝 Lập Kế hoạch Học tập - To Do List")
    new_task = st.text_input("Thêm nhiệm vụ mới:")
    if st.button("➕ Thêm vào danh sách"):
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

# TAB 5: NHÓM CHAT CHUNG CÔNG KHAI & VIDEO CALL
with tab_group:
    st.subheader("👥 Phòng Học Nhóm Chung Công Khai & Video Call Trực Tuyến")
    
    st.markdown("""
    <a href="https://meet.jit.si/PHUCgpt_PhongHocNhomChung_DongHa" target="_blank">
        <button style="width:100%; background:#4CAF50; color:white; padding:15px; border-radius:12px; font-weight:bold; font-size:18px; border:none; cursor:pointer;">
            📹 Tham gia Phòng Video Call & Audio Call Nhóm Trực Tuyến ↗
        </button>
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎨 Gửi Sticker")
    stk_cols = st.columns(4)
    stickers = ["🌸 Tố chất!", "🔥 Quyết chiến!", "📚 Học bài thôi!", "💯 10 Điểm!"]
    for i, stk in enumerate(stickers):
        if stk_cols[i].button(stk):
            c = conn.cursor()
            c.execute("INSERT INTO group_chats (sender, content, timestamp) VALUES (?, ?, ?)", (st.session_state.username, f"[Sticker]: {stk}", datetime.datetime.now().strftime("%H:%M")))
            conn.commit()
            st.rerun()

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

# TAB 6: NOTE & BÚT VẼ ĐA NĂNG (MỚI)
with tab_note:
    st.subheader("🎨 Trình Ghi Chú & Bút Vẽ Đa Năng (Rich Text & Custom Pen)")
    
    col_n1, col_n2 = st.columns([1, 1])
    
    with col_n1:
        note_title = st.text_input("Tiêu đề ghi chú:", placeholder="Ví dụ: Phân tích Chí Phèo - Nam Cao...")
        pen_type = st.selectbox("Tùy chọn loại bút:", ["✏️ Bút Chì (Standard)", "✒️ Bút Mực / Bút Cọ", "🖍️ Bút Dạ Quang (Highlighter)", "🧹 Cục Tẩy (Eraser)"])
        pen_color = st.color_picker("🎨 Bộ Trộn Màu Bút / Chữ (Toàn bộ màu thế giới):", "#D81B60")
    
    with col_n2:
        st.markdown("### 📝 Nội dung Note (Định dạng Word)")
        note_content = st.text_area("Nhập nội dung văn bản ghi chú:", height=180, placeholder="Viết các ý chính, công thức, dàn ý vào đây...")

    if st.button("💾 Lưu Ghi Chú Vào Bách Khoa Note"):
        if note_title.strip() and note_content.strip():
            c = conn.cursor()
            now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            c.execute("INSERT INTO user_notes (username, title, content, pen_type, pen_color, updated_at) VALUES (?, ?, ?, ?, ?, ?)", 
                      (st.session_state.username, note_title, note_content, pen_type, pen_color, now_str))
            conn.commit()
            st.success(f"Đã lưu thành công Ghi chú '{note_title}'!")
            st.rerun()
        else:
            st.warning("Vui lòng điền Tiêu đề và Nội dung Note!")

    st.markdown("---")
    st.subheader("📂 Danh Sách Ghi Chú Đã Lưu")
    c = conn.cursor()
    c.execute("SELECT id, title, content, pen_type, pen_color, updated_at FROM user_notes WHERE username = ? ORDER BY id DESC", (st.session_state.username,))
    saved_notes = c.fetchall()
    
    if saved_notes:
        for nid, ntitle, nct, npt, npc, nup in saved_notes:
            with st.expander(f"📌 {ntitle} ({nup}) - [{npt}]"):
                st.markdown(f"<div style='border-left: 4px solid {npc}; padding-left: 10px;'>{nct}</div>", unsafe_allow_html=True)
                if st.button("🗑️ Xóa Note này", key=f"del_note_{nid}"):
                    c.execute("DELETE FROM user_notes WHERE id = ?", (nid,))
                    conn.commit()
                    st.rerun()
    else:
        st.info("Chưa có ghi chú nào được lưu.")
