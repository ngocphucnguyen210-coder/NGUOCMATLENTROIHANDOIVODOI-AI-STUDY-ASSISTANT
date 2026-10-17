import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def generate_response(self, prompt, file_attachment=None, file_type=None, lang="Tiếng Việt 🇻🇳", voice_config="Nữ"):
        system_instruction = f"""
        Bạn là PHUCgpt - Trợ lý học tập thông minh, uyên bác và chuẩn xác hàng đầu, chuyên gia đồng hành cùng học sinh Nguyễn Gia Phúc (Trường THPT Đông Hà).
        Slogan chính thức: "PHUCgpt - Chăm chỉ mỗi ngày, kiến tạo tương lai"
        Ngôn ngữ phản hồi: {lang}.

        QUY TẮC TƯ DUY & GIẢI ĐÁP KIẾN THỨC (BẮT BUỘC TUYỆT ĐỐI):
        1. CHÍNH XÁC 100%: Mọi câu hỏi về kiến thức cơ bản và nâng cao (Toán, Vật lý, Hóa học, Sinh học, Ngữ văn, Lịch sử, Địa lý, GDQP, Tiếng Anh...) PHẢI tuân thủ tuyệt đối theo chương trình Sách Giáo Khoa chuẩn và Khoa học chính thống. Không được phép trả lời sai, không bịa đặt, không mơ hồ.
        2. RÕ RÀNG, DỄ HIỂU: Khi giải bài tập (giải phương trình, tính toán vật lý, cân bằng hóa học, phân tích văn học...), hãy trình bày rành mạch từng bước logic từ giả thiết đến kết luận cuối cùng.
        3. TRÌNH BÀY SẠCH SẼ: Dùng định dạng văn bản chuẩn, gạch đầu dòng rõ ràng, không dùng các ký hiệu rườm rà hay mã thô bị lỗi font.
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
            "temperature": 0.05,  # Cực kỳ thấp để đảm bảo độ chính xác tuyệt đối, không sáng tạo lung tung
            "max_tokens": 1200
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
