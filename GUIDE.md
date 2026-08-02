# 📘 Full Guide — Plagiarism Detector

Everything that was built, how to run it, how to train the model, and how to demo it.
This is your one-stop reference.

---

## 1. What this project is

A **free, no-login, web-based plagiarism detector**:

- Upload **multiple documents** (PDF, DOCX, TXT, images) or paste text.
- Text is extracted (Tesseract **OCR** for images/scanned PDFs).
- Every document is compared against **every other** → **similarity matrix** (who copied whom).
- Each document can be checked against **web pages** (scraping).
- Results show a **"% copied"** score and **sentence-level highlights**.
- Two engines: **TF-IDF baseline** (hand-written in PyTorch) and a **fine-tuned Sentence-BERT** (the model you train).

**Stack:** React + Vite + **Tailwind CSS** (frontend) · **Django** + DRF (backend) · **PyTorch** + Sentence-BERT (ML).

---

## 2. Folder structure

```
plagarism-detector/
├── plagarism_detector_plan.md   ← the plan + dataset sources + references
├── GUIDE.md                     ← this file
├── README.md                    ← short quick-start
├── train.py                     ← ⭐ ONE-COMMAND model training (auto-download + save)
├── .venv/                       ← Python virtual environment (already created)
├── notebooks/
│   ├── 01_train_similarity_model.ipynb   ← training in notebook form (for your report)
│   └── 02_web_scraping_similarity.ipynb  ← web-scraping demo (no training)
├── backend/                     ← Django API
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/                  ← Django settings/urls/wsgi
│   └── detector/
│       ├── views.py             ← thin HTTP layer (parses request → calls a service)
│       ├── urls.py
│       ├── services/            ← ALL logic (one responsibility per file)
│       │   ├── text_extraction.py  ← file → text (+ Tesseract OCR)
│       │   ├── preprocess.py       ← clean, tokenize, split sentences
│       │   ├── similarity.py       ← TF-IDF (PyTorch) + SBERT engines + all-pairs matrix
│       │   ├── highlighter.py      ← sentence-level matches + % copied
│       │   └── web_scraper.py      ← search + scrape + compare
│       └── models/              ← trained model saved here (plagiarism-sbert/)
└── frontend/                    ← React + Vite + Tailwind
    └── src/
        ├── api.js               ← the only file that talks to the backend
        ├── App.jsx
        └── components/          ← FileUploader, SimilarityMatrix, HighlightedText
```

---

## 3. Prerequisites (already done ✅)

These were installed for you:

- Python venv at `plagarism-detector/.venv` with all backend + ML packages
  (torch, sentence-transformers, transformers, datasets, accelerate, Django, DRF,
  pdfplumber, python-docx, pytesseract, BeautifulSoup, pandas).
- Frontend `node_modules` (React, Vite, Tailwind).

**One system package you may still need** (for image/scanned-PDF OCR only):

```bash
sudo apt install tesseract-ocr        # Ubuntu/Debian
# brew install tesseract              # macOS
```

Text/PDF/DOCX work without it; only image OCR needs the Tesseract binary.

---

## 4. Run the app (2 terminals)

**Terminal 1 — backend (Django):**
```bash
cd plagarism-detector
.venv/bin/python backend/manage.py runserver          # → http://localhost:8000
```

**Terminal 2 — frontend (React):**
```bash
cd plagarism-detector/frontend
npm run dev                                           # → http://localhost:5173
```

Open **http://localhost:5173**, drag in 2+ files, click **Check plagiarism**.
The Vite dev server proxies `/api` to Django automatically.

---

## 5. ⭐ Train the model (one command)

You train **once**, it **saves the model**, then the app just loads it. You do NOT
retrain on every run — exactly the workflow you described.

```bash
cd plagarism-detector

# Default: QQP dataset (364k pairs), downloaded automatically — NO Kaggle login needed.
.venv/bin/python train.py

# Faster options:
.venv/bin/python train.py --dataset mrpc              # small paraphrase set (quick)
.venv/bin/python train.py --sample 30000 --epochs 1   # cap pairs for a fast MVP run
.venv/bin/python train.py --dataset paws              # adversarial paraphrases

# Use your Kaggle MIT dataset CSV instead (the "heavy" 366k set from the plan):
.venv/bin/python train.py --dataset csv --data notebooks/data/mit.csv
```

The model is saved to `backend/detector/models/plagiarism-sbert/`. After training,
`GET /api/health/` reports `"model_fine_tuned": true` and the UI shows **"using your
fine-tuned model ✅"**.

**Options:** `--dataset {qqp,mrpc,paws,csv}` · `--data <csv>` · `--sample <N>` (0 = all) ·
`--epochs <N>` · `--batch <N>` · `--base <model>` · `--out <path>`.

> Which dataset satisfies the "train on a heavy dataset" requirement?
> **QQP (364k pairs)** — heavy *and* auto-downloading. If your report specifically needs the
> MIT Plagiarism set (366k), download it from Kaggle and use `--dataset csv --data ...`.

### Or train in the notebook (for your report / defense)
`notebooks/01_train_similarity_model.ipynb` does the same thing cell-by-cell and includes a
from-scratch PyTorch training-step cell so you can explain forward/backward pass.

---

## 6. API reference

| Method | Endpoint | Body | Returns |
|---|---|---|---|
| GET | `/api/health/` | — | `{status, model_fine_tuned}` |
| POST | `/api/compare/` | multipart `files` (2+) **or** JSON `texts:[{name,text}]`, optional `method` (`sbert`\|`tfidf`) | similarity `matrix` + `flagged_pairs` with sentence matches |
| POST | `/api/check-web/` | one `files` item or `texts`, optional `urls:[...]` | `sources` scored by similarity |

Quick test:
```bash
curl -F "files=@a.txt" -F "files=@b.txt" http://localhost:8000/api/compare/
```

---

## 7. How to demo (for submission/defense)

**Ready-made sample files are in `samples/`** — no prep needed:
- `doc1_original.txt` + `doc2_paraphrased.txt` → same meaning, different words (photosynthesis)
- `doc3_unrelated.txt` → different topic (French Revolution)

Steps:
1. Start backend + frontend.
2. On the **"Compare documents"** tab, upload all three files from `samples/`.
3. The matrix lights up **red** for doc1↔doc2 (verified **0.90 similarity, 100% copied**) and
   stays green for doc3 (≈0.02–0.07).
4. Scroll down → the flagged pair shows the **"% copied"** bar and the matching sentences.
5. Point out it catches **paraphrasing** — that's the SBERT model, not just word matching.
6. Switch to the **"Check against web"** tab, paste a paragraph, add a URL (e.g. a Wikipedia
   page), and show the scraped source scored above the threshold (verified 0.759 → flagged).

---

## 8. How it maps to the proposal

| Proposal feature | Where |
|---|---|
| Multi-file upload + OCR | `services/text_extraction.py`, `FileUploader.jsx` |
| Intra-class all-pairs matrix | `services/similarity.py` → `all_pairs_matrix()` |
| TF-IDF baseline (PyTorch) | `services/similarity.py` → `TfidfEngine` |
| Fine-tuned Sentence-BERT | `train.py` / notebook 01 → `SbertEngine` |
| Web scraping | `services/web_scraper.py`, notebook 02 |
| Sentence-level highlights + threshold 0.7 | `services/highlighter.py` |
| No login / no permanent storage | `views.py` processes in memory |

**Deviations from the proposal (mention in defense):** backend is **Django** (proposal said
FastAPI) for the batteries-included admin/ORM; similarity is **PyTorch**, not scikit-learn.

---

## 9. Datasets (summary — full list in the plan)

| Dataset | Size | Get it | Use |
|---|---|---|---|
| **QQP** | 364k | auto via `train.py` | **train** (default) |
| **MIT Plagiarism** | 366k | [Kaggle](https://www.kaggle.com/datasets/ruvelpereira/mit-plagairism-detection-dataset) | **train** (heavy, from the proposal) |
| **Clough & Stevenson** | ~100 | [GitHub](https://github.com/josecruzado21/plagiarism_detection) | evaluate (4-class) |
| **MRPC / PAWS** | 5.8k / 108k | auto via `train.py` | quick train / adversarial eval |

---

## 10. Troubleshooting

| Symptom | Fix |
|---|---|
| `Invalid HF URI 'hf://datasets/glue'` | Already fixed — `train.py` uses namespaced ids (`nyu-mll/glue`). |
| `requires accelerate>=1.1.0` | Already installed. If missing: `.venv/bin/pip install accelerate`. |
| Image upload returns empty text | Install the Tesseract binary (`sudo apt install tesseract-ocr`). |
| First `/compare/` is slow | It downloads `all-MiniLM-L6-v2` (~90 MB) once, then it's cached. |
| Torch venv is huge (4 GB) | It pulled the CUDA stack. For CPU-only: `pip install torch --index-url https://download.pytorch.org/whl/cpu`. |
| CORS errors | The backend allows all origins in dev (`config/settings.py`). |

---

## 11. What's verified working

- ✅ Backend installs, Django system check passes, server boots.
- ✅ `/api/compare/` on the 3 sample files: doc1↔doc2 = 0.90 (100% copied), doc3 ≈ 0.02–0.07.
- ✅ `/api/check-web/` scrapes a URL and scores it (Wikipedia photosynthesis = 0.759, flagged).
- ✅ Frontend builds (Tailwind, tabs, web-check panel) and the dev proxy reaches the API.
- ✅ `train.py` downloads data → trains → evaluates → saves the model (smoke-tested).

## 12. Nice next steps (optional, post-MVP)

- Run the full `train.py` (QQP, no `--sample`) for the final, higher-quality model.
- Add long-document chunking (stub exists in the plan).
- Add file upload (not just paste) to the web-check tab if you want parity with batch mode.
