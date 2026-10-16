import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        # 🔑 Thay mã Groq API Key (gsk_...) của bạn vào đây
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

        if not self.api_key or self.api_key.startswith("gsk_DÁN"):
            raise ValueError("Vui lòng điền mã Groq API Key (gsk_...) hợp lệ!")

    def _encode_image(self, image_file):
        return base64.b64encode(image_file.getvalue()).decode('utf-8')

    def generate_response(self, prompt, image=None, lang="Tiếng Việt 🇻🇳"):
        system_instruction = f"""
        Bạn là PHUCgpt - Trợ Lý AI Học Tập & Bách Khoa Tri Thức Toàn Năng Bậc Nhất.
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        Ngôn ngữ phản hồi chính: {lang}.

        QUY TẮC PHẢN HỒI:
        - Giải bài tập tự nhiên (Toán, Lý, Hóa, Sinh...): Tóm tắt giả thiết, công thức, lời giải chi tiết từng bước chuẩn xác 100%.
        - Văn học & Khoa học xã hội: Phân tích sâu sắc, lập luận chặt chẽ, văn phong trau chuốt.
        - Luyện thi IELTS,HSK & Ngoại ngữ: Chấm điểm, sửa lỗi ngữ pháp, nâng cấp từ vựng Band 7.0+, dịch thuật chuyên nghiệp.
        - Tư duy & Tri thức bách khoa: Giải đáp mọi thắc mắc ngắn gọn, logic, dễ hiểu.
        - Hình ảnh: Đọc và giải quyết triệt để các bài toán/sơ đồ trong ảnh chụp.
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_instruction}]

        if image:
            model_name = "llama-3.2-11b-vision-preview"
            base64_image = self._encode_image(image)
            user_content = [
                {"type": "text", "text": prompt if prompt else "Hãy giải bài tập/phân tích hình ảnh này giúp tôi."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
            messages.append({"role": "user", "content": user_content})
        else:
            model_name = "llama-3.1-70b-versatile"
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
