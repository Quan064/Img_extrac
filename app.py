from flask import Flask, render_template, request, redirect, jsonify
import pytesseract
from PIL import Image
import os
import yake  # thư viện lọc keyword

app = Flask(__name__)

# Nếu dùng Windows, cần chỉ định đường dẫn Tesseract nếu chưa có trong PATH
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get("image")
        if not file:
            return "No file uploaded", 400

        # Mở ảnh và OCR tiếng Anh
        image = Image.open(file.stream)
        text = pytesseract.image_to_string(image, lang='eng')

        # Dùng YAKE để trích keyword
        kw_extractor = yake.KeywordExtractor(lan="en", n=1, top=5)
        keywords = [kw[0] for kw in kw_extractor.extract_keywords(text)]

        # Nếu không tìm được keyword, trả về văn bản gốc
        if not keywords:
            keywords = [text.strip()[:50]]

        # Gộp keyword thành chuỗi tìm kiếm
        search_query = "+".join(keywords)
        google_url = f"https://www.google.com/search?q={search_query}"

        return jsonify({"search_url": google_url})

    return render_template('index.html')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)