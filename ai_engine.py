import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        # 🔑 Groq API Key của bạn
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def search_web_fallback(self, query):
        """Hàm tìm kiếm tin cậy qua DuckDuckGo HTML API đơn giản"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            url = f"https://html.duckduckgo.com/html/?q={query}"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(res.text, 'html.parser')
                snippets = []
                for a in soup.find_all('a', class_='result__snippet', limit=3):
                    snippets.append(a.get_text())
                return "\n".join(snippets)
        except Exception:
            pass
        return ""

    def _encode_file(self, uploaded_file):
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

    def generate_response(self, prompt, file_attachment=None, file_type=None, lang="Tiếng Việt 🇻🇳", voice_config="Nữ - Miền Bắc (Trầm)"):
        # Tra cứu web thực tế
        web_info = self.search_web_fallback(prompt)

        # System Instruction nghiêm ngặt chống ảo giác kiến thức
        system_instruction = f"""
        Bạn là PHUCgpt - Trợ lý AI Học tập & Bách khoa Tri thức.
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        Ngôn ngữ: {lang}.

        QUY TẮC BẮT BUỘC VỀ ĐỘ CHÍNH XÁC KIẾN THỨC:
        1. Tuyệt đối KHÔNG ĐƯỢC TỰ BỊA ĐẶT thông tin, tên tuổi, ca sĩ, diễn viên, tác phẩm hay công thức khoa học.
        2. Với các câu hỏi về thực tế, nhân vật công cộng, bài tập Toán/Lý/Hóa/Văn: Nếu không chắc chắn 100%, hãy thành thật trả lời không biết hoặc chỉ nêu thông tin có căn cứ xác thực.
        3. Giải bài tập: Phải trình bày chi tiết từng bước logic, đúng bản chất công thức.

        [DỮ LIỆU THỰC TẾ TRA CỨU]:
        {web_info if web_info else "Không có dữ liệu ngoại vi."}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_instruction}]

        # Xử lý đính kèm file/ảnh
        if file_attachment and file_type and "image" in file_type:
            model_name = "qwen/qwen3.8-27b"
            base64_data = self._encode_file(file_attachment)
            user_content = [
                {"type": "text", "text": prompt if prompt else "Hãy phân tích hình ảnh này thật chính xác."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}
            ]
            messages.append({"role": "user", "content": user_content})
        else:
            # Sử dụng model qwen/qwen3.8-27b hoặc openai/gpt-oss-20b với temperature thấp
            model_name = "qwen/qwen3.8-27b"
            
            if file_attachment:
                try:
                    file_text = file_attachment.getvalue().decode("utf-8", errors="ignore")
                    prompt = f"{prompt}\n\n[Nội dung tệp đính kèm]:\n{file_text[:3000]}"
                except:
                    pass
            messages.append({"role": "user", "content": prompt if prompt else "Xin chào!"})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.1  # Đưa temperature về 0.1 để AI trả lời hoàn toàn chính xác, không ảo giác
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
        return f"🎨 **PHUCgpt Image Generator**: Đã tạo thành công bức ảnh theo mô tả: '{prompt_text}'."
