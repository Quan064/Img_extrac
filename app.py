from PIL import Image
import gradio as gr
from io import BytesIO
import os
from dotenv import load_dotenv

from google import genai
from google.genai import types

# Tạo client và gửi request
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

PROMPT = r"""Yêu cầu: Trích toàn bộ văn bản trong ảnh, từ văn bản đó lọc những từ khóa mà bạn nghĩ sẽ giúp ích cho việc tìm kiếm trên google search
Định dạng câu trả lời: "<văn bản từ ảnh>\n<các từ khóa cách nhau bởi dấu ', '>"
"""

def extract(image: Image.Image):
    if image is None:
        return "No image provided", "", ""

    # Chuyển ảnh thành bytes, mã hoá base64
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()

    response = client.models.generate_content(
        model="gemini-2.5-flash",  # hoặc gemini-2.5-pro nếu account bạn có quyền
        contents=[
            types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
            types.Part.from_text(text=PROMPT)
        ],
    )

    text = response.candidates[0].content.parts[0].text.strip()

    if "\n" in text:
        full_text, keywords = text.rsplit("\n", 1)
    else:
        full_text, keywords = text, ""

    # Open Google search in a new tab
    search_query = keywords.replace(' ', '+')
    google_url = f"https://www.google.com/search?q={search_query}&udm=50"

    return full_text, keywords, google_url

def make_ui():
    with gr.Blocks() as demo:
        gr.Markdown("# 🔍 OCR Keyword Search (Gradio)")
        inp = gr.Image(type="pil", label="Upload image")
        out_txt = gr.Textbox(label="Image Text", lines=5)
        out_kw = gr.Textbox(label="Extracted Keywords", lines=5)
        btn_extrac = gr.Button("Extract")
        out_url = gr.Textbox(label="Url", lines=5)
        btn_search = gr.Button("Google Search")

        inp.clear(
            lambda: ("", "", ""),
            outputs=[out_txt, out_kw, out_url]
        )
        btn_extrac.click(
            extract,
            inputs=inp,
            outputs=[out_txt, out_kw, out_url]
        )
        btn_search.click(
            fn=None,
            inputs=out_url,
            outputs=None,
            js="""
                (url) => { window.open(url, '_blank'); }
            """
        )

    return demo

demo = make_ui()


if __name__ == '__main__':
    demo.launch()