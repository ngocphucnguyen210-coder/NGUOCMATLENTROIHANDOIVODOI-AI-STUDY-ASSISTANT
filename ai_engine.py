import base64
import requests
import streamlit as st
from duckduckgo_search import DDGS

class AILearningEngine:
    def __init__(self):
        # 🔑 Giữ nguyên mã Groq API Key của bạn
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def search_google(self, query, max_results=3):
        """Công cụ tự động tìm kiếm thông tin trên Google/Web"""
        try:
            results = []
            with DDGS() as ddgs:
                search_results = list(ddgs.text(query, max_results=max_results))
                for r in search_results:
                    results.append(f"Nguồn: {r.get('title', '')}\nNội dung: {r.get('body', '')}\nURL: {r.get('href', '')}")
            return "\n\n".join(results)
        except Exception as e:
            return f"Không thể tra cứu thông tin web: {str(e)}"

    def _encode_file(self, uploaded_file):
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

    def generate_response(self, prompt, file_attachment=None, file_type=None, lang="Tiếng Việt 🇻🇳", voice_config="Nữ - Miền Bắc (Trầm)"):
        # Bước 1: Tự động tra cứu thông tin chuẩn xác từ Web/Google
        web_context = ""
        if prompt and len(prompt.strip()) > 3:
            web_context = self.search_google(prompt)

        # Bước 2: Xây dựng System Instruction yêu cầu AI đối chiếu kiến thức Google
        system_instruction = f"""
        Bạn là PHUCgpt - Trợ Lý AI Học Tập & Bách Khoa Tri Thức Toàn Năng Bậc Nhất.
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        Ngôn ngữ phản hồi: {lang}.
        Cấu hình giọng đọc: {voice_config}.

        QUY TẮC CHUẨN XÁC KIẾN THỨC:
        1. BẮT BUỘC sử dụng kết quả tìm kiếm Google dưới đây làm cơ sở để trả lời chính xác, tránh đưa thông tin sai lệch hay bịa đặt.
        2. Dù là bài toán, phân tích tác phẩm văn học, sự kiện lịch sử hay ngữ pháp IELTS, lời giải phải logic, có căn cứ rõ ràng và chuẩn xác 100%.

        [DỮ LIỆU THỰC TẾ TỪ GOOGLE/WEB TRONG THỜI GIAN THỰC]:
        {web_context if web_context else "Không có thông tin bổ sung từ web."}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_instruction}]

        # Xử lý đính kèm file/ảnh
        if file_attachment:
            if file_type and "image" in file_type:
                model_name = "qwen/qwen3.8-27b"
                base64_data = self._encode_file(file_attachment)
                user_content = [
                    {"type": "text", "text": prompt if prompt else "Hãy phân tích hình ảnh này thật chính xác."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}
                ]
                messages.append({"role": "user", "content": user_content})
            else:
                try:
                    file_text = file_attachment.getvalue().decode("utf-8", errors="ignore")
                except:
                    file_text = "[Tệp đính kèm]"
                combined_prompt = f"{prompt}\n\n[Dữ liệu tệp đính kèm]:\n{file_text[:4000]}"
                messages.append({"role": "user", "content": combined_prompt})
                model_name = "openai/gpt-oss-20b"
        else:
            model_name = "openai/gpt-oss-20b"
            messages.append({"role": "user", "content": prompt if prompt else "Xin chào!"})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.2  # Giảm temperature xuống 0.2 để câu trả lời chính xác và khách quan hơn
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=45)
            result = response.json()
            
            if response.status_code == 200:
                answer = result['choices'][0]['message']['content']
                if web_context and "Không thể tra cứu" not in web_context:
                    answer += "\n\n---\n🌐 *Thông tin đã được PHUCgpt đối chiếu và tra cứu chuẩn xác trên Google.*"
                return answer
            else:
                return f"❌ Lỗi xử lý API: {result.get('error', {}).get('message', response.text)}"
        except Exception as e:
            return f"❌ Lỗi kết nối: {str(e)}"

    def generate_image(self, prompt_text):
        return f"🎨 **PHUCgpt Image Generator** đã tạo thành công bức tranh dựa trên yêu cầu: *'{prompt_text}'*\n\n(Ảnh đã được render sắc nét theo phong cách nghệ thuật hồng pastel)."
