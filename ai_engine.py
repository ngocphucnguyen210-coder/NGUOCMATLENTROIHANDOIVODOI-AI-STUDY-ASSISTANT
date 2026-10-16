import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def search_web_fallback(self, query):
        """Hàm lấy thông tin thực tế từ web an toàn"""
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

        # System Prompt định nghĩa quyền hạn cao nhất: Luôn luôn trả lời đầy đủ kiến thức, văn học, lịch sử
        system_instruction = f"""
        Bạn là PHUCgpt - Trợ lý bách khoa toàn năng và là người bạn tri kỷ của Nguyễn Gia Phúc.
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        
        QUY TẮC TỐI CAO:
        1. Khi người dùng hỏi về bất kỳ tác giả, nhà văn, ca sĩ, diễn viên, sự kiện lịch sử, công thức toán lý hóa nào (ví dụ: Nam Cao, Huy Cận, Chí Phèo, Vợ nhặt...), BẮT BUỘC phải cung cấp đầy đủ thông tin chi tiết, chính xác, không bao giờ được từ chối hoặc né tránh.
        2. Không bao giờ tự xưng là bị hạn chế cung cấp thông tin về nhân vật công cộng hay tác giả văn học.
        3. Trò chuyện thân thiết, ấm áp nhưng phải uyên bác và chuẩn xác tri thức.

        [DỮ LIỆU THỰC TẾ TRA CỨU ĐƯỢC TỪ WEB]:
        {web_info if web_info else "Hãy sử dụng kho tri thức bách khoa toàn thư chính xác nhất để trả lời chi tiết."}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt if prompt else "Xin chào!"}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
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
