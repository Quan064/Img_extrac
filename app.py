import easyocr
from PIL import Image
import numpy as np
from keybert import KeyBERT
import gradio as gr

# Initialize EasyOCR reader (English)
reader = easyocr.Reader(['en'], gpu=False)

# Initialize KeyBERT model
kw_model = KeyBERT()


def extract(image: Image.Image):
    if image is None:
        return "No image provided", "", ""

    img_np = np.array(image)
    result = reader.readtext(img_np)
    text = " ".join([item[1] for item in result])

    if text:
        keywords = kw_model.extract_keywords(text, top_n=5)
        keywords = [kw[0] for kw in keywords]
    else:
        keywords = ["(no text detected)"]

    # Open Google search in a new tab
    search_query = '+'.join(keywords).replace(' ', '+')
    google_url = f"https://www.google.com/search?q={search_query}&udm=50"

    return text, ", ".join(keywords), google_url

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