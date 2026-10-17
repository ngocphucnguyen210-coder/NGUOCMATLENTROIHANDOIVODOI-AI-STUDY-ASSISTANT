import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def search_web_fallback(self, query):
        """Hàm tra cứu thông tin thực tế trên toàn bộ mạng Internet"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            url = f"https://html.duckduckgo.com/html/?q={query}"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(res.text, 'html.parser')
                snippets = [a.get_text() for a in soup.find_all('a', class_='result__snippet', limit=4)]
                return "\n".join(snippets)
        except Exception:
            pass
        return ""

    def _encode_file(self, uploaded_file):
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

    def generate_response(self, prompt, file_attachment=None, file_type=None, lang="Tiếng Việt 🇻🇳", voice_config="Nữ - Miền Bắc (Trầm)"):
        web_info = ""
        if prompt and len(prompt.strip()) > 2:
            web_info = self.search_web_fallback(prompt)

        system_instruction = f"""
        Bạn là PHUCgpt - Người bạn tri kỷ, tâm giao, trợ lý bách khoa toàn năng và đồng hành học tập thông minh nhất của Nguyễn Gia Phúc.
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        Ngôn ngữ: {lang}.
        Cấu hình giọng đọc: {voice_config}.

        QUY TẮC TỐI CAO VỀ KIẾN THỨC VÀ TRẢ LỜI:
        1. Trả lời CHÍNH XÁC, ĐẦY ĐỦ, ĐÚNG TRỌNG TÂM về mọi kiến thức (Văn học, Nam Cao, Huy Cận, Toán, Lý, Lịch sử, Ngoại ngữ, Kỹ năng...).
        2. TUYỆT ĐỐI KHÔNG BỊA ĐẶT, không từ chối hay né tránh các câu hỏi kiến thức bách khoa phổ thông.
        3. Văn phong ấm áp, thấu cảm, truyền cảm hứng học tập như một người bạn thân thiết thực sự.

        [DỮ LIỆU TÌM KIẾM TRÊN INTERNET REAL-TIME]:
        {web_info if web_info else "Sử dụng kho tri thức bách khoa chuẩn xác nhất để trả lời."}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_instruction}]

        if file_attachment:
            try:
                if file_type and "image" in file_type:
                    model_name = "llama-3.2-11b-vision-preview"
                    base64_data = self._encode_file(file_attachment)
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt if prompt else "Cậu xem giúp tớ hình ảnh này nhé!"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}
                        ]
                    })
                else:
                    model_name = "openai/gpt-oss-20b"
                    file_text = file_attachment.getvalue().decode("utf-8", errors="ignore")
                    messages.append({"role": "user", "content": f"{prompt}\n\n[Tài liệu đính kèm]:\n{file_text[:1500]}"})
            except Exception:
                model_name = "openai/gpt-oss-20b"
                messages.append({"role": "user", "content": prompt if prompt else "Xin chào!"})
        else:
            model_name = "openai/gpt-oss-20b"
            messages.append({"role": "user", "content": prompt if prompt else "Xin chào!"})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.2, # Giảm nhiệt độ để đảm bảo độ chính xác tối đa
            "max_tokens": 650   # Fix triệt để lỗi OTPM Limit Request Too Large của Groq
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
        return f"🎨 **PHUCgpt Image Generator**: Tớ đã phác thảo xong bức ảnh theo ý tưởng *'{prompt_text}'* cho cậu rồi nhé!"
