import os
import streamlit as st
from google import genai
from google.genai import types

class AILearningEngine:
    def __init__(self):
        # Dán đoạn mã AQ... của bạn vào đây, hệ thống sẽ tự nhận diện
        api_key = "AQ.Ab8RN6Ip6cWwOx0rNEbbw--1xSrniZAlSizH6JE1udWwLzHMJg"
            
        if not api_key:
            raise ValueError("Vui lòng điền mã xác thực!")
            
        # Khởi tạo client tương thích
        self.client = genai.Client(api_key=api_key)

    def generate_response(self, prompt, image=None, video_bytes=None, lang="Tiếng Việt", enable_search=True):
        system_instruction = f"""
        Bạn là PHUCgpt - Trợ Lý AI Học Tập Thông Minh & Toàn Năng. 
        Ngôn ngữ phản hồi chính: {lang}.
        
        Nhiệm vụ chính:
        1. GIẢI BÀI TẬP & PHÂN TÍCH TÁC PHẨM:
           - Tóm tắt đề bài / Tác phẩm (Ví dụ: Chí Phèo, Vợ nhặt...).
           - Phương pháp, phân tích chi tiết, sắc sảo, chuẩn văn học/khoa học.
           - Lời giải từng bước rõ ràng, dễ hiểu.
        2. TRI THỨC CUỘC SỐNG: Trả lời khoa học, mạch lạc, dễ tiếp thu.
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
            return f"❌ Lỗi xử lý từ AI: {str(e)}"
