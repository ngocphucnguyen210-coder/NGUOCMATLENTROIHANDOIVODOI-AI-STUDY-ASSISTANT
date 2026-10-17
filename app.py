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
    page_title="PHUCgpt - Chăm chỉ mỗi ngày, kiến tạo tương lai",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# LOGO CHÍNH THỨC CỦA PHÚC (CHÚ GẤU LEO NÚI TRI THỨC)
OFFICIAL_LOGO_URL = "https://raw.githubusercontent.com/nguocmatlentroihandoivodoi-ai-study-assistant/main/logo.png"

# 2. Khởi tạo Database SQLite
def init_db():
    conn = sqlite3.connect('phucgpt_app_v7.db', check_same_thread=False)
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
        "slogan": "PHUCgpt - Chăm chỉ mỗi ngày, kiến tạo tương lai",
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
        "slogan": "PHUCgpt - Study hard every day, shape the future",
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
                c.execute("SELECT id FROM
