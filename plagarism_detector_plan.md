# Plagiarism Detector — Implementation Plan

> Companion to the Project II proposal *"Plagiarism Detector"* (Gandaki College of
> Engineering and Science, Pokhara University). This document turns the proposal into a
> concrete, buildable plan: dataset sources, the one model we must train, an MVP you can
> submit **this week**, and the folder/architecture layout that the code in this repo follows.

---

## 0. TL;DR — what we are building

A **free, no-login, web-based plagiarism detector** that:

1. Accepts **multiple file uploads** (PDF, DOCX, TXT, images) *or* pasted text.
2. Extracts text (Tesseract **OCR** for images/scanned PDFs, English).
3. Compares **every document against every other** (intra-class *all-pairs* matrix).
4. Compares each document against **web pages** (scraping) — external plagiarism.
5. Shows a **similarity matrix**, a **"X % copied"** score, and **sentence-level highlights**.

**Two similarity engines** (exactly as in the proposal):
- **Baseline:** TF-IDF + cosine similarity (implemented from scratch with PyTorch tensors, *not* scikit-learn, since you are learning PyTorch).
- **Proposed / the model we TRAIN:** a **fine-tuned Sentence-BERT** (`all-MiniLM-L6-v2`) trained on a large labelled plagiarism/paraphrase dataset.

> **The one model we train (requirement satisfied):** we take a *pretrained* `all-MiniLM-L6-v2`
> and **fine-tune** it on a heavy (100k–366k pair) labelled dataset. Fine-tuning **is** training —
> it produces a new checkpoint `models/plagiarism-sbert/` that we own and can defend.

---

## 1. Where the proposal is thin — and my recommendation

| Proposal says | Issue | Recommendation |
|---|---|---|
| Backend = **FastAPI** (Table 1) | You told me you want **Django** | ✅ Use **Django + Django REST Framework**. It's fine — mention in defense you switched for the admin panel + batteries-included ORM. Frontend stays **React**. |
| Dataset = "Kaggle Plagiarism Detection Dataset by *jobrieniii*, 100k pairs, 4 classes" | **No link in the proposal**, and the exact set is hard to locate/verify | ✅ Use the **MIT Plagiarism Detection Dataset** (366,915 labelled pairs, real & downloadable) as the *training-heavy* set, and the **Clough & Stevenson** corpus (the true "cut / light / heavy / original" 4-class set) for **evaluation**. See §2. |
| "Jaccard similarity" appears in Fig 1 but not in the text | Minor inconsistency | Optional third baseline; cheap to add, good for the report's comparison table. |
| Web scraping "queries a search engine" | Search engines block scraping / need paid APIs | ✅ MVP: use a **search API** (SerpAPI/Bing free tier) *or* a fixed list of candidate URLs. Fall back gracefully. See §5. |

**Bottom line:** the proposal is solid and buildable. The only real gap was the dataset link — fixed below.

---

## 2. Dataset sources (this is the section you asked for)

### 2.0 Best 3–4 datasets at a glance (use these) ⭐

| # | Dataset | Size | Label | Direct source | Role in project |
|---|---|---|---|---|---|
| 1 | **MIT Plagiarism Detection** | **366,915 pairs** | plagiarised / not (0–1) | [kaggle.com/datasets/ruvelpereira/mit-plagairism-detection-dataset](https://www.kaggle.com/datasets/ruvelpereira/mit-plagairism-detection-dataset) | **TRAIN** the SBERT model (heavy set) |
| 2 | **Clough & Stevenson** | ~100 docs | near-copy / light / heavy / original | [github.com/josecruzado21/plagiarism_detection](https://github.com/josecruzado21/plagiarism_detection) | **EVALUATE** (matches proposal's 4 classes) |
| 3 | **Quora Question Pairs (QQP)** | ~404,000 pairs | duplicate / not | [kaggle.com/c/quora-question-pairs](https://www.kaggle.com/c/quora-question-pairs) · HF: `load_dataset("glue","qqp")` | Extra paraphrase training data |
| 4 | **MRPC** (MS Research Paraphrase) | 5,801 pairs | paraphrase / not | HF: `load_dataset("glue","mrpc")` | Clean paraphrase eval / sanity check |

> **Just want to start?** Download **#1 (MIT)**, drop it in `notebooks/data/`, and run
> `01_train_similarity_model.ipynb`. Everything else is optional augmentation.

### 2.1 PRIMARY — the heavy set we FINE-TUNE on ⭐

**MIT Plagiarism Detection Dataset** — 366,915 labelled sentence pairs (a cleaned subset of the
Stanford SNLI corpus), columns roughly `source_text`, `plagiarism_text`, `label` (0/1).

- Kaggle: https://www.kaggle.com/datasets/ruvelpereira/mit-plagairism-detection-dataset
- Why: large enough to be a real training job, binary label maps directly to
  "plagiarised / not", and it's genuinely downloadable (unlike the proposal's unnamed set).
- Used by many reference notebooks, e.g. https://www.kaggle.com/code/hakim11/plagiarism-detection-model-using-lstm

> This is the dataset the training notebook (`notebooks/01_train_similarity_model.ipynb`) expects.
> Download it, unzip into `notebooks/data/`, done.

### 2.2 EVALUATION — the true 4-class set from the proposal's description

**Clough & Stevenson Corpus** (University of Sheffield) — ~100 short answer documents labelled
**near-copy / light revision / heavy revision / non-plagiarised** (exactly the "cut / light
paraphrase / heavy paraphrase / original" taxonomy in your proposal).

- Reference implementation & data: https://github.com/josecruzado21/plagiarism_detection
- Why: small but *perfectly* matches the proposal's 4 categories → great for the results table
  and for a qualitative demo in the defense. Too small to train on alone → use only to evaluate.

### 2.3 STRONG ALTERNATIVES / augmentation (all real & free)

| Dataset | Size | Label | Get it | Use for |
|---|---|---|---|---|
| **Quora Question Pairs (QQP)** | ~404k pairs | duplicate / not | Kaggle *"Quora Question Pairs"*; also in HF `glue`, config `qqp` | Extra paraphrase training data |
| **MRPC** (MS Research Paraphrase Corpus) | 5,801 pairs | paraphrase / not | HF `glue`, config `mrpc` | Small, clean paraphrase eval |
| **PAWS** | ~108k pairs | paraphrase / not | HF `paws`, config `labeled_final` | *Adversarial* (word-swap) hard cases |
| **STS-B** | 8,628 pairs | score 0–5 | HF `glue`, config `stsb` | Graded similarity (regression) eval |
| **SNLI / MNLI** | 570k / 433k | entailment/neutral/contradiction | HF `snli`, `multi_nli` | Sentence-pair pretraining signal |
| **PAN plagiarism corpus** | large | span-level | https://pan.webis.de/data.html | Classic academic benchmark (report citation) |

**HuggingFace one-liner** for any of the above:
```python
from datasets import load_dataset
ds = load_dataset("glue", "mrpc")          # or "qqp", "stsb"
ds = load_dataset("paws", "labeled_final")
```

### 2.4 Recommended final choice (simple + defensible)

- **Train:** MIT Plagiarism Detection Dataset (§2.1). *(Subsample to 30k–50k pairs for a
  fast MVP run; use the full set for the final model.)*
- **Evaluate:** Clough & Stevenson (§2.2) + a held-out split of the MIT set.
- **Mention in report:** QQP / MRPC / PAWS as augmentation options and STS-B for graded scoring.

---

## 3. Architecture (LLD, kept deliberately simple)

```
plagarism-detector/
├── plagarism_detector_plan.md      ← this file
├── README.md                       ← how to run everything
├── notebooks/
│   ├── 01_train_similarity_model.ipynb   ← TRAIN (PyTorch fine-tune of SBERT)  ⭐
│   ├── 02_web_scraping_similarity.ipynb  ← scrape + compare (no training)
│   └── data/                             ← put datasets here (gitignored)
├── backend/                        ← Django + DRF
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/                     ← project settings
│   └── detector/                   ← the app
│       ├── services/               ← ALL logic lives here (single responsibility each)
│       │   ├── text_extraction.py  ← PDF/DOCX/TXT/image → text (Tesseract OCR)
│       │   ├── preprocess.py       ← lowercase, stopwords, sentence split
│       │   ├── similarity.py       ← TF-IDF (PyTorch) + SBERT engines
│       │   ├── highlighter.py      ← sentence-level matched-span detection
│       │   └── web_scraper.py      ← BeautifulSoup fetch + compare
│       ├── views.py                ← thin HTTP layer, calls services
│       ├── serializers.py
│       └── urls.py
└── frontend/                       ← React (Vite)
    └── src/
        ├── api.js                  ← one place that talks to Django
        ├── components/
        │   ├── FileUploader.jsx
        │   ├── SimilarityMatrix.jsx
        │   └── HighlightedText.jsx
        └── App.jsx
```

**LLD principles applied (so the code stays beginner-friendly):**
- **Single Responsibility:** each file in `services/` does *one* thing.
- **Views are thin:** an HTTP view only parses the request, calls a service, returns JSON.
- **The model is pluggable:** `similarity.py` loads the fine-tuned checkpoint *if it exists*,
  otherwise falls back to the stock pretrained model → the app runs even before you train.
- **No premature abstraction:** plain functions and small classes, no design-pattern soup.

### Pipeline (matches proposal §3.2.3)

```
upload → extract text (OCR) → preprocess → embed (TF-IDF + SBERT)
      → all-pairs cosine similarity  ┐
      → web scrape + cosine similarity┘→ threshold (0.7) → highlight → report (matrix + %)
```

---

## 4. The model we train — details for `01_train_similarity_model.ipynb`

- **Base:** `sentence-transformers/all-MiniLM-L6-v2` (384-dim, lightweight).
- **Framework:** **PyTorch** (via `sentence-transformers`, which is pure PyTorch under the hood —
  satisfies "use PyTorch not scikit-learn"). We also show a **from-scratch PyTorch training loop
  variant** so you can explain forward/backward pass in the defense.
- **Task setup:** sentence pairs → label (1 = plagiarised/duplicate, 0 = original).
  - Loss: `OnlineContrastiveLoss` (pulls plagiarised pairs together, pushes originals apart) OR
  - Loss: `CosineSimilarityLoss` if you treat the label as a target similarity (0/1).
- **Output:** a saved checkpoint `backend/detector/models/plagiarism-sbert/` that the Django
  similarity service auto-loads.
- **Eval metrics:** accuracy, F1, and cosine-AUC on a held-out split + Clough & Stevenson.
- **Runtime:** subsample to ~30k pairs, 1 epoch → a few minutes on GPU / ~20–30 min CPU. Plenty
  for an MVP and a "we trained a model" claim you can defend.

---

## 5. Web scraping (external plagiarism) — realistic MVP

The proposal says "query a search engine + scrape top 10". Pure search-engine scraping is
fragile (Google/Bing block bots). MVP-safe options, in order of preference:

1. **Search API + BeautifulSoup fetch** — use a free tier (SerpAPI / Bing Web Search / Brave
   Search API) to get candidate URLs from document keywords, then fetch & strip each page with
   `requests` + BeautifulSoup, then cosine-compare. *(Recommended.)*
2. **DuckDuckGo HTML endpoint** (`html.duckduckgo.com/html/`) — no key, lighter blocking.
3. **Fixed candidate URLs** — for the demo, let the user paste 1–3 URLs to check against. Zero
   external dependency, always works in the defense room.

`web_scraper.py` implements (2)+(3) with a graceful fallback so the demo never dies on Wi-Fi.

---

## 6. MVP scope — what to finish THIS WEEK

**Goal:** a working end-to-end demo — upload 2+ files, see a similarity matrix, see highlights.

| Day | Deliverable | Status file |
|---|---|---|
| 1 | Django project runs; `POST /api/compare` accepts text + returns a matrix | `backend/` |
| 1 | React upload page hits the API and renders the matrix | `frontend/` |
| 2 | Text extraction for PDF/DOCX/TXT + Tesseract OCR for images | `services/text_extraction.py` |
| 2 | Sentence-level highlighting ("this much copied") | `services/highlighter.py` |
| 3 | Run `01_train_similarity_model.ipynb`, save checkpoint, wire into backend | `notebooks/` |
| 3 | Web-scrape compare (paste-URL fallback is enough for MVP) | `services/web_scraper.py` |
| 4 | Polish, seed 3–4 sample docs, write demo script | — |

**Definition of done for the MVP submission**
- [ ] Upload ≥2 files → intra-class similarity matrix renders.
- [ ] At least one pair shows sentence-level highlights + a "% copied" number.
- [ ] The fine-tuned SBERT checkpoint exists and is loaded (falls back gracefully if not).
- [ ] One notebook that **trains** the model runs top-to-bottom.
- [ ] README explains how to run backend, frontend, and the notebooks.

**Explicitly OUT of MVP scope** (say so in the defense; keep for Sprint 2+):
- Full search-engine scraping at scale, DOCX-with-images edge cases, auth, deployment,
  Devanagari/Nepali OCR, chunking of very long documents (stub included, not tuned).

---

## 7. How each proposal claim is covered

| Proposal claim | Where in this repo |
|---|---|
| Multi-file upload (PDF/DOCX/TXT/image) | `text_extraction.py`, `FileUploader.jsx` |
| Tesseract OCR (English) | `text_extraction.py` (`pytesseract`) |
| Intra-class all-pairs matrix | `similarity.py` → `all_pairs_matrix()`, `SimilarityMatrix.jsx` |
| TF-IDF baseline | `similarity.py` → `TfidfEngine` (PyTorch tensors) |
| Fine-tuned Sentence-BERT | `01_train_similarity_model.ipynb` → checkpoint → `SbertEngine` |
| Web scraping (up to 10 pages) | `web_scraper.py` |
| Sentence-level highlights | `highlighter.py`, `HighlightedText.jsx` |
| Threshold 0.7 decision | `similarity.py` (`DEFAULT_THRESHOLD = 0.7`) |
| No login / no permanent storage | Django views process in-memory, nothing persisted by default |

---

## 8. Tech stack (final)

- **Frontend:** React (Vite) + fetch + **Tailwind CSS** for styling.
- **Backend:** Django + Django REST Framework.
- **ML:** PyTorch + `sentence-transformers` + `transformers` + `datasets`.
- **Text:** `pdfplumber` / `python-docx` / `pytesseract` (+ system Tesseract binary).
- **Scraping:** `requests` + `beautifulsoup4`.
- **Notebooks:** Jupyter, PyTorch.

See `README.md` for exact install/run commands.

---

## 9. References & sources

### Datasets
1. **MIT Plagiarism Detection Dataset** (366,915 pairs, subset of SNLI) — Kaggle.
   https://www.kaggle.com/datasets/ruvelpereira/mit-plagairism-detection-dataset
2. **Clough, P. & Stevenson, M.** — *A Corpus of Plagiarised Short Answers* (near-copy / light /
   heavy / non-plagiarised). Reference code & data:
   https://github.com/josecruzado21/plagiarism_detection
3. **Quora Question Pairs (QQP)** — Kaggle competition.
   https://www.kaggle.com/c/quora-question-pairs
4. **MRPC — Microsoft Research Paraphrase Corpus** (GLUE). Dolan & Brockett, 2005.
   https://huggingface.co/datasets/glue
5. **PAWS — Paraphrase Adversaries from Word Scrambling**, Zhang et al., 2019.
   https://huggingface.co/datasets/paws
6. **STS-B — Semantic Textual Similarity Benchmark** (GLUE).
   https://huggingface.co/datasets/glue
7. **SNLI / MultiNLI** corpora. https://huggingface.co/datasets/snli
8. **PAN plagiarism detection corpora** (academic benchmark).
   https://pan.webis.de/data.html

### Models, tools & methods
9. **Sentence-BERT** — Reimers & Gurevych, *Sentence-BERT: Sentence Embeddings using Siamese
   BERT-Networks*, EMNLP 2019. https://arxiv.org/abs/1908.10084
10. **all-MiniLM-L6-v2** pretrained model.
    https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
11. **BERT** — Devlin et al., 2018. https://arxiv.org/abs/1810.04805
12. **TF-IDF / cosine similarity** — classical IR baseline (see any IR textbook, e.g.
    Manning, Raghavan & Schütze, *Introduction to Information Retrieval*, 2008).
13. **Tesseract OCR** (Google, open source). https://github.com/tesseract-ocr/tesseract
14. **BeautifulSoup** (web scraping). https://www.crummy.com/software/BeautifulSoup/
15. **sentence-transformers** library. https://www.sbert.net/
16. **PyTorch**. https://pytorch.org/
17. **Django REST Framework**. https://www.django-rest-framework.org/

### Helpful reference implementations / reading
18. Pinecone — *Plagiarism Detection Using Transformers*.
    https://www.pinecone.io/learn/plagiarism-detection/
19. Kaggle — *Plagiarism Detection Model Using LSTM* (uses the MIT dataset).
    https://www.kaggle.com/code/hakim11/plagiarism-detection-model-using-lstm
20. Medium — *Fine-Tuning BERT for Paraphrase Detection: A Step-by-Step Guide*.
    https://medium.com/@viswadarshanrramiya/fine-tuning-bert-for-paraphrase-detection-a-step-by-step-guide-54fc90836d0d

> Citations [1]–[7] in the proposal (Turnitin, Tesseract, TF-IDF, Sentence-BERT, Kaggle dataset,
> Grammarly, BERT) all map onto the references above — reuse these URLs to fill the proposal's
> Bibliography where links were missing.

