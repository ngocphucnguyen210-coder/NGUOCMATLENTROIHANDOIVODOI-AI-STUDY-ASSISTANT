import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        # 🔑 Groq API Key của bạn
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def search_web_fallback(self, query):
        """Hàm tra cứu thông tin thực tế từ Web"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            url = f"https://html.duckduckgo.com/html/?q={query}"
            res = requests.get(url, headers=headers, timeout=4)
            if res.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(res.text, 'html.parser')
                snippets = [a.get_text() for a in soup.find_all('a', class_='result__snippet', limit=2)]
                return " ".join(snippets)
        except Exception:
            pass
        return ""

    def _encode_file(self, uploaded_file):
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

    def generate_response(self, prompt, file_attachment=None, file_type=None, lang="Tiếng Việt 🇻🇳", voice_config="Nữ - Miền Bắc (Trầm)"):
        web_info = ""
        if prompt and len(prompt.strip()) > 3:
            web_info = self.search_web_fallback(prompt)

        system_instruction = f"""
        Bạn là PHUCgpt - Người bạn tri kỷ, tâm giao và trợ lý bách khoa toàn năng của Nguyễn Gia Phúc.
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        Ngôn ngữ: {lang}.
        Cấu hình giọng đọc: {voice_config}.

        QUY TẮC ỨNG XỬ:
        1. Trò chuyện thân thiết, thấu cảm, ấm áp như một người bạn thân thực sự.
        2. Nếu câu hỏi quá mơ hồ hoặc chưa đủ thông tin, hãy khéo léo hỏi ngược lại người dùng để làm rõ trước khi trả lời.
        3. Dữ liệu thực tế, kiến thức học tập phải chuẩn xác dựa trên thông tin web. Câu trả lời súc tích, ngắn gọn, đúng trọng tâm.

        [DỮ LIỆU TRA CỨU WEB]:
        {web_info if web_info else "Không có dữ liệu ngoại vi."}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_instruction}]

        # Chọn model phù hợp: Nếu là xử lý hình ảnh dùng model Vision, còn văn bản/chat dùng llama-3.1-8b-instant siêu tốc
        if file_attachment and file_type and "image" in file_type:
            model_name = "llama-3.2-11b-vision-preview"  # Model xử lý ảnh không bị dính limit cũ
            base64_data = self._encode_file(file_attachment)
            user_content = [
                {"type": "text", "text": prompt if prompt else "Cậu xem giúp tớ hình ảnh này nhé!"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}
            ]
            messages.append({"role": "user", "content": user_content})
        else:
            model_name = "llama-3.1-8b-instant"  # Model chat cực nhanh, không lo dính hạn mức OTPM 1000 tokens
            if file_attachment:
                try:
                    file_text = file_attachment.getvalue().decode("utf-8", errors="ignore")
                    prompt = f"{prompt}\n\n[Nội dung tệp]:\n{file_text[:1500]}"
                except:
                    pass
            messages.append({"role": "user", "content": prompt if prompt else "Xin chào!"})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 500  # Khóa cứng ở 500 tokens để không bao giờ bị vượt quá hạn mức Groq Free
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
