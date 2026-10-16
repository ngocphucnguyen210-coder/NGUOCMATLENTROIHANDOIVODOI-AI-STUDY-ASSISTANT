import sqlite3
import streamlit as st
from PIL import Image
from audio_recorder_streamlit import audio_recorder
from ai_engine import AILearningEngine

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="PHUCgpt - Đồng Hành Thông Minh",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. Khởi tạo Database SQLite
def init_db():
    conn = sqlite3.connect('phucgpt_database.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            provider TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            title TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

# 3. Khởi tạo Trạng thái Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

# --- MÀN HÌNH ĐĂNG NHẬP & LIÊN KẾT ỨNG DỤNG ---
if not st.session_state.logged_in:
    st.markdown("""
    <style>
        .login-card {
            background: white;
            padding: 35px;
            border-radius: 24px;
            box-shadow: 0 10px 30px rgba(216, 27, 96, 0.12);
            text-align: center;
            border: 1px solid #FFC0CB;
            max-width: 450px;
            margin: auto;
            margin-top: 5vh;
        }
        .login-title {
            color: #D81B60;
            font-size: 34px;
            font-weight: 800;
        }
        .login-slogan {
            color: #AD1457;
            font-size: 14px;
            font-style: italic;
            margin-bottom: 20px;
        }
    </style>
    <div class="login-card">
        <div class="login-title">🌸 PHUCgpt</div>
        <div class="login-slogan">"Đồng hành thông minh, vun tròn vẹn Phúc"</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔗 Chọn ứng dụng liên kết")
        auth_choice = st.selectbox(
            "Chọn nền tảng:", 
            ["🌐 Google / Gmail", "📘 Facebook", "🍏 Apple / iCloud"]
        )

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

# --- GIAO DIỆN CHÍNH ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background: linear-gradient(135deg, #FFF0F5 0%, #FFE4E1 100%); }
    .header-container { text-align: center; padding: 10px 0px; }
    .brand-title { font-size: 36px; font-weight: 800; color: #D81B60; }
    .brand-slogan { color: #AD1457; font-size: 14px; font-style: italic; }
    [data-testid="stChatMessageUser"] { background: linear-gradient(135deg, #FF80AB 0%, #FF4081 100%) !important; color: white !important; border-radius: 20px 20px 4px 20px !important; }
    [data-testid="stChatMessageBot"] { background-color: #FFFFFF !important; color: #2D3748 !important; border: 1px solid rgba(255, 182, 193, 0.5) !important; border-radius: 20px 20px 20px 4px !important; }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.9) !important; border-right: 1px solid rgba(255, 182, 193, 0.4); }
    .stButton>button { background: linear-gradient(135deg, #FF4081 0%, #D81B60 100%) !important; color: white !important; border-radius: 12px !important; border: none !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

ai_engine = AILearningEngine()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"<h3 style='color: #D81B60; text-align: center;'>🌸 Chào, {st.session_state.username}</h3>", unsafe_allow_html=True)
    
    if st.button("🚪 Đăng xuất tài khoản", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.current_session_id = None
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
        if st.button(f"💬 {sess_title}", key=f"sess_{sess_id}", use_container_width=True):
            st.session_state.current_session_id = sess_id
            st.rerun()

    st.markdown("---")
    st.subheader("🎙️ Cấu hình Giọng đọc Voice")
    voice_gender = st.selectbox("Giới tính:", ["Nữ", "Nam"])
    voice_pitch = st.selectbox("Độ cao / Trầm:", ["Cao", "Trung bình", "Trầm ấm"])
    voice_region = st.selectbox("Vùng miền:", ["Miền Bắc 🇻🇳", "Miền Trung 🇻🇳", "Miền Nam 🇻🇳"])
    voice_config = f"{voice_gender} - {voice_pitch} - {voice_region}"

    st.markdown("---")
    st.subheader("🎨 Tính năng Tạo Ảnh AI")
    image_prompt_input = st.text_input("Mô tả bức ảnh bạn muốn tạo:")
    if st.button("🎨 Tạo Ảnh Ngay", use_container_width=True):
        if image_prompt_input:
            with st.spinner("AI đang phác thảo..."):
                img_res = ai_engine.generate_image(image_prompt_input)
                st.success(img_res)
        else:
            st.warning("Vui lòng nhập mô tả ảnh!")

# --- KHUNG CHÍNH ---
st.markdown("""
    <div class="header-container">
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

st.markdown("### 📎 Đính kèm tệp & Ghi âm")
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Tải ảnh hoặc tài liệu:", type=["png", "jpg", "jpeg", "pdf", "txt", "docx"])
with col2:
    st.markdown("**🎙️ Ghi âm giọng nói:**")
    audio_bytes = audio_recorder(text="Bấm để ghi âm", recording_color="#FF4081", neutral_color="#E0E0E0", icon_size="2x")

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")

prompt = st.chat_input("Nhập câu hỏi, tâm sự hoặc yêu cầu của bạn...")

if prompt or uploaded_file or audio_bytes:
    user_msg = prompt if prompt else "[Yêu cầu kèm tệp/ghi âm]"
    
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (st.session_state.current_session_id, "user", user_msg))
    conn.commit()

    with st.chat_message("user"):
        if uploaded_file:
            if "image" in uploaded_file.type:
                st.image(uploaded_file, caption="Ảnh đính kèm", width=300)
            else:
                st.write(f"📁 Tệp: {uploaded_file.name}")
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
        st.markdown(user_msg)

    c.execute("SELECT title FROM sessions WHERE id = ?", (st.session_state.current_session_id,))
    res_title = c.fetchone()
    if res_title and res_title[0] == "Đoạn chat mới":
        new_title = user_msg[:25] + "..." if len(user_msg) > 25 else user_msg
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
