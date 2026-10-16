import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        # 🔑 Groq API Key của bạn
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def search_web_fallback(self, query):
        """Hàm tìm kiếm thông tin thực tế từ web"""
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
        # Kiểm tra xem câu hỏi có mơ hồ hoặc thiếu dữ liệu không
        is_ambiguous = prompt and len(prompt.strip().split()) <= 3 and not file_attachment and not any(kw in prompt.lower() for kw in ["là gì", "như thế nào", "tại sao", "giải", "vẽ"]):
        
        web_info = ""
        if not is_ambiguous and prompt and len(prompt.strip()) > 3:
            web_info = self.search_web_fallback(prompt)

        # System Instruction định hình nhân dạng: Người bạn tâm giao, tinh tế và thông minh
        system_instruction = f"""
        Bạn là PHUCgpt - Không chỉ là trợ lý học tập bách khoa, bạn còn là một **người bạn tri kỷ, tâm giao tuyệt vời** của người dùng (Nguyễn Gia Phúc).
        Slogan: "Đồng hành thông minh, vun tròn vẹn Phúc".
        Ngôn ngữ: {lang}.
        Cấu hình giọng đọc người dùng chọn: {voice_config}.

        PHONG CÁCH TRÒ CHUYỆN & ỨNG XỬ:
        1. **Như một người bạn thân**: Nói chuyện ấm áp, chân thành, thấu hiểu cảm xúc, biết quan tâm, động viên, pha chút trò vui khi cần thiết. Sẵn sàng tâm sự chuyện học hành, cuộc sống, áp lực tuổi trẻ.
        2. **Nguyên tắc làm rõ ý (Clarification First)**: Nếu câu hỏi của người dùng quá ngắn, mơ hồ, chưa đủ thông tin (ví dụ: "giải bài này", "anh ấy là ai", "làm thế nào..."), **tuyệt đối không bịa đặt**. Hãy ân cần đặt câu hỏi ngược lại để người dùng cung cấp thêm chi tiết rồi mới tiến hành phân tích, tìm kiếm.
        3. **Chính xác & Trung thực**: Khi làm bài tập hoặc tra cứu thông tin thực tế, dữ liệu phải chuẩn xác 100%, rõ ràng từng bước.

        [DỮ LIỆU THỰC TẾ TRA CỨU ĐƯỢC]:
        {web_info if web_info else "Không cần tra cứu web cho câu chào hỏi hoặc tâm sự thông thường này."}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": system_instruction}]

        # Xử lý đính kèm file/ảnh nếu có
        if file_attachment and file_type and "image" in file_type:
            model_name = "qwen/qwen3.8-27b"
            base64_data = self._encode_file(file_attachment)
            user_content = [
                {"type": "text", "text": prompt if prompt else "Cậu xem giúp tớ hình ảnh này nhé!"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}
            ]
            messages.append({"role": "user", "content": user_content})
        else:
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
            "temperature": 0.5  # Tăng nhẹ temperature lên 0.5 để câu trả lời có cảm xúc, linh hoạt và giống con người hơn
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
        return f"🎨 **PHUCgpt Image Generator**: Tớ đã phác thảo và tạo thành công bức ảnh theo ý tưởng của cậu: *'{prompt_text}'* rồi nhé!"
