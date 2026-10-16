import edge_tts
import asyncio
import os

# Map cấu hình giọng đọc
VOICE_MAPPING = {
    "vi": {
        "Nữ - Miền Bắc": "vi-VN-HoaiMyNeural",
        "Nam - Miền Nam": "vi-VN-NamMinhNeural",
        "Nữ - Miền Nam (Trầm)": "vi-VN-HoaiMyNeural", # Tùy chỉnh pitch bên dưới
    },
    "en": {"Nữ": "en-US-AriaNeural", "Nam": "en-US-GuyNeural"},
    "fr": {"Nữ": "fr-FR-DeniseNeural", "Nam": "fr-FR-HenriNeural"},
    "ko": {"Nữ": "ko-KR-SunHiNeural", "Nam": "ko-KR-InJoonNeural"},
    "ja": {"Nữ": "ja-JP-NanamiNeural", "Nam": "ja-JP-KeitaNeural"},
    "de": {"Nữ": "de-DE-KatjaNeural", "Nam": "de-DE-KillianNeural"}
}

async def generate_speech_async(text, voice_code, pitch_str, output_path):
    communicate = edge_tts.Communicate(text, voice_code, pitch=pitch_str)
    await communicate.save(output_path)

def text_to_speech(text, lang="vi", voice_option="Nữ - Miền Bắc", tone_option="Trung bình", output_path="output.mp3"):
    voice_code = VOICE_MAPPING.get(lang, {}).get(voice_option, "vi-VN-HoaiMyNeural")
    
    # Cấu hình Tông giọng (Pitch)
    pitch_str = "+0Hz"
    if tone_option == "Cao":
        pitch_str = "+15Hz"
    elif tone_option == "Trầm":
        pitch_str = "-15Hz"

    try:
        asyncio.run(generate_speech_async(text, voice_code, pitch_str, output_path))
        return output_path
    except Exception as e:
        print(f"Lỗi TTS: {e}")
        return None
