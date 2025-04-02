from flask import Flask, render_template, request, send_file, session
import google.generativeai as genai
import PyPDF2
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate
import os
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
logging.basicConfig(level=logging.DEBUG)

# Add your Google API key here or set it as an environment variable
api_key = os.getenv('API_KEY')

genai.configure(api_key = api_key)
model = genai.GenerativeModel('gemini-1.5-flash-8b')

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

# Font paths - you'll need to download these fonts
FONTS_DIR = 'static/fonts/'
os.makedirs(FONTS_DIR, exist_ok=True)

# Define fonts for different languages
LANGUAGE_FONTS = {
    'default': {
        'name': 'FreeSans',
        'path': f'{FONTS_DIR}FreeSans.ttf'
    },
    'hindi': {
        'name': 'NotoSansDevanagari',
        'path': f'{FONTS_DIR}NotoSansDevanagari-Regular.ttf'
    },
    'bengali': {
        'name': 'NotoSansBengali',
        'path': f'{FONTS_DIR}NotoSansBengali-Regular.ttf'
    },
    'telugu': {
        'name': 'NotoSansTelugu',
        'path': f'{FONTS_DIR}NotoSansTelugu-Regular.ttf'
    },
    # Add more languages as needed
}

def register_fonts():
    """Register fonts for PDF generation"""
    # Register default font
    try:
        if not os.path.exists(LANGUAGE_FONTS['default']['path']):
            logging.warning(f"Default font file not found: {LANGUAGE_FONTS['default']['path']}")
            return False
            
        pdfmetrics.registerFont(TTFont(LANGUAGE_FONTS['default']['name'], 
                                      LANGUAGE_FONTS['default']['path']))
        
        # Register language-specific fonts if available
        for lang, font in LANGUAGE_FONTS.items():
            if lang != 'default' and os.path.exists(font['path']):
                pdfmetrics.registerFont(TTFont(font['name'], font['path']))
                logging.info(f"Registered font for {lang}: {font['name']}")
        
        return True
    except Exception as e:
        logging.error(f"Error registering fonts: {str(e)}")
        return False

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
        logging.error(f"Translation error: {str(e)}")
        return f"Translation error: {str(e)}"

def create_translated_pdf(translated_text, target_language='default'):
    """Create a new PDF with translated text with proper font support"""
    buffer = io.BytesIO()
    
    # Register fonts first
    if not register_fonts():
        # If font registration fails, attempt to create PDF with basic functionality
        logging.warning("Font registration failed. Creating PDF with limited font support.")
    
    # Create a PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Determine which font to use
    font_name = LANGUAGE_FONTS['default']['name']
    if target_language in LANGUAGE_FONTS and os.path.exists(LANGUAGE_FONTS[target_language]['path']):
        font_name = LANGUAGE_FONTS[target_language]['name']
    
    # Create a custom style with the appropriate font
    custom_style = ParagraphStyle(
        'CustomStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        leading=14,
        encoding='utf-8'
    )
    
    # Create content for the PDF
    content = []
    
    # Add a title
    title = Paragraph(f"Translated Document ({LANGUAGES.get(target_language, 'Unknown')})", styles['Title'])
    content.append(title)
    
    # Add the translated text
    if translated_text:
        # Clean up the text and split into paragraphs
        paragraphs = translated_text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                try:
                    p = Paragraph(para.replace('\n', '<br/>'), custom_style)
                    content.append(p)
                except Exception as e:
                    logging.error(f"Error creating paragraph: {str(e)}")
                    # Fallback to simpler text if paragraph creation fails
                    content.append(Paragraph(f"[Content formatting error: {str(e)}]", styles['Normal']))
    else:
        content.append(Paragraph("No translation available", styles['Normal']))
    
    try:
        # Build the PDF
        doc.build(content)
        buffer.seek(0)
        return buffer
    except Exception as e:
        logging.error(f"Error building PDF: {str(e)}")
        # Create a simple error PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, f"Error creating PDF: {str(e)}")
        c.drawString(100, 730, "Please download Noto fonts for proper display of non-Latin scripts.")
        c.save()
        buffer.seek(0)
        return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['GET', 'POST'])
def translate():
    translation = ''
    pdf_available = False
    target_language = 'hindi'  # Default language
    
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
                                      languages=LANGUAGES,
                                      pdf_available=False)
            
            # Get selected language
            target_language = request.form.get('language', 'hindi')
            
            # Translate text
            translation = translate_text(text, target_language)
            
            # Only set pdf_available if we have valid translation text
            pdf_available = bool(translation) and 'error' not in translation.lower()
            
            # Store translation in session
            session['last_translation'] = translation
            session['pdf_available'] = pdf_available
            session['target_language'] = target_language
            
        except Exception as e:
            logging.error(f"Translation error: {str(e)}")
            translation = f'An error occurred during translation: {str(e)}'
            pdf_available = False
    
    return render_template('translate.html', 
                          translation=translation, 
                          languages=LANGUAGES,
                          pdf_available=pdf_available)

@app.route('/download-pdf')
def download_pdf():
    try:
        # Retrieve translation from session
        translation = session.get('last_translation', 'No translation available')
        target_language = session.get('target_language', 'default')
        
        # Create PDF with language-specific font
        buffer = create_translated_pdf(translation, target_language)
        
        return send_file(buffer, 
                        mimetype='application/pdf', 
                        as_attachment=True, 
                        download_name='translated_document.pdf')
    except Exception as e:
        logging.error(f"PDF generation error: {str(e)}")
        return "Error generating PDF. Please try again.", 500

if __name__ == '__main__':
    app.run(debug=True)