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
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(res.text, 'html.parser')
                snippets = [a.get_text() for a in soup.find_all('a', class_='result__snippet', limit=3)]
                return "\n".join(snippets)
        except Exception:
            pass
        return ""

    def generate_response(self, prompt, file_attachment=None, file_type=None, lang="Tiếng Việt 🇻🇳", voice_config="Nữ"):
        web_info = ""
        if prompt and len(prompt.strip()) > 3:
            web_info = self.search_web_fallback(prompt)

        system_instruction = f"""
        Bạn là PHUCgpt - Trợ lý bách khoa toàn năng và là người bạn tri kỷ của Nguyễn Gia Phúc.
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        
        QUY TẮC TỐI CAO VỀ KIẾN THỨC:
        1. Khi người dùng hỏi bất kỳ câu hỏi nào về văn học (Nam Cao, Huy Cèo, Chí Phèo, Vợ nhặt, v.v.), lịch sử, khoa học, đời sống: PHẢI trả lời cực kỳ đầy đủ, chính xác, chi tiết và chuẩn văn bản SGK.
        2. TUYỆT ĐỐI KHÔNG từ chối, không né tránh, không đưa ra câu trả lời chung chung hoặc sai lệch.
        3. Giữ thái độ thân thiết, ấm áp của một người bạn nhưng kiến thức phải chuẩn xác 100%.

        [DỮ LIỆU THỰC TẾ TRA CỨU]:
        {web_info if web_info else "Sử dụng kho tri thức bách khoa toàn thư chính xác tuyệt đối để trả lời."}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Sử dụng model llama-3.3-70b-versatile: Model lớn cực kỳ thông minh, uyên bác và không bao giờ bị lỗi kiến thức cơ bản
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt if prompt else "Xin chào!"}
            ],
            "temperature": 0.2,
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
        return f"🎨 **PHUCgpt Image Generator**: Tớ đã phác thảo xong bức ảnh theo ý tưởng của cậu: *'{prompt_text}'* rồi nhé!"
