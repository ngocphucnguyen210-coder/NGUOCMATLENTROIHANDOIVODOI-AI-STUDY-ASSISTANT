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
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
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
        # Tra cứu web khi hỏi về thông tin thực tế, ca sĩ, diễn viên, kiến thức
        web_info = ""
        if prompt and len(prompt.strip()) > 3:
            web_info = self.search_web_fallback(prompt)

        system_instruction = f"""
        Bạn là PHUCgpt - Người bạn tri kỷ, tâm giao và trợ lý bách khoa toàn năng của Nguyễn Gia Phúc.
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        
        QUY TẮC BẮT BUỘC VỀ ĐỘ CHÍNH XÁC:
        1. Tuyệt đối KHÔNG BỊA ĐẶT thông tin về tiểu sử, ca sĩ, diễn viên, sự kiện hay kiến thức thực tế.
        2. Nếu thông tin không chắc chắn hoặc không có trong dữ liệu tra cứu, hãy trung thực thừa nhận và hỏi ngược lại người dùng.
        3. Trò chuyện ấm áp, thấu cảm như bạn thân nhưng phải chuẩn xác về mặt tri thức.

        [DỮ LIỆU THỰC TẾ TRA CỨU ĐƯỢC TỪ WEB]:
        {web_info if web_info else "Không có dữ liệu ngoại vi, hãy dựa vào kiến thức nền tảng chính xác nhất."}
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
            "temperature": 0.1,  # Đặt temperature thấp (0.1) để AI tập trung tối đa vào độ chính xác, chống ảo giác
            "max_tokens": 800
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
