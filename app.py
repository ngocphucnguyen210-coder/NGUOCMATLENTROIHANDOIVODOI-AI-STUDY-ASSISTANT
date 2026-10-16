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

# 2. Khởi tạo Database SQLite nâng cao (Quản lý User, Phiên Chat, Tin nhắn)
def init_db():
    conn = sqlite3.connect('phucgpt_database.db', check_same_thread=False)
    c = conn.cursor()
    # Bảng phiên chat
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            title TEXT
        )
    ''')
    # Bảng tin nhắn
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

# 3. Quản lý trạng thái Đăng nhập & Phiên chat
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

# --- MÀN HÌNH ĐĂNG NHẬP NÂNG CAO ---
if not st.session_state.logged_in:
    st.markdown("""
    <style>
        .login-card {
            background: white;
            padding: 40px;
            border-radius: 24px;
            box-shadow: 0 10px 30px rgba(216, 27, 96, 0.1);
            text-align: center;
            max-width: 450px;
            margin: auto;
            margin-top: 5vh;
            border: 1px solid #FFC0CB;
        }
        .login-title {
            color: #D81B60;
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 5px;
        }
        .login-slogan {
            color: #AD1457;
            font-size: 14px;
            font-style: italic;
            margin-bottom: 25px;
        }
    </style>
    <div class="login-card">
        <div class="login-title">🌸 PHUCgpt</div>
        <div class="login-slogan">"Đồng hành thông minh, vun tròn vẹn Phúc"</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        login_method = st.selectbox("Chọn hình thức đăng nhập:", ["📧 Đăng nhập bằng Gmail", "📘 Đăng nhập bằng Facebook", "🍏 Đăng nhập bằng iCloud", "👤 Đăng nhập khách (Guest)"])
        user_input = st.text_input("Nhập email hoặc tên tài khoản của bạn:")
        
        if st.button("🚀 Xác nhận Đăng nhập", use_container_width=True):
            if user_input.strip() == "":
                user_input = "NguyenGiaPhuc_User"
            st.session_state.logged_in = True
            st.session_state.username = user_input
            
            # Tạo sẵn phiên chat đầu tiên nếu chưa có
            c = conn.cursor()
            c.execute("INSERT INTO sessions (username, title) VALUES (?, ?)", (user_input, "Đoạn chat mới"))
            conn.commit()
            st.session_state.current_session_id = c.lastrowid
            st.rerun()
    st.stop()

# --- GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP ---
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

# --- THANH SIDEBAR QUẢN LÝ NÂNG CAO ---
with st.sidebar:
    st.markdown(f"<h3 style='color: #D81B60; text-align: center;'>🌸 Xin chào, {st.session_state.username}</h3>", unsafe_allow_html=True)
    
    # Nút Đăng xuất
    if st.button("🚪 Đăng xuất tài khoản", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.current_session_id = None
        st.rerun()

    st.markdown("---")
    
    # Nút Tạo đoạn chat mới
    if st.button("✨ Tạo đoạn chat mới", use_container_width=True):
        c = conn.cursor()
        c.execute("INSERT INTO sessions (username, title) VALUES (?, ?)", (st.session_state.username, "Đoạn chat mới"))
        conn.commit()
        st.session_state.current_session_id = c.lastrowid
        st.rerun()

    # Ô Tìm kiếm cuộc chat
    search_query = st.text_input("🔍 Tìm kiếm cuộc chat cũ...", placeholder="Nhập từ khóa...")

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
    st.subheader("🎙️ Tùy chỉnh Giọng nói Voice")
    voice_gender = st.selectbox("Chọn giới tính giọng đọc:", ["Nữ", "Nam"])
    voice_pitch = st.selectbox("Độ cao / Trầm giọng:", ["Cao", "Trung bình", "Trầm ấm"])
    voice_region = st.selectbox("Vùng miền:", ["Miền Bắc 🇻🇳", "Miền Trung 🇻🇳", "Miền Nam 🇻🇳"])
    voice_config = f"{voice_gender} - {voice_pitch} - {voice_region}"

    st.markdown("---")
    st.subheader("🎨 Tính năng Tạo Ảnh AI")
    image_prompt_input = st.text_input("Mô tả bức ảnh bạn muốn vẽ:")
    if st.button("🎨 Tạo Ảnh Ngay", use_container_width=True):
        if image_prompt_input:
            with st.spinner("AI đang phác thảo và vẽ bức ảnh theo yêu cầu..."):
                img_result = ai_engine.generate_image(image_prompt_input)
                st.success(img_result)
        else:
            st.warning("Vui lòng nhập mô tả bức ảnh bạn muốn tạo!")

# --- KHUNG GIAO DIỆN CHÍNH ---
st.markdown("""
    <div class="header-container">
        <div class="brand-title">PHUCgpt</div>
        <div class="brand-slogan">"Đồng hành thông minh, vun tròn vẹn Phúc"</div>
    </div>
""", unsafe_allow_html=True)

# Hiển thị lịch sử tin nhắn của phiên hiện tại
if st.session_state.current_session_id:
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE session_id = ?", (st.session_state.current_session_id,))
    messages = c.fetchall()
    
    for role, content in messages:
        with st.chat_message(role):
            st.markdown(content)

# --- KHU VỰC NHẬP DỮ LIỆU ĐA PHƯƠNG TIỆN (Ảnh, Tệp, Voice, Quay video, Văn bản) ---
st.markdown("### 📎 Đính kèm tệp đa phương tiện & Thu âm")
col_upload1, col_upload2 = st.columns(2)
with col_upload1:
    uploaded_file = st.file_uploader("Gửi ảnh hoặc Tệp tài liệu:", type=["png", "jpg", "jpeg", "pdf", "txt", "docx"])
with col_upload2:
    st.markdown("**🎙️ Ghi âm giọng nói (Voice):**")
    audio_bytes = audio_recorder(text="Bấm để ghi âm", recording_color="#FF4081", neutral_color="#E0E0E0", icon_size="2x")

# Xử lý khi có giọng nói ghi âm gửi lên
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    st.info("Đã ghi âm giọng nói thành công! Bạn có thể bấm gửi kèm yêu cầu.")

# Khung chat input chính
prompt = st.chat_input("Hỏi PHUCgpt bất kỳ câu hỏi, bài tập hoặc yêu cầu nào...")

if prompt or uploaded_file or audio_bytes:
    # Xác định nội dung gửi
    user_msg = prompt if prompt else "[Yêu cầu kèm tệp/giọng nói đa phương tiện]"
    
    # Lưu vào database tin nhắn
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (st.session_state.current_session_id, "user", user_msg))
    conn.commit()

    with st.chat_message("user"):
        if uploaded_file:
            if "image" in uploaded_file.type:
                st.image(uploaded_file, caption="Ảnh đính kèm", width=300)
            else:
                st.write(f"📁 Tệp đính kèm: {uploaded_file.name}")
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
        st.markdown(user_msg)

    # Đổi tên tiêu đề đoạn chat theo câu hỏi đầu tiên nếu đang là "Đoạn chat mới"
    c.execute("SELECT title FROM sessions WHERE id = ?", (st.session_state.current_session_id,))
    current_title = c.fetchone()[0]
    if current_title == "Đoạn chat mới":
        new_title = user_msg[:25] + "..." if len(user_msg) > 25 else user_msg
        c.execute("UPDATE sessions SET title = ? WHERE id = ?", (new_title, st.session_state.current_session_id))
        conn.commit()

    # Gọi AI trả lời
    with st.chat_message("bot"):
        with st.spinner("PHUCgpt đang phân tích và xử lý đa phương tiện..."):
            response = ai_engine.generate_response(
                prompt=user_msg, 
                file_attachment=uploaded_file, 
                file_type=uploaded_file.type if uploaded_file else None,
                voice_config=voice_config
            )
            st.markdown(response)
            
            # Lưu phản hồi vào DB
            c.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (st.session_state.current_session_id, "bot", response))
            conn.commit()
