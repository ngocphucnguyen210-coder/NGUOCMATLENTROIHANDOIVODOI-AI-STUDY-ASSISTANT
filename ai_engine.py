import os
import streamlit as st
from google import genai
from google.genai import types

class AILearningEngine:
    def __init__(self):
        # Dán mã AQ... của bạn vào đây
        api_key = "AQ.Ab8RN6L5vSHLO3tYkUSn6QQz5pohjq2aKlUeFdBkuQAaW8s6lA"
            
        if not api_key:
            raise ValueError("Vui lòng điền mã xác thực!")
            
        # Khởi tạo client, hệ thống sẽ tự nhận diện token OAuth/AQ
        self.client = genai.Client(api_key=api_key)

    def generate_response(self, prompt, image=None, video_bytes=None, lang="Tiếng Việt 🇻🇳", enable_search=True):
        system_instruction = f"""
        Bạn là PHUCgpt - Trợ Lý AI Học Tập & Ngôn Ngữ Toàn Năng Bậc Nhất.
        Ngôn ngữ phản hồi chính: {lang}.

        BẠN CHUYÊN XỬ LÝ CHUYÊN SÂU MỌI TÁC VỤ HỌC TẬP VÀ NGOẠI NGỮ:
        1. GIẢI BÀI TẬP TỰ NHIÊN (Toán học, Vật lý, Hóa học, Sinh học, Tin học...): Lời giải chi tiết từng bước, chính xác.
        2. VĂN HỌC & KHOA HỌC XÃ HỘI (Ngữ văn, Lịch sử, Địa lý...): Phân tích sâu sắc, lập dàn ý, viết bài mẫu.
        3. LUYỆN THI IELTS & NGOẠI NGỮ: Chấm bài, sửa lỗi ngữ pháp, từ vựng Band 7.0+, dịch thuật chuyên nghiệp.
        """

        contents = []
        if image:
            contents.append(image)
        if prompt:
            contents.append(prompt)

        tools = []
        if enable_search:
            tools.append(types.Tool(google_search=types.GoogleSearch()))

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3,
            tools=tools if tools else None
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=config
            )
            return response.text
        except Exception as e:
            return f"❌ Lỗi xử lý từ AI (Token AQ): {str(e)}"
