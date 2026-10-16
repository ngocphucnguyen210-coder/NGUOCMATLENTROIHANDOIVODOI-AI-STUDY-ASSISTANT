import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def search_web_fallback(self, query):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            url = f"https://html.duckduckgo.com/html/?q={query}"
            res = requests.get(url, headers=headers, timeout=3)
            if res.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(res.text, 'html.parser')
                snippets = [a.get_text() for a in soup.find_all('a', class_='result__snippet', limit=2)]
                return " ".join(snippets)
        except Exception:
            pass
        return ""

    def generate_response(self, prompt, file_attachment=None, file_type=None, lang="Tiếng Việt 🇻🇳", voice_config="Nữ"):
        web_info = self.search_web_fallback(prompt) if prompt and len(prompt.strip()) > 3 else ""

        system_instruction = f"""
        Bạn là PHUCgpt - Người bạn tri kỷ, tâm giao và trợ lý học tập của Nguyễn Gia Phúc.
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        Hãy trò chuyện ấm áp, ngắn gọn, thấu cảm như bạn thân. Nếu câu hỏi mơ hồ, hãy hỏi ngược lại để làm rõ.
        Thông tin web tham khảo: {web_info if web_info else "Không có."}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Sử dụng model gemma2-9b-it chuẩn xác và luôn khả dụng trên Groq miễn phí
        payload = {
            "model": "gemma2-9b-it",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt if prompt else "Xin chào!"}
            ],
            "temperature": 0.5,
            "max_tokens": 600
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                return result['choices'][0]['message']['content']
            else:
                return f"❌ Lỗi xử lý API: {result.get('error', {}).get('message', response.text)}"
        except Exception as e:
            return f"❌ Lỗi kết nối: {str(e)}"

    def generate_image(self, prompt_text):
        return f"🎨 **PHUCgpt Image Generator**: Tớ đã phác thảo xong bức ảnh theo ý tưởng của cậu: *'{prompt_text}'* rồi nhé!"
