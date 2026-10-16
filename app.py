import sqlite3
import streamlit as st
from PIL import Image
from ai_engine import AILearningEngine

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="PHUCgpt - Đồng Hành Thông Minh",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Khởi tạo Database SQLite để lưu lịch sử chat vĩnh viễn
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

# 3. CSS Giao diện Hồng Pastel sắc nét
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background-color: #FFF5F7;
    }
    .main-header {
        text-align: center;
        padding: 5px 0px 15px 0px;
    }
    .main-title {
        color: #D81B60;
        font-size: 36px;
        font-weight: 700;
    }
    .main-slogan {
        color: #AD1457;
        font-size: 15px;
        font-weight: 500;
        font-style: italic;
    }
    [data-testid="stChatMessageUser"] {
        background-color: #F8BBD0 !important;
        color: #4A148C !important;
        border-radius: 18px 18px 2px 18px !important;
    }
    [data-testid="stChatMessageBot"] {
        background-color: #FFFFFF !important;
        color: #212121 !important;
        border: 1px solid #F48FB1 !important;
        border-radius: 18px 18px 18px 2px !important;
    }
    [data-testid="stSidebar"] {
        background-color: #FCE4EC !important;
        border-right: 1px solid #F8BBD0;
    }
    .stButton>button {
        background-color: #EC407A !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover {
        background-color: #D81B60 !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. Khởi tạo AI Engine
@st.cache_resource
def load_engine():
    return AILearningEngine()

ai_engine = load_engine()

# 5. Thanh Sidebar Điều Hướng & Tính Năng Mở rộng
with st.sidebar:
    st.markdown("<h2 style='color: #C2185B; text-align: center;'>🌸 PHUCgpt</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #880E4F; font-size: 13px;'>Đồng hành thông minh, vun tròn vẹn Phúc</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("🎯 Chọn chủ đề học tập:")
    mode = st.radio(
        "Lĩnh vực:",
        ["📐 Giải bài tập tự nhiên", "📖 Văn học & Xã hội", "🇬🇧 IELTS & Ngoại ngữ", "💡 Tri thức bách khoa"],
        index=3
    )

    st.markdown("---")
    st.subheader("📷 Đính kèm ảnh bài tập:")
    uploaded_image = st.file_uploader("Tải ảnh (PNG, JPG):", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        st.image(uploaded_image, caption="Xem trước ảnh", use_container_width=True)

    st.markdown("---")
    if st.button("🗑️ Xóa toàn bộ lịch sử (DB)", use_container_width=True):
        clear_db()
        st.rerun()

# 6. Giao diện chính
st.markdown("""
    <div class="main-header">
        <div class="main-title">PHUCgpt</div>
        <div class="main-slogan">"Đồng hành thông minh, vun tròn vẹn Phúc"</div>
    </div>
""", unsafe_allow_html=True)

# 7. Tải lịch sử chat từ Database
messages = load_messages_from_db()
if not messages:
    messages = [{"role": "bot", "content": "Xin chào! Mình là **PHUCgpt**. Bạn cần giải bài tập hay tra cứu kiến thức gì hôm nay?"}]

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 8. Xử lý tin nhắn người dùng
prompt = st.chat_input("Hỏi PHUCgpt bất kỳ câu hỏi hoặc bài tập nào...")

if prompt:
    # Lưu tin nhắn user vào DB
    save_message_to_db("user", prompt)
    with st.chat_message("user"):
        if uploaded_image:
            st.image(uploaded_image, caption="Ảnh đính kèm", width=300)
        st.markdown(prompt)

    # Gọi AI trả lời và lưu vào DB
    with st.chat_message("bot"):
        with st.spinner("PHUCgpt đang phân tích..."):
            full_prompt = f"[{mode}] {prompt}"
            response = ai_engine.generate_response(prompt=full_prompt, image=uploaded_image)
            st.markdown(response)
            save_message_to_db("bot", response)
