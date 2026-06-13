# Plagiarism Detector - Architecture & Folder Explanation

This document explains the folder structure of your Plagiarism Detector project and how the different pieces connect to make the whole system work.

## Overall Architecture
The project is divided into two main parts: the **Frontend** (what the user sees and interacts with) and the **Backend** (the brain that does the heavy lifting, processing, and AI magic). There is also a **Notebooks** folder used purely for training the AI model.

```text
plagarism-detector/
├── frontend/                     ← React UI (User Interface)
├── backend/                      ← Django API (Server & AI logic)
├── notebooks/                    ← Training the Model
├── plagarism_detector_plan.md    ← Original implementation plan
├── explanation.md                ← This file
└── README.md                     ← Instructions to run the code
```

---

## 1. The Frontend (User Interface)
**Folder:** `frontend/`

This is built using **React** and **Vite**. It handles what the user sees in their browser.
- **`src/App.jsx`**: The main page of the application. It brings all the components together.
- **`src/api.js`**: This file is the bridge. It talks to the Django backend. When a user uploads a file, this file sends it to the backend server to be processed.
- **`src/components/FileUploader.jsx`**: The drag-and-drop area where users select their PDFs, Word docs, or text files.
- **`src/components/SimilarityMatrix.jsx`**: Once the backend finishes checking the files, this component displays the results in a grid (matrix) so you can easily see if Document A copied Document B.
- **`src/components/HighlightedText.jsx`**: Shows the actual text of the documents and highlights the exact sentences that were flagged as plagiarized.

---

## 2. The Backend (Server & Logic)
**Folder:** `backend/`

This is built using **Django** (a Python framework). It receives files from the frontend, reads them, and uses the AI model to calculate plagiarism.

Inside the `backend/detector/` folder, the logic is broken down into specific "services" so it is easy to understand:
- **`views.py`**: The "traffic cop". It receives the request from `frontend/api.js` and passes it to the services below.
- **`services/text_extraction.py`**: Reads the uploaded files. If you upload an image, it uses Tesseract OCR to read the text out of the picture. If it's a PDF, it pulls the text out.
- **`services/preprocess.py`**: Cleans up the text (removes weird characters, splits paragraphs into individual sentences) so the AI can understand it better.
- **`services/similarity.py`**: **This is the core of the project.** It takes the cleaned sentences and runs them through the Sentence-BERT AI model (or the TF-IDF baseline). It calculates the mathematical distance (cosine similarity) between sentences to give you a percentage score (e.g., 85% copied).
- **`services/web_scraper.py`**: If web checking is enabled, this file searches DuckDuckGo for keywords from the document, downloads the web pages, and compares the internet text against the student's text.
- **`services/highlighter.py`**: Figures out exactly which sentences matched so the frontend knows what to highlight in red.

---

## 3. The Model Training (AI)
**Folder:** `notebooks/`

This folder isn't used while the app is running. It is only used to **teach** the AI model.
- **`01_train_similarity_model.ipynb`**: This is a Jupyter Notebook where you wrote the code using PyTorch to take a pre-existing model (`all-MiniLM-L6-v2`) and train it on the MIT Plagiarism Dataset. 
- Once training is done, the resulting "smart" model is saved into `backend/detector/models/plagiarism-sbert/` so the Django backend can use it.

## Summary of the Flow
1. User drops files into **Frontend** (`FileUploader`).
2. Frontend sends files to **Backend** (`views.py`).
3. Backend extracts text (`text_extraction.py`).
4. Backend checks for internet plagiarism (`web_scraper.py`).
5. Backend runs the AI model to check for copying between the files (`similarity.py`).
6. Backend sends the results matrix back.
7. Frontend displays the grid and highlights (`SimilarityMatrix` & `HighlightedText`).
