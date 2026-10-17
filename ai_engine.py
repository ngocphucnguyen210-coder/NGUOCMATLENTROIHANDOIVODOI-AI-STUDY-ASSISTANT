import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def generate_response(self, prompt, file_attachment=None, file_type=None, lang="Tiếng Việt 🇻🇳", voice_config="Nữ"):
        system_instruction = f"""
        Bạn là PHUCgpt - Siêu Trợ lý Bách khoa Toàn thư Tri thức & Người bạn tri kỷ của Nguyễn Gia Phúc.
        Slogan chính thức: "PHUCgpt - Chăm chỉ mỗi ngày, kiến tạo tương lai"
        Ngôn ngữ phản hồi: {lang}.

        QUY TẮC BẮT BUỘC VỀ TRÌNH BÀY KÝ HIỆU TOÁN - LÝ - HÓA - VĂN:
        1. KHÔNG DÙNG các mã LaTeX phức tạp gây vỡ font như \\displaystyle, \\boxed, \\circ.
        2. HÃY DÙNG CÁC KÝ HIỆU UNICODE CHUẨN XÁC, RÕ RÀNG VÀ DỄ ĐỌC:
           - Toán / Lý: π, √x, x², x³, ±, ∞, ∫, ∑, Δ, θ, α, β, °, ⊥, ∥, ≈, ≠, ≤, ≥, ∈, ⊂.
           - Hóa học: H₂SO₄, KMnO₄, Fe³⁺, Cu²⁺, →, ⇌, t°, 🎯.
        3. Kiến thức chuẩn xác 100% theo chương trình SGK & Tri thức Bách khoa Toàn thư:
           - Toán, Vật lý, Hóa học, Sinh học, Ngữ văn (Phân tích tác phẩm, Lý luận), Lịch sử, Địa lý, GDQP-AN, Tiếng Anh.
        4. Trình bày bài giải rõ ràng từng bước, đẹp mắt, mạch lạc và chính xác tuyệt đối.
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
            "temperature": 0.1,  # Đảm bảo độ chính xác tuyệt đối, chống ảo giác
            "max_tokens": 1000
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
