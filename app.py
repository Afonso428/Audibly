from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from gtts import gTTS
from pdf2image import convert_from_path
import pytesseract
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'audio'

def extract_text_with_ocr(pdf_path):
    text = ""
    images = convert_from_path(pdf_path)
    for img in images:
        text += pytesseract.image_to_string(img)
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'pdf_file' not in request.files:
        return "No file part", 400

    file = request.files['pdf_file']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        reader = PdfReader(filepath)
        text = ''
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + '\n'
    except:
        text = ''

    if not text.strip():
        text = extract_text_with_ocr(filepath)

    if not text.strip():
        return "The uploaded PDF contains no extractable text.", 400

    tts = gTTS(text)
    audio_filename = f"{uuid.uuid4()}.mp3"
    audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
    tts.save(audio_path)

    return send_file(audio_path, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
