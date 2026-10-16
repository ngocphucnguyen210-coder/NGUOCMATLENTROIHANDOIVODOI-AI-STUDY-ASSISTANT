import sqlite3
import streamlit as st
from PIL import Image
from ai_engine import AILearningEngine

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="PHUCgpt - Đồng Hành Thông Minh",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. CSS Tùy chỉnh giao diện Sang trọng, Hiện đại & Hồng Pastel cao cấp
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Nền ứng dụng hồng pastel dịu mắt, cao cấp */
    .stApp {
        background: linear-gradient(135deg, #FFF0F5 0%, #FFE4E1 100%);
    }

    /* Tiêu đề Header sang trọng */
    .header-container {
        text-align: center;
        padding: 20px 0px 10px 0px;
    }
    .brand-title {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(90deg, #D81B60, #FF69B4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        margin-bottom: 0px;
    }
    .brand-slogan {
        color: #AD1457;
        font-size: 15px;
        font-weight: 500;
        font-style: italic;
        margin-top: 5px;
    }

    /* Khung chat người dùng (Hiện đại, bo góc mềm mại) */
    [data-testid="stChatMessageUser"] {
        background: linear-gradient(135deg, #FF80AB 0%, #FF4081 100%) !important;
        color: white !important;
        border-radius: 20px 20px 4px 20px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 15px rgba(255, 64, 129, 0.2);
    }

    /* Khung chat AI (Trắng tinh tế, có viền hồng mờ) */
    [data-testid="stChatMessageBot"] {
        background-color: #FFFFFF !important;
        color: #2D3748 !important;
        border: 1px solid rgba(255, 182, 193, 0.5) !important;
        border-radius: 20px 20px 20px 4px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    }

    /* Sidebar sang trọng */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 182, 193, 0.4);
    }

    /* Nút bấm hiện đại, hiệu ứng mượt */
    .stButton>button {
        background: linear-gradient(135deg, #FF4081 0%, #D81B60 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 10px 20px;
        box-shadow: 0 4px 12px rgba(216, 27, 96, 0.25);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(216, 27, 96, 0.35);
    }

    /* Ô nhập chat lơ lửng, cao cấp */
    .stChatInputContainer {
        border-radius: 24px !important;
        border: 2px solid #FFB6C1 !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
        box-shadow: 0 8px 30px rgba(255, 182, 193, 0.2) !important;
        padding: 4px 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Khởi tạo Database SQLite lưu lịch sử
def init_db():
    conn = sqlite3.connect('phucgpt_history.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

def save_message_to_db(role, content):
    c = conn.cursor()
    c.execute("INSERT INTO chats (role, content) VALUES (?, ?)", (role, content))
    conn.commit()

def load_messages_from_db():
    c = conn.cursor()
    c.execute("SELECT role, content FROM chats")
    rows = c.fetchall()
    return [{"role": row[0], "content": row[1]} for row in rows]

def clear_db():
    c = conn.cursor()
    c.execute("DELETE FROM chats")
    conn.commit()

# 4. Khởi tạo AI Engine
ai_engine = AILearningEngine()

# 5. Thanh Sidebar điều hướng hiện đại
with st.sidebar:
    st.markdown("<h2 style='color: #D81B60; text-align: center; font-weight: 800;'>🌸 PHUCgpt</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #AD1457; font-size: 13px; font-weight: 500;'>Đồng hành thông minh, vun tròn vẹn Phúc</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("🎯 Chọn chủ đề học tập:")
    mode = st.radio(
        "Lĩnh vực chuyên sâu:",
        ["📐 Giải bài tập tự nhiên", "📖 Văn học & Xã hội", "🇬🇧 IELTS & Ngoại ngữ", "💡 Tri thức bách khoa"],
        index=3
    )

    st.markdown("---")
    st.subheader("📷 Đính kèm ảnh bài tập:")
    uploaded_image = st.file_uploader("Tải ảnh (PNG, JPG):", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        st.image(uploaded_image, caption="Xem trước ảnh", use_container_width=True)

    st.markdown("---")
    if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
        clear_db()
        st.rerun()

# 6. Giao diện Header chính
st.markdown("""
    <div class="header-container">
        <div class="brand-title">PHUCgpt</div>
        <div class="brand-slogan">"Đồng hành thông minh, vun tròn vẹn Phúc"</div>
    </div>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# 7. Tải và hiển thị lịch sử trò chuyện
messages = load_messages_from_db()
if not messages:
    messages = [{"role": "bot", "content": "Xin chào! Mình là **PHUCgpt** - Trợ lý thông minh của bạn. Hôm nay bạn muốn chinh phục kiến thức hoặc bài tập gì nào?"}]

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 8. Xử lý tin nhắn nhập vào từ người dùng
prompt = st.chat_input("Nhập câu hỏi hoặc yêu cầu bài tập của bạn...")

if prompt:
    save_message_to_db("user", prompt)
    with st.chat_message("user"):
        if uploaded_image:
            st.image(uploaded_image, caption="Ảnh đính kèm", width=280)
        st.markdown(prompt)

    with st.chat_message("bot"):
        with st.spinner("PHUCgpt đang phân tích và tổng hợp tri thức..."):
            full_prompt = f"[{mode}] {prompt}"
            response = ai_engine.generate_response(prompt=full_prompt, image=uploaded_image)
            st.markdown(response)
            save_message_to_db("bot", response)
