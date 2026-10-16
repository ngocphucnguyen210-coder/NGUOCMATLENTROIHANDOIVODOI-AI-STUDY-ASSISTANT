import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class AILearningEngine:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Chưa cấu hình GEMINI_API_KEY trong file .env")
        self.client = genai.Client(api_key=api_key)

    def generate_response(self, prompt, image=None, video_bytes=None, lang="Tiếng Việt", enable_search=True):
        system_instruction = f"""
        Bạn là Trợ lý Học tập AI Thông minh & Toàn năng bậc nhất. 
        Ngôn ngữ phản hồi chính: {lang}.
        
        Nhiệm vụ chính:
        1. GIẢI BÀI TẬP (Toán, Lý, Hóa, Văn, Anh, Sinh, Sử, Địa...):
           - Tóm tắt đề bài.
           - Phương pháp & Công thức áp dụng.
           - Lời giải từng bước chi tiết, dễ hiểu, chuẩn xác 100%.
           - Đáp số / Kết luận.
        2. TRI THỨC CUỘC SỐNG & TƯ DUY TỰ DO: Trả lời khoa học, mạch lạc, dễ tiếp thu.
        3. NHẬN DIỆN MẢNH/VIDEO: Nhận diện hình ảnh bài tập, giải bài hoặc phân tích video.
        """

        contents = []
        if image:
            contents.append(image)
        if prompt:
            contents.append(prompt)

        # Cấu hình Google Search Grounding
        tools = []
        if enable_search:
            tools.append(types.Tool(google_search=types.GoogleSearch()))

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3, # Thấp để giải toán chính xác hơn
            tools=tools if tools else None
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", # Hoặc gemini-2.5-pro
                contents=contents,
                config=config
            )
            return response.text
        except Exception as e:
            return f"❌ Lỗi khi kết nối với AI Engine: {str(e)}"
