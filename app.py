from flask import Flask, render_template, request, send_file, session
import google.generativeai as genai
import PyPDF2
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  

# Configure Gemini API
genai.configure(api_key='your_api_key_here')
model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')

# Language mapping
LANGUAGES = {
    'hindi': 'Hindi',
    'english': 'English',
    'telugu': 'Telugu',
    'bengali': 'Bengali',
    'marathi': 'Marathi',
    'tamil': 'Tamil',
    'urdu': 'Urdu',
    'gujarati': 'Gujarati',
    'malayalam': 'Malayalam',
    'kannada': 'Kannada',
    'odia': 'Odia',
    'punjabi': 'Punjabi',
    'assamese': 'Assamese',
    'maithili': 'Maithili',
    'santali': 'Santali',
    'kashmiri': 'Kashmiri',
    'nepali': 'Nepali',
    'konkani': 'Konkani',
    'sindhi': 'Sindhi',
    'dogri': 'Dogri',
    'manipuri': 'Manipuri',
    'bodo': 'Bodo'
}

def extract_text_from_file(file):
    """Extract text from different file types"""
    filename = file.filename.lower()
    
    # PDF handling
    if filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text, pdf_reader
    
    # Plain text handling
    elif filename.endswith('.txt'):
        return file.read().decode('utf-8'), None
    
    return "Unsupported file type", None

def translate_text(text, target_language):
    """Translate text using Gemini"""
    try:
        response = model.generate_content(
            f"Translate this text to {LANGUAGES[target_language]}: {text}"
        )
        return response.text
    except Exception as e:
        return f"Translation error: {str(e)}"

def create_translated_pdf(translated_text):
    """Create a new PDF with translated text"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Register Arial font - make sure you have Arial.ttf in your project directory
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    c.setFont('Arial', 12)
    
    text_object = c.beginText(50, 750)
    for line in translated_text.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['GET', 'POST'])
def translate():
    if request.method == 'POST':
        try:
            # Check if file is uploaded
            if 'file' in request.files and request.files['file'].filename:
                file = request.files['file']
                text, _ = extract_text_from_file(file)
            
            # Check if text is pasted
            elif request.form.get('text'):
                text = request.form.get('text')
            
            else:
                return render_template('translate.html', 
                                    translation='No text provided', 
                                    languages=LANGUAGES)
            
            # Get selected language
            target_language = request.form.get('language', 'hindi')
            
            # Translate text
            translation = translate_text(text, target_language)
            
            # Store translation in session
            session['last_translation'] = translation
            
            return render_template('translate.html', 
                                translation=translation, 
                                languages=LANGUAGES,
                                pdf_available=True)
        
        except Exception as e:
            print(f"Translation error: {str(e)}")  # For debugging
            return render_template('translate.html', 
                                translation='An error occurred during translation.', 
                                languages=LANGUAGES)
    
    return render_template('translate.html', 
                        translation='', 
                        languages=LANGUAGES,
                        pdf_available=False)

@app.route('/download-pdf')
def download_pdf():
    # Retrieve translation from session
    translation = session.get('last_translation', 'No translation available')
    
    # Create PDF
    buffer = create_translated_pdf(translation)
    
    return send_file(buffer, 
                     mimetype='application/pdf', 
                     as_attachment=True, 
                     download_name='translated_document.pdf')

if __name__ == '__main__':
    app.run(debug=True)