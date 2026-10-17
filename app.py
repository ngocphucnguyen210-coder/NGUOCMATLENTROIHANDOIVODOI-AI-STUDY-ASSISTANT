import time
import datetime
import sqlite3
import base64
import streamlit as st
from PIL import Image
from audio_recorder_streamlit import audio_recorder
from ai_engine import AILearningEngine

# 1. Cấu hình Trang Streamlit
st.set_page_config(
    page_title="PHUCgpt - Đồng Hành Thông Minh",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Link Logo mới chú gấu leo núi tri thức của Gia Phúc
LOGO_URL = "https://raw.githubusercontent.com/nguocmatlentroihandoivodoi-ai-study-assistant/main/logo.png"

# 2. Khởi tạo Database SQLite nâng cấp
def init_db():
    conn = sqlite3.connect('phucgpt_database.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, provider TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, title TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, role TEXT, content TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS todos (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, task TEXT, done INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS study_time (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, subject TEXT, date TEXT, minutes INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS group_rooms (id INTEGER PRIMARY KEY AUTOINCREMENT, group_name TEXT UNIQUE, phones TEXT, created_by TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS group_chats (id INTEGER PRIMARY KEY AUTOINCREMENT, group_name TEXT, sender TEXT, content TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS custom_events (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, event_date TEXT, title TEXT, type TEXT)''')
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

# Session state cho Đồng hồ đếm giờ Real-time
if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
if "start_time" not in st.session_state:
    st.session_state.start_time = 0
if "elapsed_time" not in st.session_state:
    st.session_state.elapsed_time = 0

# Cấu hình CSS Hình nền
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

    .brand-title {{ font-size: 38px; font-weight: 800; color: #D81B60; text-align: center; margin-top: 5px; }}
    .brand-slogan {{ color: #AD1457; font-size: 15px; font-style: italic; text-align: center; margin-bottom: 15px; }}
    
    [data-testid="stChatMessageUser"] {{ background: linear-gradient(135deg, #FF80AB 0%, #FF4081 100%) !important; color: white !important; border-radius: 20px 20px 4px 20px !important; }}
    [data-testid="stChatMessageBot"] {{ background-color: rgba(255, 255, 255, 0.95) !important; color: #2D3748 !important; border: 1px solid rgba(255, 182, 193, 0.6) !important; border-radius: 20px 20px 20px 4px !important; box-shadow: 0 4px 15px rgba(216, 27, 96, 0.05); }}
    [data-testid="stSidebar"] {{ background-color: rgba(255, 255, 255, 0.9) !important; backdrop-filter: blur(10px); border-right: 1px solid rgba(255, 182, 193, 0.4); }}
    .stButton>button {{ background: linear-gradient(135deg, #FF4081 0%, #D81B60 100%) !important; color: white !important; border-radius: 12px !important; border: none !important; font-weight: 600 !important; }}

    .logo-container {{ text-align: center; padding: 10px; }}
    .logo-img {{ border-radius: 20px; box-shadow: 0 8px 20px rgba(216, 27, 96, 0.2); max-width: 140px; }}
    
    .timer-display {{ font-size: 48px; font-weight: 800; color: #D81B60; text-align: center; background: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 20px; border: 2px solid #FF80AB; margin: 15px 0; }}
</style>
""", unsafe_allow_html=True)

# --- MÀN HÌNH ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.markdown(f"""
    <div class="logo-container" style="margin-top: 3vh;">
        <img src="{LOGO_URL}" class="logo-img" onerror="this.src='https://cdn-icons-png.flaticon.com/512/869/869840.png'">
        <div class="brand-title">🌸 PHUCgpt</div>
        <div class="brand-slogan">"Đồng hành thông minh, vun tròn vẹn Phúc"</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔗 Chọn ứng dụng liên kết")
        auth_choice = st.selectbox("Chọn nền tảng:", ["🌐 Google / Gmail", "📘 Facebook", "🍏 Apple / iCloud"])
        st.markdown("---")

        if "Google" in auth_choice:
            st.markdown('<a href="https://accounts.google.com/signin" target="_blank"><button style="width:100%; background-color:#4285F4; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">Mở trang đăng nhập Google ↗</button></a>', unsafe_allow_html=True)
        elif "Facebook" in auth_choice:
            st.markdown('<a href="https://www.facebook.com/login" target="_blank"><button style="width:100%; background-color:#1877F2; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">Mở trang đăng nhập Facebook ↗</button></a>', unsafe_allow_html=True)
        elif "Apple" in auth_choice:
            st.markdown('<a href="https://appleid.apple.com/" target="_blank"><button style="width:100%; background-color:#000000; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">Mở trang đăng nhập Apple ID ↗</button></a>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        linked_email = st.text_input("Nhập email hoặc tên tài khoản của bạn:")

        if st.button("✅ Xác nhận Hoàn tất Liên kết", use_container_width=True):
            if linked_email.strip() == "":
                st.warning("Vui lòng nhập tài khoản!")
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
    st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" class="logo-img" width="90" onerror="this.src=\'https://cdn-icons-png.flaticon.com/512/869/869840.png\'"></div>', unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #D81B60; text-align: center;'>🌸 Chào, {st.session_state.username}</h3>", unsafe_allow_html=True)
    
    if st.button("🚪 Đăng xuất tài khoản", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.current_session_id = None
        st.rerun()

    st.markdown("---")
    st.subheader("🎨 Custom Tùy chọn Hình nền")
    selected_bg = st.selectbox("Hình nền sẵn có:", list(bg_preset_styles.keys()), index=list(bg_preset_styles.keys()).index(st.session_state.bg_theme))
    
    if selected_bg != st.session_state.bg_theme and not st.session_state.custom_bg_base64:
        st.session_state.bg_theme = selected_bg
        st.rerun()

    bg_file = st.file_uploader("🖼️ Tải ảnh nền từ máy (Tùy thích):", type=["png", "jpg", "jpeg"])
    if bg_file:
        b64 = base64.b64encode(bg_file.getvalue()).decode('utf-8')
        st.session_state.custom_bg_base64 = b64
        st.rerun()

    if st.session_state.custom_bg_base64 and st.button("🔄 Đặt lại hình nền mặc định"):
        st.session_state.custom_bg_base64 = None
        st.rerun()

    st.markdown("---")
    if st.button("✨ Tạo đoạn chat mới", use_container_width=True):
        c = conn.cursor()
        c.execute("INSERT INTO sessions (username, title) VALUES (?, ?)", (st.session_state.username, "Đoạn chat mới"))
        conn.commit()
        st.session_state.current_session_id = c.lastrowid
        st.rerun()

    search_query = st.text_input("🔍 Tìm kiếm cuộc chat cũ...")

    st.markdown("---")
    st.subheader("📂 Dãy lưu trữ đoạn chat")
    
    c = conn.cursor()
    if search_query:
        c.execute("SELECT id, title FROM sessions WHERE username = ? AND title LIKE ?", (st.session_state.username, f"%{search_query}%"))
    else:
        c.execute("SELECT id, title FROM sessions WHERE username = ?", (st.session_state.username,))
    sessions = c.fetchall()

    for sess_id, sess_title in sessions:
        cols = st.columns([3, 1])
        with cols[0]:
            if st.button(f"💬 {sess_title[:16]}", key=f"sess_{sess_id}", use_container_width=True):
                st.session_state.current_session_id = sess_id
                st.rerun()
        with cols[1]:
            if st.button("🗑️", key=f"del_{sess_id}", help="Xóa đoạn chat này"):
                c.execute("DELETE FROM messages WHERE session_id = ?", (sess_id,))
                c.execute("DELETE FROM sessions WHERE id = ?", (sess_id,))
                conn.commit()
                st.rerun()

    st.markdown("---")
    st.subheader("🎙️ Cấu hình Giọng đọc Voice")
    voice_gender = st.selectbox("Giới tính:", ["Nữ", "Nam"])
    voice_pitch = st.selectbox("Độ cao / Trầm:", ["Cao", "Trung bình", "Trầm ấm"])
    voice_region = st.selectbox("Vùng miền:", ["Miền Bắc 🇻🇳", "Miền Trung 🇻🇳", "Miền Nam 🇻🇳"])
    voice_config = f"{voice_gender} - {voice_pitch} - {voice_region}"

# --- KHUNG TABS CHÍNH ---
tab_chat, tab_timer, tab_calendar, tab_todo, tab_group = st.tabs([
    "💬 Trợ lý PHUCgpt", 
    "⏱️ Đồng Hồ Bấm Giờ Học Real-time", 
    "📅 Lịch & Sự Kiện / Sinh Nhật", 
    "📝 Kế hoạch To-Do List", 
    "👥 Nhóm SĐT & Video Call"
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
        messages = c.fetchall()
        
        for role, content in messages:
            with st.chat_message(role):
                st.markdown(content)

    st.markdown("### 📎 Đính kèm tệp đa phương tiện & Thu âm")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Gửi ảnh hoặc Tệp tài liệu:", type=["png", "jpg", "jpeg", "pdf", "txt", "docx"])
    with col2:
        st.markdown("**🎙️ Ghi âm giọng nói (Voice):**")
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
            if uploaded_file:
                if "image" in uploaded_file.type:
                    st.image(uploaded_file, caption="Ảnh đính kèm", width=280)
                else:
                    st.write(f"📁 Tệp: {uploaded_file.name}")
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
            st.markdown(user_msg)

        c.execute("SELECT title FROM sessions WHERE id = ?", (st.session_state.current_session_id,))
        res_title = c.fetchone()
        if res_title and res_title[0] == "Đoạn chat mới":
            new_title = user_msg[:22] + "..." if len(user_msg) > 22 else user_msg
            c.execute("UPDATE sessions SET title = ? WHERE id = ?", (new_title, st.session_state.current_session_id))
            conn.commit()

        with st.chat_message("bot"):
            with st.spinner("PHUCgpt đang lắng nghe và suy ngẫm..."):
                response = ai_engine.generate_response(
                    prompt=user_msg, 
                    file_attachment=uploaded_file, 
                    file_type=uploaded_file.type if uploaded_file else None,
                    voice_config=voice_config
                )
                st.markdown(response)
                c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (st.session_state.current_session_id, "bot", response))
                conn.commit()

# TAB 2: ĐỒNG HỒ BẤM GIỜ REAL-TIME
with tab_timer:
    st.subheader("⏱️ Đồng Hồ Bấm Giờ Học Tập Real-Time")
    
    col_ctrl1, col_ctrl2 = st.columns([1, 1])
    with col_ctrl1:
        timer_subject = st.selectbox("Chọn môn học bấm giờ:", ["Ngữ Văn", "Toán Học", "Vật Lý", "Tiếng Anh", "Lịch Sử", "Hóa Học", "Sinh Học", "Khác"])
    
    # Tính thời gian chạy
    if st.session_state.timer_running:
        current_elapsed = st.session_state.elapsed_time + (time.time() - st.session_state.start_time)
    else:
        current_elapsed = st.session_state.elapsed_time

    mins, secs = divmod(int(current_elapsed), 60)
    hours, mins = divmod(mins, 60)
    time_format = f"{hours:02d}:{mins:02d}:{secs:02d}"

    st.markdown(f'<div class="timer-display">⏱️ {time_format}</div>', unsafe_allow_html=True)

    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    with btn_col1:
        if st.button("▶️ Bắt Đầu Học", use_container_width=True):
            if not st.session_state.timer_running:
                st.session_state.timer_running = True
                st.session_state.start_time = time.time()
                st.rerun()
    with btn_col2:
        if st.button("⏸️ Tạm Dừng", use_container_width=True):
            if st.session_state.timer_running:
                st.session_state.elapsed_time += time.time() - st.session_state.start_time
                st.session_state.timer_running = False
                st.rerun()
    with btn_col3:
        if st.button("🔄 Đặt Lại", use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.elapsed_time = 0
            st.rerun()
    with btn_col4:
        if st.button("💾 Lưu Kết Quả Học", use_container_width=True):
            if st.session_state.timer_running:
                st.session_state.elapsed_time += time.time() - st.session_state.start_time
                st.session_state.timer_running = False
            
            saved_minutes = max(1, int(st.session_state.elapsed_time // 60))
            today_str = str(datetime.date.today())
            c = conn.cursor()
            c.execute("INSERT INTO study_time (username, subject, date, minutes) VALUES (?, ?, ?, ?)", (st.session_state.username, timer_subject, today_str, saved_minutes))
            conn.commit()
            
            st.session_state.elapsed_time = 0
            st.success(f"🎉 Đã lưu thành công {saved_minutes} phút học môn {timer_subject} vào ngày {today_str}!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Tổng Số Phút Học Tích Lũy Hôm Nay")
    today_str = str(datetime.date.today())
    c = conn.cursor()
    c.execute("SELECT subject, SUM(minutes) FROM study_time WHERE username = ? AND date = ? GROUP BY subject", (st.session_state.username, today_str))
    records = c.fetchall()
    if records:
        for sub, m in records:
            st.write(f"- **{sub}**: `{m}` phút")
    else:
        st.info("Chưa có thời gian học được ghi nhận hôm nay.")

# TAB 3: LỊCH VẠN NĂNG & SỰ KIỆN / SINH NHẬT
with tab_calendar:
    st.subheader("📅 Lịch Vạn Năng & Sự Kiện Lớn / Sinh Nhật")
    
    col_cal1, col_cal2 = st.columns([1, 1])
    
    with col_cal1:
        selected_date = st.date_input("📆 Chọn ngày để xem sự kiện:", datetime.date.today())
        
        # Danh sách các ngày lễ lớn cố định trong năm
        holidays_dict = {
            "01-01": "🎆 Tết Dương Lịch",
            "02-03": "🚩 Ngày thành lập Đảng CCSVN",
            "03-08": "💐 Quốc tế Phụ nữ",
            "03-26": "🔥 Ngày thành lập Đoàn TNCS Hồ Chí Minh",
            "04-30": "🇻🇳 Ngày Giải phóng miền Nam, Thống nhất đất nước",
            "05-01": "🛠️ Ngày Quốc tế Lao động",
            "05-19": "⭐ Sinh nhật Chủ tịch Hồ Chí Minh",
            "09-02": "🇻🇳 Ngày Quốc khánh nước CHXHCN Việt Nam",
            "10-20": "🌸 Ngày Phụ nữ Việt Nam",
            "11-20": "👨‍🏫 Ngày Nhà giáo Việt Nam",
            "12-22": "🎖️ Ngày thành lập QĐND Việt Nam"
        }

        date_key = selected_date.strftime("%m-%d")
        st.markdown(f"### 📌 Sự kiện ngày {selected_date.strftime('%d/%m/%Y')}:")
        
        if date_key in holidays_dict:
            st.success(f"🎉 **Ngày lễ toàn quốc:** {holidays_dict[date_key]}")
        else:
            st.info("Không có ngày lễ lớn toàn quốc vào ngày này.")

        # Tra cứu sự kiện/sinh nhật custom do người dùng tự cài đặt
        c = conn.cursor()
        c.execute("SELECT title, type FROM custom_events WHERE username = ? AND event_date = ?", (st.session_state.username, str(selected_date)))
        custom_evs = c.fetchall()
        if custom_evs:
            st.markdown("**🎂 Sự kiện cá nhân / Sinh nhật đã cài đặt:**")
            for t, tp in custom_evs:
                st.write(f"- [{tp}] **{t}**")

    with col_cal2:
        st.markdown("### ⚙️ Tự Cài Đặt Sinh Nhật / Sự Kiện Mới")
        ev_title = st.text_input("Tên sự kiện / Sinh nhật ai đó:")
        ev_type = st.selectbox("Loại sự kiện:", ["🎂 Sinh nhật", "📚 Mốc thi cử / Bài kiểm tra", "🎉 Kỷ niệm cá nhân", "📌 Khác"])
        ev_date = st.date_input("Chọn ngày diễn ra:", datetime.date.today(), key="set_ev_date")

        if st.button("➕ Lưu Sự Kiện Vào Lịch"):
            if ev_title.strip():
                c = conn.cursor()
                c.execute("INSERT INTO custom_events (username, event_date, title, type) VALUES (?, ?, ?, ?)", (st.session_state.username, str(ev_date), ev_title, ev_type))
                conn.commit()
                st.success(f"Đã thêm '{ev_title}' vào Lịch ngày {ev_date.strftime('%d/%m/%Y')}!")
                st.rerun()
            else:
                st.warning("Vui lòng nhập tên sự kiện!")

# TAB 4: TO-DO LIST
with tab_todo:
    st.subheader("📝 Lập Kế hoạch Học tập - To Do List")
    col_td1, col_td2 = st.columns([2, 1])
    
    with col_td1:
        new_task = st.text_input("Thêm nhiệm vụ / Bài tập mới:")
        if st.button("➕ Thêm vào danh sách"):
            if new_task.strip():
                c = conn.cursor()
                c.execute("INSERT INTO todos (username, task, done) VALUES (?, ?, 0)", (st.session_state.username, new_task))
                conn.commit()
                st.rerun()

    st.markdown("---")
    c = conn.cursor()
    c.execute("SELECT id, task, done FROM todos WHERE username = ?", (st.session_state.username,))
    todos = c.fetchall()
    
    for task_id, task_text, is_done in todos:
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

# TAB 5: PHÒNG HỌC NHÓM SĐT & VIDEO CALL
with tab_group:
    st.subheader("👥 Tạo Nhóm Học Tập Bằng Số Điện Thoại & Video Call")
    
    col_g1, col_g2 = st.columns([1, 1])
    
    with col_g1:
        st.markdown("### ➕ Tạo Nhóm Học Mới")
        new_group_name = st.text_input("Tên nhóm học tập:")
        phone_numbers = st.text_area("Nhập Số điện thoại thành viên (phân cách bằng dấu phẩy):", placeholder="0912345678, 0987654321, ...")
        
        if st.button("🚀 Xác nhận Tạo Nhóm"):
            if new_group_name.strip() and phone_numbers.strip():
                try:
                    c = conn.cursor()
                    c.execute("INSERT INTO group_rooms (group_name, phones, created_by) VALUES (?, ?, ?)", (new_group_name, phone_numbers, st.session_state.username))
                    conn.commit()
                    st.success(f"Đã tạo thành công nhóm '{new_group_name}' với các SĐT: {phone_numbers}")
                    st.rerun()
                except Exception as e:
                    st.error("Tên nhóm đã tồn tại hoặc có lỗi!")
            else:
                st.warning("Vui lòng điền đầy đủ Tên nhóm và Số điện thoại!")

    with col_g2:
        st.markdown("### 📂 Danh Sách Nhóm Của Bạn")
        c = conn.cursor()
        c.execute("SELECT group_name, phones FROM group_rooms")
        all_rooms = c.fetchall()
        
        if all_rooms:
            selected_room = st.selectbox("Chọn nhóm để trò chuyện:", [r[0] for r in all_rooms])
            curr_phones = [r[1] for r in all_rooms if r[0] == selected_room][0]
            st.info(f"📱 **SĐT Thành viên:** {curr_phones}")
        else:
            selected_room = "Nhóm Ôn Thi THPT Đông Hà"
            st.info("Chưa có nhóm riêng. Bạn đang trong phòng mặc định.")

    st.markdown("---")
    
    col_vid1, col_vid2 = st.columns([1, 1])
    with col_vid1:
        st.markdown(f"### 🎥 Video Call / Audio Call phòng `{selected_room}`")
        st.markdown(f'<a href="https://meet.jit.si/PHUCgpt_{selected_room.replace(" ", "_")}" target="_blank"><button style="width:100%; background:#4CAF50; color:white; padding:12px; border-radius:10px; border:none; font-weight:bold; cursor:pointer;">📹 Tham gia Video Call nhóm ↗</button></a>', unsafe_allow_html=True)
    
    with col_vid2:
        st.markdown("### 🎨 Gửi Sticker nhanh")
        sticker_cols = st.columns(4)
        stickers = ["🌸 Tố chất!", "🔥 Quyết chiến!", "📚 Học bài thôi!", "💯 10 Điểm!"]
        for i, stk in enumerate(stickers):
            if sticker_cols[i%4].button(stk):
                c = conn.cursor()
                c.execute("INSERT INTO group_chats (group_name, sender, content) VALUES (?, ?, ?)", (selected_room, st.session_state.username, f"[Sticker]: {stk}"))
                conn.commit()
                st.rerun()

    st.markdown("---")
    st.markdown(f"### 💬 Trò chuyện trong nhóm `{selected_room}`")
    group_input = st.text_input("Nhập tin nhắn nhóm:")
    if st.button("Gửi tin nhắn nhóm"):
        if group_input.strip():
            c = conn.cursor()
            c.execute("INSERT INTO group_chats (group_name, sender, content) VALUES (?, ?, ?)", (selected_room, st.session_state.username, group_input))
            conn.commit()
            st.rerun()

    c = conn.cursor()
    c.execute("SELECT sender, content FROM group_chats WHERE group_name = ? ORDER BY id DESC LIMIT 15", (selected_room,))
    for sender, msg in c.fetchall():
        st.markdown(f"**{sender}**: {msg}")
