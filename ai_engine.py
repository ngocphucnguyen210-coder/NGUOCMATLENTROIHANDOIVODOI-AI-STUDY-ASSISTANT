import os
import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        # API Key Groq của bạn
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def _encode_image(self, image_file):
        """Chuyển đổi hình ảnh sang chuỗi Base64 để gửi qua API"""
        return base64.b64encode(image_file.getvalue()).decode('utf-8')

    def generate_response(self, prompt, image=None, video_bytes=None, lang="Tiếng Việt 🇻🇳", enable_search=True):
        system_instruction = f"""
        Bạn là PHUCgpt - Trợ Lý AI Học Tập & Ngôn Ngữ Toàn Năng Bậc Nhất.
        Ngôn ngữ phản hồi chính: {lang}.

        BẠN CHUYÊN XỬ LÝ CHUYÊN SÂU MỌI TÁC VỤ HỌC TẬP VÀ NGOẠI NGỮ:

        1. GIẢI BÀI TẬP TỰ NHIÊN (Toán học, Vật lý, Hóa học, Sinh học, Tin học...):
           - Tóm tắt giả thiết, dữ kiện (từ văn bản hoặc ảnh chụp đề bài).
           - Liệt kê công thức, phương pháp tư duy & Lời giải chi tiết từng bước (Step-by-step) chính xác 100%.
           - Đưa ra đáp số cuối cùng rõ ràng.

        2. VĂN HỌC & KHOA HỌC XÃ HỘI (Ngữ văn, Lịch sử, Địa lý, GDCD...):
           - Phân tích tác phẩm văn học sâu sắc, văn phong trau chuốt, giàu tính luận điểm.
           - Lập dàn ý chi tiết, viết đoạn văn/bài văn mẫu.

        3. LUYỆN THI IELTS & NGOẠI NGỮ (Anh, Trung, Nhật, Hàn...):
           - IELTS Speaking & Writing: Chấm điểm, sửa lỗi ngữ pháp, nâng cấp từ vựng Band 7.0+ - 8.0+, gợi ý ý tưởng (Idea generation).
           - Dịch thuật chuyên nghiệp mượt mà, đúng ngữ cảnh giữa mọi ngôn ngữ trên thế giới.

        4. TƯ DUY & KIẾN THỨC TỔNG HỢP:
           - Trả lời ngắn gọn, chuẩn xác, logic cao đối với mọi thắc mắc học thuật và cuộc sống.
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Tạo danh sách tin nhắn gửi cho AI
        messages = [{"role": "system", "content": system_instruction}]

        # Chọn Model: Nếu có ảnh thì dùng llama-3.2-11b-vision (đọc ảnh), nếu chỉ có chữ thì dùng llama-3.3-70b (siêu thông minh)
        if image:
            model_name = "llama-3.2-11b-vision-preview"
            base64_image = self._encode_image(image)
            
            user_content = [
                {"type": "text", "text": prompt if prompt else "Hãy giải chi tiết bài tập/phân tích hình ảnh này giúp tôi."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
            messages.append({"role": "user", "content": user_content})
        else:
            model_name = "llama-3.3-70b-versatile"
            messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.3
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=40)
            result = response.json()
            
            if response.status_code == 200:
                return result['choices'][0]['message']['content']
            else:
                error_msg = result.get('error', {}).get('message', response.text)
                return f"❌ Lỗi xử lý API: {error_msg}"
                
        except Exception as e:
            return f"❌ Lỗi kết nối: {str(e)}"
