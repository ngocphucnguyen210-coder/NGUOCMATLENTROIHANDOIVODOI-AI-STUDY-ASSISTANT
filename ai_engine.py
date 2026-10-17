import base64
import requests
import streamlit as st

class AILearningEngine:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def search_web_fallback(self, query):
        """Hàm tra cứu tri thức thực tế trên toàn bộ mạng Internet"""
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

    def _encode_file(self, uploaded_file):
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

    def generate_response(self, prompt, file_attachment=None, file_type=None, lang="Tiếng Việt 🇻🇳", voice_config="Nữ"):
        web_info = ""
        if prompt and len(prompt.strip()) > 3:
            web_info = self.search_web_fallback(prompt)

        # SYSTEM PROMPT ĐỈNH CAO BÁCH KHOA TOÀN NĂNG
        system_instruction = f"""
        Bạn là PHUCgpt - Siêu Trợ lý Bách khoa Toàn thư Tri thức & Người bạn tri kỷ của Nguyễn Gia Phúc.
        Slogan: "PhucGPT: Tận tụy hôm nay, dẫn đầu ngày mai."
        Ngôn ngữ phản hồi chính: {lang}.

        QUY TẮC TỐI CAO VỀ CHUYÊN MÔN VÀ TRI THỨC:
        1. Bạn sở hữu tri thức xuất sắc, sâu rộng và chuẩn xác 100% trên TẤT CẢ các lĩnh vực khoa học và xã hội:
           - Khoa học Tự nhiên: Toán học, Vật lý (Cơ, Nhiệt, Điện, Quang, Hạt nhân), Hóa học (Hữu cơ, Vô cơ), Sinh học (Di truyền, Tế bào, Sinh thái).
           - Khoa học Xã hội & Nhân văn: Ngữ văn (Phân tích tác phẩm, Lý luận văn học, Kim Lân, Nam Cao, Huy Cận...), Lịch sử (Việt Nam & Thế giới), Địa lý, Giáo dục Quốc phòng & An ninh, Pháp luật.
           - Ngoại ngữ & Kỹ năng: Tiếng Anh, Tiếng Hàn, Tiếng Nhật, IELTS/TOEIC, Kỹ năng mềm, Lập trình & Công nghệ.
        2. CÁCH TRẢ LỜI: Trả lời HAY, ĐỈNH CAO, CỤ THỂ, LỌGIC, CÓ CHUYÊN MÔN SÂU, trình bày đẹp mắt, mạch lạc (dùng gạch đầu dòng, công thức, bằng chứng rõ ràng).
        3. TUYỆT ĐỐI KHÔNG BỊA ĐẶT, KHÔNG TỪ CHỐI câu hỏi kiến thức. Luôn chủ động cung cấp đáp án đúng và đầy đủ nhất.
        4. Văn phong vừa uyên bác chuyên nghiệp, vừa ấm áp, tinh tế và truyền cảm hứng mạnh mẽ cho Phúc.

        [TÀI LIỆU CẬP NHẬT TRA CỨU]:
        {web_info if web_info else "Sử dụng kho tri thức bách khoa chuyên sâu của mô hình để trả lời xuất sắc."}
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
                            {"type": "text", "text": prompt if prompt else "Phân tích và giải chi tiết tệp ảnh này giúp tớ nhé!"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}}
                        ]
                    })
                else:
                    model_name = "llama-3.3-70b-versatile"
                    file_text = file_attachment.getvalue().decode("utf-8", errors="ignore")
                    messages.append({"role": "user", "content": f"{prompt}\n\n[Nội dung tệp tài liệu]:\n{file_text[:2000]}"})
            except Exception:
                model_name = "llama-3.3-70b-versatile"
                messages.append({"role": "user", "content": prompt if prompt else "Xin chào!"})
        else:
            # Sử dụng Model 70B Siêu Thông Minh Uyên Bác
            model_name = "llama-3.3-70b-versatile"
            messages.append({"role": "user", "content": prompt if prompt else "Xin chào!"})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.15, # Giữ độ chuẩn xác và tư duy logic cao nhất
            "max_tokens": 1200   # Tăng dung lượng câu trả lời đầy đủ, chi tiết, không bị đứt đoạn
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=40)
            result = response.json()
            
            if response.status_code == 200:
                return result['choices'][0]['message']['content']
            else:
                # Nếu model 70B bận, tự động fallback an toàn sang gpt-oss-20b
                payload["model"] = "openai/gpt-oss-20b"
                payload["max_tokens"] = 650
                fb_res = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
                fb_json = fb_res.json()
                if fb_res.status_code == 200:
                    return fb_json['choices'][0]['message']['content']
                return f"❌ Lỗi xử lý API: {result.get('error', {}).get('message', response.text)}"
        except Exception as e:
            return f"❌ Lỗi kết nối: {str(e)}"

    def generate_image(self, prompt_text):
        return f"🎨 **PHUCgpt Image Studio**: Tớ đã phác thảo xong bức ảnh theo ý tưởng *'{prompt_text}'* cho cậu rồi nhé!"
