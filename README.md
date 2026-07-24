# Plagiarism Detector - GCES Minor II Project

Hey, welcome to our project repo! This is a web-based plagiarism detector we built for our Minor II Project at Gandaki College of Engineering and Science (GCES). 

The main idea was to build something free and fast that doesn't save your files permanently (privacy first!). It checks documents against each other and also searches the web for copied content.

### Team Members
- Neon Neupane (Backend & ML)
- Bishal Acharya (Frontend)
- Nabin Giri (Frontend)

## Features
- **Upload Anything:** Supports PDF, Word docs, text files, and even images (uses OCR to read text from pictures).
- **Intra-class Checking:** Compares a batch of documents against each other to see who copied from whom.
- **Web Checking:** Searches DuckDuckGo to make sure the text wasn't just copy-pasted from Wikipedia.
- **Smart Matching:** Uses a fine-tuned Sentence-BERT model (PyTorch) to catch paraphrased sentences, not just exact word matches.

## Folder Structure
- `frontend/` - React and Vite stuff. This is the UI where you upload files.
- `backend/` - Django server. Handles the AI model, OCR, and API endpoints.
- `notebooks/` - Our Jupyter notebooks used to train the AI model on the MIT Plagiarism dataset.

## How to Run It locally

### 1. Backend (Django)
You'll need Python installed. We also use Tesseract for OCR, so make sure that's installed on your system if you want to test image uploads.
```bash
cd backend
python -m venv .venv
# On Windows: .\.venv\Scripts\activate
# On Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```
The server will run on `http://localhost:8000`.

### 2. Frontend (React)
Open a new terminal and make sure you have Node.js installed.
```bash
cd frontend
npm install
npm run dev
```
It usually runs on `http://localhost:5173`. Open that in your browser and you're good to go!

---
*Built for the Project II defense.*
