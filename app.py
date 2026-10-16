import streamlit as st
from PIL import Image
import os
import database as db
from ai_engine import AILearningEngine
from voice_engine import text_to_speech
from media_processor import enhance_image

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & GIAO DIỆN HỒNG PASTEL (CSS CUSTOM)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Trợ Lý Học Tập AI Pastel",
    page_icon="🌸",
    layout="wide"
)

# Custom CSS cho Tone Hồng Pastel mượt mà
PASTEL_PINK_CSS = """
<style>
    /* Gradient Nền Chính */
    .stApp {
        background: linear-gradient(135deg, #FFF5F7 0%, #FCE4EC 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Hồng Nhạt */
    [data-testid="stSidebar"] {
        background-color: #F8BBD0 !important;
    }
    
    /* Khung Chat AI */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #FFFFFF !important;
        border-radius: 15px;
        border: 1px solid #F48FB1;
        box-shadow: 0px 4px 10px rgba(244, 143, 177, 0.1);
    }
    
    /* Khung Chat User */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #F48FB1 !important;
        color: white !important;
        border-radius: 15px;
    }
    
    /* Nút Bấm Hồng Pastel */
    .stButton>button {
        background-color: #EC407A !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #D81B60 !important;
        transform: scale(1.02);
    }
    
    /* Input Text Bar */
    .stTextInput input {
        border-radius: 20px !important;
        border: 2px solid #F48FB1 !important;
    }
</style>
"""
st.markdown(PASTEL_PINK_CSS, unsafe_allow_html=True)

# Khởi tạo AI Engine
@st.cache_resource
def get_ai_engine():
    return AILearningEngine()

try:
    ai_engine = get_ai_engine()
except Exception as e:
    st.error(f"Hãy cấu hình GEMINI_API_KEY trong file .env! Lỗi: {e}")
    st.stop()

# ---------------------------------------------------------
# 2. SESSION STATE (QUẢN LÝ PHIÊN PHIÊN ĐĂNG NHẬP & CHAT)
# ---------------------------------------------------------
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Dictionary Ngôn ngữ Giao diện
LANGUAGES = {
    "Tiếng Việt 🇻🇳": "vi",
    "English 🇺🇸": "en",
    "Français 🇫🇷": "fr",
    "한국어 🇰🇷": "ko",
    "日本語 🇯🇵": "ja",
    "Deutsch 🇩🇪": "de"
}

# ---------------------------------------------------------
# 3. SIDEBAR (THANH ĐIỀU HƯỚNG VÀ CÀI ĐẶT)
# ---------------------------------------------------------
with st.sidebar:
    st.title("🌸 Trợ Lý AI Học Tập")
    
    # 1. Đăng nhập Gmail
    if not st.session_state.user_email:
        st.subheader("🔑 Đăng Nhập")
        email_input = st.text_input("Nhập Gmail của bạn:")
        if st.button("Đăng Nhập"):
            if "@" in email_input:
                st.session_state.user_email = email_input
                st.session_state.messages = db.get_chat_history(email_input)
                st.rerun()
            else:
                st.warning("Gmail không hợp lệ!")
    else:
        st.success(f"👤 {st.session_state.user_email}")
        if st.button("Đăng Xuất"):
            st.session_state.user_email = None
            st.session_state.messages = []
            st.rerun()
            
    st.divider()

    # 2. Cài đặt Ngôn ngữ Giao diện
    st.subheader("🌐 Ngôn Ngữ AI")
    selected_lang_name = st.selectbox("Chọn ngôn ngữ trả lời:", list(LANGUAGES.keys()))
    lang_code = LANGUAGES[selected_lang_name]

    # 3. Cài đặt Giọng nói Voice Chat
    st.subheader("🎙 Cài Đặt Giọng Nói AI")
    voice_gender_region = st.selectbox(
        "Giọng đọc & Vùng miền:",
        ["Nữ - Miền Bắc", "Nam - Miền Nam", "Nữ - Miền Nam (Trầm)"]
    )
    voice_tone = st.select_slider("Tông giọng (Pitch):", options=["Trầm", "Trung bình", "Cao"], value="Trung bình")
    enable_audio = st.checkbox("Tự động phát Âm thanh (Voice)", value=False)

    st.divider()
    
    # 4. Quản lý Lịch sử trò chuyện
    st.subheader("📜 Quản Lý Lịch Sử")
    if st.button("🗑 Xóa Lịch Sử Trò Chuyện"):
        if st.session_state.user_email:
            db.clear_chat_history(st.session_state.user_email)
            st.session_state.messages = []
            st.success("Đã xóa sạch lịch sử chat!")
            st.rerun()

# ---------------------------------------------------------
# 4. KHU VỰC HIỂN THỊ CHAT TRUNG TÂM
# ---------------------------------------------------------
st.header("✨ AI Study Assistant - Giải Bài Tập & Tư Duy Toàn Cầu")

# Hiển thị lịch sử Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------
# 5. CÔNG CỤ TẢI ẢNH / VIDEO BÀI TẬP
# ---------------------------------------------------------
col_img, col_cam = st.columns(2)
uploaded_image = None

with col_img:
    file_upload = st.file_uploader("📸 Tải ảnh/Video bài tập:", type=["jpg", "png", "jpeg", "mp4"])
    if file_upload and file_upload.type.startswith("image"):
        raw_img = Image.open(file_upload)
        uploaded_image = enhance_image(raw_img) # Làm rõ ảnh qua OpenCV
        st.image(uploaded_image, caption="Ảnh bài tập (Đã xử lý làm rõ chữ)", width=250)

with col_cam:
    camera_photo = st.camera_input("📷 Chụp ảnh từ Webcam bài tập")
    if camera_photo:
        raw_img = Image.open(camera_photo)
        uploaded_image = enhance_image(raw_img)

# ---------------------------------------------------------
# 6. NHẬP CÂU HỎI VÀ XỬ LÝ AI
# ---------------------------------------------------------
user_prompt = st.chat_input("Hỏi AI bài tập, kiến thức cuộc sống hoặc nhập tin nhắn...")

if user_prompt:
    if not st.session_state.user_email:
        st.warning("Vui lòng nhập Gmail ở thanh bên trái để lưu lịch sử cuộc trò chuyện!")
    
    # 1. Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    if st.session_state.user_email:
        db.save_message(st.session_state.user_email, "user", user_prompt)

    # 2. AI phản hồi
    with st.chat_message("assistant"):
        with st.spinner("🧠 AI đang tư duy & giải bài tập..."):
            response_text = ai_engine.generate_response(
                prompt=user_prompt,
                image=uploaded_image,
                lang=selected_lang_name,
                enable_search=True # Tự động kết nối Google
            )
            st.markdown(response_text)

            # Phát âm thanh Voice nếu bật
            if enable_audio:
                audio_file = text_to_speech(
                    text=response_text[:300], # Đọc 300 ký tự đầu để tối ưu tốc độ
                    lang=lang_code,
                    voice_option=voice_gender_region,
                    tone_option=voice_tone
                )
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")

    # 3. Lưu phản hồi AI vào DB
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    if st.session_state.user_email:
        db.save_message(st.session_state.user_email, "assistant", response_text)
