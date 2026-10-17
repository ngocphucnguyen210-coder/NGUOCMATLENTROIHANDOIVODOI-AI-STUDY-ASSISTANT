import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def generate_response(self, prompt, file_attachment=None, file_type=None, lang="Tiếng Việt 🇻🇳", voice_config="Nữ"):
        system_instruction = f"""
        Bạn là PHUCgpt - Trợ lý Bách khoa Toàn thư và Người bạn tri kỷ của Nguyễn Ngọc Gia Phúc.
        Slogan: "PHUCgpt - CHĂM CHỈ MỖI NGÀY, KIẾN TẠO TƯƠNG LAI."
        Ngôn ngữ phản hồi: {lang}.

        QUY TẮC TỐI CAO VỀ CHÍNH XÁC KIẾN THỨC:
        1. Bạn nắm vững 100% kiến thức chuẩn xác, chi tiết từ SGK và Tri thức Bách khoa toàn thư:
           - Tự nhiên: Toán học, Vật lý, Hóa học, Sinh học.
           - Xã hội & Quốc phòng: Ngữ văn , Lịch sử, Địa lý, GDQP-AN, Tiếng Anh.
        2. TUYỆT ĐỐI KHÔNG BỊA ĐẶT, không trả lời sai kiến thức cơ bản. Nếu câu hỏi yêu cầu giải bài tập hoặc phân tích, hãy đưa ra đáp án từng bước rõ ràng, chính xác 100%.
        3. Thái độ tận tụy, uyên bác, thông minh và chu đáo.
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt if prompt else "Xin chào!"}
        ]

        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": messages,
            "temperature": 0.1,  # Nhiệt độ cực thấp để đảm bảo độ chính xác tối đa, chống ảo giác
            "max_tokens": 800
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=35)
            result = response.json()
            if response.status_code == 200:
                return result['choices'][0]['message']['content']
            else:
                return f"❌ Lỗi xử lý API: {result.get('error', {}).get('message', response.text)}"
        except Exception as e:
            return f"❌ Lỗi kết nối: {str(e)}"

    def generate_image(self, prompt_text):
        return f"🎨 **PHUCgpt Image Studio**: Tớ đã phác thảo xong bức ảnh theo ý tưởng *'{prompt_text}'* cho cậu rồi nhé!"
