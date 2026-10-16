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
        """Mã hóa file ảnh sang chuỗi Base64 để gửi qua API"""
        return base64.b64encode(image_file.getvalue()).decode('utf-8')

    def generate_response(self, prompt, image=None, lang="Tiếng Việt 🇻🇳", enable_search=False):
        # SYSTEM INSTRUCTION TOÀN NĂNG: Đảm bảo giải đáp mọi vấn đề & mọi lĩnh vực kiến thức
        system_instruction = f"""
        Bạn là PHUCgpt - Trợ Lý AI Học Tập & Bách Khoa Tri Thức Toàn Năng Bậc Nhất.
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        Ngôn ngữ phản hồi chính: {lang}.

        QUY TẮC PHẢN HỒI VÀ TƯ DUY TOÀN NĂNG:
        Bạn là một chuyên gia bách khoa đa lĩnh vực. BẤT KỲ CÂU HỎI, VẤN ĐỀ HAY KIẾN THỨC NÀO người dùng đưa ra, bạn đều có khả năng phân tích sâu sắc, chính xác, logic và dễ hiểu.

        1. ĐỐI VỚI BÀI TẬP KHOA HỌC TỰ NHIÊN (Toán, Vật lý, Hóa học, Sinh học, Tin học, Lập trình...):
           - Tóm tắt giả thiết, dữ kiện và bài toán.
           - Đưa ra phương pháp tư duy, công thức áp dụng.
           - Lời giải chi tiết từng bước (Step-by-step), trình bày rõ ràng, đáp số chuẩn xác 100%.

        2. ĐỐI VỚI VĂN HỌC, KHXH & NGHỆ THUẬT (Ngữ văn, Lịch sử, Địa lý, Triết học, Tâm lý...):
           - Phân tích đa chiều, sâu sắc, lập luận chặt chẽ, văn phong trau chuốt và giàu tính biểu cảm.
           - Lập dàn ý chi tiết, viết đoạn văn mẫu, phân tích tác phẩm hoặc sự kiện lịch sử khoa học.

        3. ĐỐI VỚI NGOẠI NGỮ & LUYỆN THI (Anh, Trung, Nhật, Hàn, IELTS, TOEIC...):
           - IELTS Speaking & Writing: Chấm điểm, chỉnh sửa ngữ pháp tỉ mỉ, nâng cấp từ vựng Band 7.0+ - 8.0+, gợi ý ý tưởng (Ideas).
           - Dịch thuật chuyên nghiệp, tự nhiên, chuẩn ngữ cảnh giữa mọi ngôn ngữ trên thế giới.

        4. ĐỐI VỚI CÂU HỎI TRI THỨC MỞ, TƯ DUY & ĐỜI SỐNG (Khoa học, Kỹ năng mềm, Lời khuyên, Đời sống...):
           - Đưa ra câu trả lời toàn diện, khách quan, giàu thông tin và có cấu trúc mạch lạc (sử dụng bullet points, in đậm từ khóa quan trọng).
           - Giải thích các khái niệm phức tạp một cách đơn giản, dễ hiểu nhất.

        5. ĐỐI VỚI HÌNH ẢNH (ẢNH BÀI TẬP / SƠ ĐỒ / TÀI LIỆU):
           - Tự động trích xuất nội dung, văn bản, công thức hoặc hình vẽ từ ảnh.
           - Giải chi tiết bài tập hoặc phân tích đầy đủ nội dung hình ảnh yêu cầu.

        PHONG CÁCH PHẢN HỒI:
        - Thân thiện, tôn trọng, truyền cảm hứng học tập và tràn đầy năng lượng tích cực.
        - Trình bày đẹp mắt bằng Markdown (dùng tiêu đề, danh sách, khối code, công thức LaTeX nếu cần).
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_instruction}]

        # Linh hoạt lựa chọn Model theo tác vụ
        if image:
            # Model thị giác (Vision) hỗ trợ đọc ảnh bài tập / hình vẽ / sơ đồ
            model_name = "llama-3.2-11b-vision-preview"
            base64_image = self._encode_image(image)
            
            user_content = [
                {"type": "text", "text": prompt if prompt else "Hãy phân tích hình ảnh này và giải đáp/trợ giúp chi tiết cho tôi."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
            messages.append({"role": "user", "content": user_content})
        else:
            # Model văn bản siêu trí tuệ Llama 3.3 70B - Xử lý mượt mà mọi lĩnh vực tri thức
            model_name = "llama-3.3-70b-versatile"
            messages.append({"role": "user", "content": prompt if prompt else "Xin chào PHUCgpt!"})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.4  # Cân bằng hoàn hảo giữa tính chính xác và sự sáng tạo
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=45)
            result = response.json()
            
            if response.status_code == 200:
                return result['choices'][0]['message']['content']
            else:
                error_msg = result.get('error', {}).get('message', response.text)
                return f"❌ Lỗi xử lý AI: {error_msg}"
                
        except Exception as e:
            return f"❌ Lỗi kết nối API: {str(e)}"
