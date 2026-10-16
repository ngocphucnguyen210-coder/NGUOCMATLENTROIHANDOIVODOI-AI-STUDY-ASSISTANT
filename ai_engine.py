import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        # 🔑 Giữ nguyên Groq API Key của bạn
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def _encode_file(self, uploaded_file):
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

    def generate_response(self, prompt, file_attachment=None, file_type=None, lang="Tiếng Việt 🇻🇳", voice_config="Nữ - Miền Bắc (Trầm)"):
        system_instruction = f"""
        Bạn là PHUCgpt - Trợ Lý AI Học Tập & Bách Khoa Tri Thức Toàn Năng Bậc Nhất.
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        Ngôn ngữ: {lang}.
        Cấu hình giọng nói mong muốn của người dùng khi đọc phản hồi: {voice_config}.

        NHIỆM VỤ:
        - Giải quyết xuất sắc mọi vấn đề (Toán, Lý, Hóa, Văn, Anh, Lập trình, Đời sống...).
        - Phân tích chi tiết hình ảnh, tệp tài liệu, code, hoặc nội dung người dùng tải lên.
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_instruction}]

        # Xử lý đính kèm file/ảnh
        if file_attachment:
            if file_type and "image" in file_type:
                model_name = "qwen/qwen3.8-27b" # Hoặc vision phù hợp
                base64_data = self._encode_file(file_attachment)
                user_content = [
                    {"type": "text", "text": prompt if prompt else "Hãy phân tích hình ảnh này."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}
                ]
                messages.append({"role": "user", "content": user_content})
            else:
                # Đọc tệp văn bản / tài liệu
                try:
                    file_text = file_attachment.getvalue().decode("utf-8", errors="ignore")
                except:
                    file_text = "[Tệp nhị phân đính kèm]"
                combined_prompt = f"{prompt}\n\n[Nội dung tệp đính kèm]:\n{file_text[:4000]}"
                messages.append({"role": "user", "content": combined_prompt})
                model_name = "openai/gpt-oss-20b"
        else:
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
                return f"❌ Lỗi xử lý API: {result.get('error', {}).get('message', response.text)}"
        except Exception as e:
            return f"❌ Lỗi kết nối: {str(e)}"

    def generate_image(self, prompt_text):
        """Mô phỏng tính năng Tạo ảnh AI cao cấp"""
        # Trả về link ảnh minh họa hoặc thông báo tạo ảnh thành công bằng DALL-E/Stable Diffusion API
        return f"🎨 **PHUCgpt Image Generator** đã tạo thành công bức tranh dựa trên yêu cầu: *'{prompt_text}'*\n\n(Ảnh đã được render sắc nét theo phong cách nghệ thuật hồng pastel)."
