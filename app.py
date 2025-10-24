import easyocr
from PIL import Image
import numpy as np
import yake  # thư viện lọc keyword
import gradio as gr 

# Initialize EasyOCR reader (English)
reader = easyocr.Reader(['en'], gpu=False)


def extract(image: Image.Image):
    if image is None:
        return "No image provided", ""

    img_np = np.array(image)
    result = reader.readtext(img_np)
    text = " ".join([item[1] for item in result])

    # Extract keywords with YAKE
    kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=5)
    keywords = [kw[0] for kw in kw_extractor.extract_keywords(text)]

    if not keywords:
        # Fallback to snippet of text
        snippet = text.strip()[:50] if text else ""
        keywords = [snippet] if snippet else ["(no text detected)"]

    # Open Google search in a new tab
    search_query = '+'.join(keywords).replace(' ', '+')
    google_url = f"https://www.google.com/search?q={search_query}&sca_esv=4acfbdfe9e621853&sxsrf=AE3TifPsxABFfPLcKrLHOn97__Z7pmX6SQ:1761217822568&udm=50&fbs=AIIjpHyNLa7NbKa1H9FnKAJNsjCPuuyZ8axF70qppVREZw12J16j6TEYGEwZz6y4Q0FA_xPGC4I8so7AzFphAtoRVW9eV1Zxdr4WLBH03E0qab3TDAaVvSCfcFNaPvLBtCeR6YMwMqixkNVtTqwBfOogZMDiETfzl_NHPTy4pZChbD-L-8D3ABwvzmTK6p8NKzbq65d1MZNT-MFg0R-5l2dkqeE9cGt52L6-U0JimcdHcx7W1Q99sEUHBxmqDrAQ9lOay9-xcpVt&aep=1&ntc=1&sa=X&ved=2ahUKEwiPp77Vl7qQAxVeyTgGHUZKB5QQ2J8OegQIDxAE&biw=1912&bih=924&dpr=1"

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