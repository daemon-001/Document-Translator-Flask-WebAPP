# Document Translation Web App

A Flask-based web application for translating text and documents into multiple languages using Google's Gemini AI.

## Features
- Translate text input or uploaded documents (PDF, TXT) into various languages.
- Supports 22 Indian languages listed below.
  ```
    1. Hindi
    2. English
    3. Telugu
    4. Bengali
    5. Marathi
    6. Tamil
    7. Urdu
    8. Gujarati
    9. Malayalam
    10. Kannada
    11. Odia
    12. Punjabi
    13. Assamese
    14. Maithili
    15. Santali
    16. Kashmiri
    17. Nepali
    18. Konkani
    19. Sindhi
    20. Dogri
    21. Manipuri
    22. Bodo
  ```
- Generates a downloadable PDF file of the translated text.
- User-friendly UI with Tailwind CSS styling.
- Supports file upload and direct text translation.
- Secure session management.

## Technologies Used
- **Backend:** Flask (Python), Google Gemini AI
- **Frontend:** HTML, CSS (TailwindCSS), JavaScript
- **Libraries:** PyPDF2, ReportLab

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/daemon-001/Document-Translator-Flask-WebAPP.git
   cd Document-Translator-Flask-WebAPP
   ```
2. Install dependencies:
   ```sh
   pip install flask google-generativeai PyPDF2 reportlab
   ```
3. Run the application:
   ```sh
   python app.py
   ```
4. Open in your browser: `http://127.0.0.1:5000/`

## Usage
- Navigate to the home page.
- Click **Translate Now** to access the translation tool.
- Upload a PDF/TXT file or enter text manually.
- Select the target language and hit **Translate**.
- Download the translated text as a PDF if needed.

## API Configuration
Update the `app.py` file with your Gemini API key:
```python
import google.generativeai as genai

genai.configure(api_key='your_api_key_here')
```

## Snapshots
![Screenshot (78)](https://github.com/user-attachments/assets/fcbb89aa-737c-4995-92d4-8890fb89736e)
![Screenshot (83)](https://github.com/user-attachments/assets/4e5cf23d-40f6-47c6-8971-03715469ce08)
![Screenshot (84)](https://github.com/user-attachments/assets/b0b1f05f-5738-4340-bd29-d5e5aee6b247)
🚀 Thanks to Manish for developing a wonderful frontend! 😎

## Contributing
Pull requests are welcome! Feel free to open an issue for suggestions or improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---
Made with ❤️ using Flask and Google AI.

