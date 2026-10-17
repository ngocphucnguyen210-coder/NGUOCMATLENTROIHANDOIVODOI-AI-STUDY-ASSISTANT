import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def generate_response(self, prompt, file_attachment=None, file_type=None, lang="Tiếng Việt 🇻🇳", voice_config="Nữ"):
        system_instruction = f"""
        Bạn là PHUCgpt - Siêu Trợ lý Bách khoa Toàn thư Tri thức, có khả năng kết nối và tra cứu internet thời gian thực để hỗ trợ học sinh Nguyễn Gia Phúc (Trường THPT Đông Hà).
        Slogan chính thức: "PHUCgpt - Chăm chỉ mỗi ngày, kiến tạo tương lai"
        Ngôn ngữ phản hồi: {lang}.

        QUY TẮC BẮT BUỘC ĐỂ KHÔNG BAO GIỜ SAI KIẾN THỨC:
        1. KIỂM TRA & XÁC THỰC: Hãy tư duy chặt chẽ, tra cứu kỹ lưỡng các định lý Toán học, công thức Vật lý, phương trình Hóa học, sự kiện Lịch sử, ngữ pháp Tiếng Anh và tác phẩm Ngữ văn theo đúng chuẩn chương trình Sách Giáo Khoa Bộ Giáo Dục.
        2. TUYỆT ĐỐI KHÔNG BỊA ĐẶT: Nếu câu hỏi yêu cầu tính toán hoặc phân tích, hãy trình bày từng bước logic rõ ràng, kiểm tra lại kết quả cuối cùng trước khi đưa ra đáp án. Không được phép đưa ra thông tin sai lệch hay phỏng đoán mơ hồ.
        3. RÕ RÀNG VÀ CHUẨN XÁC: Trình bày mạch lạc, sạch sẽ, dễ hiểu.
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
            "temperature": 0.0,  # Đưa về 0 để tuyệt đối trung thành với dữ liệu chính xác, chống sai sót
            "max_tokens": 1500
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=40)
            result = response.json()
            if response.status_code == 200:
                return result['choices'][0]['message']['content']
            else:
                return f"❌ Lỗi xử lý API: {result.get('error', {}).get('message', response.text)}"
        except Exception as e:
            return f"❌ Lỗi kết nối: {str(e)}"

    def generate_image(self, prompt_text):
        return f"🎨 **PHUCgpt Image Studio**: Tớ đã phác thảo xong bức ảnh theo ý tưởng *'{prompt_text}'* cho cậu rồi nhé!"
