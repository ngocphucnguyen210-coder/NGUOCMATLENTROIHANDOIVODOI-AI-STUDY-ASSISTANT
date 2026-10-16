import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        # 🔑 Giữ nguyên mã Groq API Key của bạn
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def _encode_image(self, image_file):
        return base64.b64encode(image_file.getvalue()).decode('utf-8')

    def generate_response(self, prompt, image=None, lang="Tiếng Việt 🇻🇳"):
        system_instruction = f"""
        Bạn là PHUCgpt - Trợ Lý AI Học Tập & Bách Khoa Tri Thức Toàn Năng Bậc Nhất.
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        Ngôn ngữ phản hồi chính: {lang}.
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_instruction}]

        if image:
            # Model Vision đa năng Qwen 3.8 27B mới nhất từ Groq
            model_name = "qwen/qwen3.8-27b"
            base64_image = self._encode_image(image)
            user_content = [
                {"type": "text", "text": prompt if prompt else "Hãy giải bài tập hoặc phân tích hình ảnh này."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
            messages.append({"role": "user", "content": user_content})
        else:
            # Model GPT-OSS 20B siêu tốc độ và chính xác
            model_name = "openai/gpt-oss-20b"
            messages.append({"role": "user", "content": prompt if prompt else "Xin chào!"})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.3
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=45)
            result = response.json()
            
            if response.status_code == 200:
                return result['choices'][0]['message']['content']
            else:
                error_msg = result.get('error', {}).get('message', response.text)
                return f"❌ Lỗi xử lý API: {error_msg}"
                
        except Exception as e:
            return f"❌ Lỗi kết nối API: {str(e)}"
