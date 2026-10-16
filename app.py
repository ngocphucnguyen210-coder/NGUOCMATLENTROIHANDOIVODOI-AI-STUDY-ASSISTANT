import streamlit as st
from PIL import Image
import os
import database as db
from ai_engine import AILearningEngine
from voice_engine import text_to_speech
from media_processor import enhance_image

# ---------------------------------------------------------
# 1. CẤU HÌNH TRANG & GIAO DIỆN PHÚCGPT (HỒNG PASTEL)
# ---------------------------------------------------------
st.set_page_config(
    page_title="PHUCgpt - Trợ Lý AI Học Tập",
    page_icon="🌸",
    layout="centered"
)

PASTEL_PINK_CSS = """
<style>
    /* Gradient Nền Tổng Thể */
    .stApp {
        background: linear-gradient(135deg, #FFF5F7 0%, #FCE4EC 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Tinh Gọn */
    [data-testid="stSidebar"] {
        background-color: #F8BBD0 !important;
    }
    
    /* Khung Chat AI (Bubble) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #FFFFFF !important;
        border-radius: 18px;
        border: 1px solid #F48FB1;
        box-shadow: 0px 4px 15px rgba(244, 143, 177, 0.15);
    }
    
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #EC407A !important;
        color: white !important;
        border-radius: 18px;
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
    st.error(f"Lỗi khởi tạo AI Engine: {e}")
    st.stop()

# Session States
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_media_box" not in st.session_state:
    st.session_state.show_media_box = False

LANGUAGES = {
    "Tiếng Việt 🇻🇳": "vi",
    "English 🇺🇸": "en",
    "Français 🇫🇷": "fr",
    "한국어 🇰🇷": "ko",
    "日本語 🇯🇵": "ja"
}

# ---------------------------------------------------------
# 2. SIDEBAR (THANH ĐIỀU HƯỚNG PHÚCGPT)
# ---------------------------------------------------------
with st.sidebar:
    st.title("🌸 PHUCgpt")
    st.caption("Trợ lý học tập AI toàn năng")
    
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

    st.subheader("🌐 Ngôn Ngữ AI")
    selected_lang_name = st.selectbox("Ngôn ngữ trả lời:", list(LANGUAGES.keys()))
    lang_code = LANGUAGES[selected_lang_name]

    st.subheader("🎙 Cài Đặt Giọng Nói")
    voice_gender_region = st.selectbox("Giọng đọc:", ["Nữ - Miền Bắc", "Nam - Miền Nam", "Nữ - Miền Nam (Trầm)"])
    voice_tone = st.select_slider("Tông giọng:", options=["Trầm", "Trung bình", "Cao"], value="Trung bình")
    enable_audio = st.checkbox("Tự động phát Âm thanh", value=False)

    st.divider()
    if st.button("🗑 Xóa Lịch Sử Trò Chuyện"):
        if st.session_state.user_email:
            db.clear_chat_history(st.session_state.user_email)
            st.session_state.messages = []
            st.success("Đã xóa lịch sử!")
            st.rerun()

# ---------------------------------------------------------
# 3. GIAO DIỆN CHÍNH PHÚCGPT (CHAT WINDOW)
# ---------------------------------------------------------
st.title("💬 PHUCgpt - Trò Chuyện & Giải Bài Tập")

# Hiển thị lịch sử trò chuyện
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------
# 4. THANH CÔNG CỤ ĐÍNH KÈM (ẨN/HIỆN KHI BẤM NÚT)
# ---------------------------------------------------------
col_toggle, col_space = st.columns([1, 5])
with col_toggle:
    if st.button("➕ Đính kèm ảnh/Camera"):
        st.session_state.show_media_box = not st.session_state.show_media_box

uploaded_image = None

if st.session_state.show_media_box:
    with st.container():
        st.info("📷 Chọn phương thức tải hình ảnh bài tập:")
        tab_up, tab_cam = st.tabs(["📁 Tải ảnh từ thiết bị", "📷 Chụp qua Camera"])
        
        with tab_up:
            file_upload = st.file_uploader("Chọn ảnh bài tập:", type=["jpg", "png", "jpeg"])
            if file_upload:
                raw_img = Image.open(file_upload)
                uploaded_image = enhance_image(raw_img)
                st.image(uploaded_image, caption="Đã đính kèm ảnh bài tập", width=200)
                
        with tab_cam:
            camera_photo = st.camera_input("Chụp ảnh trực tiếp")
            if camera_photo:
                raw_img = Image.open(camera_photo)
                uploaded_image = enhance_image(raw_img)
                st.image(uploaded_image, caption="Ảnh từ Camera", width=200)

# ---------------------------------------------------------
# 5. KHUNG NHẬP TIN NHẮN (CHAT INPUT DƯỚI ĐÁY)
# ---------------------------------------------------------
user_prompt = st.chat_input("Hỏi PHUCgpt bất cứ điều gì (Toán, Lý, Văn, Anh...)...")

if user_prompt:
    if not st.session_state.user_email:
        st.warning("Vui lòng nhập Gmail ở thanh bên trái để lưu lịch sử cuộc trò chuyện!")
    
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    if st.session_state.user_email:
        db.save_message(st.session_state.user_email, "user", user_prompt)

    # AI Phản hồi
    with st.chat_message("assistant"):
        with st.spinner("✨ PHUCgpt đang tư duy..."):
            response_text = ai_engine.generate_response(
                prompt=user_prompt,
                image=uploaded_image,
                lang=selected_lang_name,
                enable_search=True
            )
            st.markdown(response_text)

            # Đọc âm thanh nếu bật
            if enable_audio:
                audio_file = text_to_speech(
                    text=response_text[:300],
                    lang=lang_code,
                    voice_option=voice_gender_region,
                    tone_option=voice_tone
                )
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")

    # Lưu phản hồi AI
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    if st.session_state.user_email:
        db.save_message(st.session_state.user_email, "assistant", response_text)
        
    # Reset lại trạng thái đính kèm ảnh sau khi gửi xong
    st.session_state.show_media_box = False
