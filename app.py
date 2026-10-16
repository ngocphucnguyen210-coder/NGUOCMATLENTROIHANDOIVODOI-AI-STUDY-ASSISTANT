import streamlit as st
from PIL import Image
from ai_engine import AILearningEngine

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="PHUCgpt - Trợ Lý Học Tập & Tri Thức",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Tối ưu CSS Giao diện Hồng Pastel & Font chữ sắc nét
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Nền chính hồng pastel dịu mắt */
    .stApp {
        background-color: #FFF5F7;
    }

    /* Header thanh thoát */
    .main-header {
        text-align: center;
        padding: 10px 0px 20px 0px;
    }
    .main-title {
        color: #D81B60;
        font-size: 38px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 5px;
    }
    .main-slogan {
        color: #AD1457;
        font-size: 16px;
        font-weight: 500;
        font-style: italic;
    }

    /* Tin nhắn Chat người dùng (Hồng) */
    [data-testid="stChatMessageUser"] {
        background-color: #F8BBD0 !important;
        color: #4A148C !important;
        border-radius: 18px 18px 2px 18px !important;
        padding: 12px 16px !important;
        font-weight: 500;
    }

    /* Tin nhắn Chat AI (Trắng nổi bật) */
    [data-testid="stChatMessageBot"] {
        background-color: #FFFFFF !important;
        color: #212121 !important;
        border: 1px solid #F48FB1 !important;
        border-radius: 18px 18px 18px 2px !important;
        padding: 12px 16px !important;
        box-shadow: 0px 2px 6px rgba(216, 27, 96, 0.05);
    }

    /* Tùy chỉnh thanh Sidebar bên trái */
    [data-testid="stSidebar"] {
        background-color: #FCE4EC !important;
        border-right: 1px solid #F8BBD0;
    }

    /* Nút bấm thiết kế viền bo tròn dễ thương */
    .stButton>button {
        background-color: #EC407A !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #D81B60 !important;
        transform: translateY(-1px);
    }

    /* Input Chat bên dưới */
    .stChatInputContainer {
        border-radius: 20px !important;
        border: 2px solid #F48FB1 !important;
        background-color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Khởi tạo AI Engine
@st.cache_resource
def load_engine():
    return AILearningEngine()

try:
    ai_engine = load_engine()
except Exception as e:
    st.error(f"❌ Không thể khởi tạo AI Engine. Chi tiết: {str(e)}")
    st.stop()

# 4. Thanh Sidebar điều hướng & Tùy chọn học tập
with st.sidebar:
    st.markdown("<h2 style='color: #C2185B; text-align: center;'>🌸 PHUCgpt</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #880E4F; font-size: 13px;'>Đồng hành thông minh, vun tròn vẹn Phúc</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("🎯 Lĩnh vực hỗ trợ:")
    mode = st.radio(
        "Chọn chế độ ưu tiên:",
        ["📐 Giải bài tập (Toán, Lý, Hóa, Sinh)", 
         "📖 Văn học & Khoa học xã hội", 
         "🇬🇧 IELTS,HSK,DELF,.. & Ngoại ngữ toàn năng", 
         "💡 Hỏi đáp Bách khoa Tri thức"],
        index=3
    )

    st.markdown("---")
    st.subheader("📷 Đính kèm ảnh bài tập:")
    uploaded_image = st.file_uploader("Tải ảnh bài tập/đề thi (PNG, JPG):", type=["png", "jpg", "jpeg"])
    
    if uploaded_image:
        st.image(uploaded_image, caption="Xem trước ảnh bài tập", use_container_width=True)

    if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 5. Khung giao diện chính
st.markdown("""
    <div class="main-header">
        <div class="main-title">PHUCgpt</div>
        <div class="main-slogan">"Đồng hành thông minh, vun tròn vẹn Phúc"</div>
    </div>
""", unsafe_allow_html=True)

# 6. Quản lý lịch sử trò chuyện
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "bot", "content": "Xin chào! Mình là **PHUCgpt** - Trợ lý học tập và bách khoa tri thức của bạn. Bạn cần hỗ trợ bài tập hay kiến thức gì hôm nay?"}
    ]

# Hiển thị các tin nhắn cũ
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            if "image" in msg and msg["image"]:
                st.image(msg["image"], caption="Ảnh bạn tải lên", width=300)
            st.markdown(msg["content"])
    else:
        with st.chat_message("bot"):
            st.markdown(msg["content"])

# 7. Nhận dữ liệu nhập từ người dùng
prompt = st.chat_input("Hỏi PHUCgpt bất kỳ bài tập, tác phẩm hay kiến thức nào...")

if prompt:
    # Lưu và hiển thị câu hỏi người dùng
    user_data = {"role": "user", "content": prompt}
    if uploaded_image:
        user_data["image"] = uploaded_image

    st.session_state.messages.append(user_data)
    with st.chat_message("user"):
        if uploaded_image:
            st.image(uploaded_image, caption="Ảnh bạn tải lên", width=300)
        st.markdown(prompt)

    # Gọi AI trả lời
    with st.chat_message("bot"):
        with st.spinner("PHUCgpt đang phân tích và tìm lời giải tối ưu nhất..."):
            # Ghép thông tin chế độ đã chọn vào prompt
            full_prompt = f"[{mode}] {prompt}"
            
            # Gọi hàm xử lý từ ai_engine
            response = ai_engine.generate_response(
                prompt=full_prompt, 
                image=uploaded_image
            )
            
            st.markdown(response)
            st.session_state.messages.append({"role": "bot", "content": response})
