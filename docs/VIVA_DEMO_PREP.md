# Plagiarism Detector — Explanation and Demo Guide

Project II · Gandaki College of Engineering and Science

A companion to [Architecture and Design](ARCHITECTURE_AND_DESIGN.md). That document
describes the system; this one is for standing in front of it and explaining it.

---

## Who studies what

Question ownership follows the Division of Work in the report. **Everyone learns sections
1, 2, 3, 5 and 7** — the opening, the demonstration, the numbers and the weak points are
asked of whoever is standing there.

| Member | Answers questions on |
|---|---|
| Neon Neupane | The engineering: architecture, endpoints, extraction and OCR, preprocessing, the speed work, error handling, and the Nepali handling |
| Bishal Acharya | The model: Sentence-BERT, fine-tuning, the loss, the corpora, the TF-IDF baseline, the accuracy figures and the domain shift |
| Nabin Giri | The frontend: the React application, how it calls the API, the uploader, the matrix, the highlight views and the controls |
| All three | The pitch, the live demonstration, the numbers table and the limitations |

---

## 1. The project in sixty seconds  ·  studied by **All three**

> The tools students can reach today either cost money or compare words. A word
> comparison is defeated by changing a few words. Our system compares the **meaning** of
> sentences instead, using a Sentence-BERT model we fine-tuned ourselves, so a paraphrase
> is still caught. It does two checks — documents against each other, and one document
> against the web — and it marks the copied sentences inside the document so the result
> can be verified by eye rather than trusted.

If you say nothing else, say that.

---

## 2. The one demonstration that proves the project  ·  studied by **All three**

Everything rests on a single comparison. Rehearse it until it is automatic.

| | TF-IDF baseline | SBERT fine-tuned |
|---|---|---|
| `doc1_original` vs `doc2_paraphrased` | **0.468** — missed | **0.668** — caught, 25% copied |
| `doc1_original` vs `doc3_unrelated` | 0.000 | 0.006 |
| `doc1_original` vs `doc4_nepali` | 0.000 | -0.018 |

Show the baseline **fail first**, then switch the engine. The contrast is the argument.

---

## 3. Numbers to know by heart  ·  studied by **All three**

| Question | Answer |
|---|---|
| Base model | `all-MiniLM-L6-v2`, 6 layers, 384 dimensions |
| Fine-tuned on | Quora Question Pairs, 30,000 pairs, 1 epoch |
| Loss | `CosineSimilarityLoss` |
| Threshold | 0.7, adjustable 0.40–0.95 in the interface |
| Chunk size | 5 sentences |
| Batch size | 32 |
| Accuracy (QQP, 2000 pairs) | TF-IDF 0.667 · pretrained 0.743 · **fine-tuned 0.826** |
| F1 | TF-IDF 0.347 · pretrained 0.715 · **fine-tuned 0.746** |
| Separation | TF-IDF 0.203 · pretrained 0.310 · **fine-tuned 0.448** |
| Speed-up | 27.1 s → 5.3 s = **5.1×** on 10 documents |
| Endpoints | `/api/health/`, `/api/compare/`, `/api/check-web/` |
| Ports | Django 8000, Vite 5173 |

---

## 4. Questions you should expect  ·  studied by **All three**

### About the model  ·  studied by **Bishal**

**How does the system decide a sentence is copied?**
Both sentences are turned into 384-dimensional vectors by Sentence-BERT. We take the
cosine of the angle between them. At or above 0.7 the sentence is marked copied. The
threshold was fixed experimentally on the sample documents and is adjustable in the
interface.

**Why Sentence-BERT and not TF-IDF?**
TF-IDF compares words. A paraphrase shares few words, so it scores low — 0.468 on our
paraphrased pair, under the threshold, missed. Sentence-BERT compares meaning and scores
the same pair 0.668. We kept TF-IDF in the system as a selectable baseline so the
difference can be shown, not just claimed.

**What did fine-tuning actually improve?**
Separation. The pretrained model scores everything high — it averages 0.556 even on
unrelated pairs — so no single threshold separates them cleanly. After fine-tuning,
unrelated pairs fall to 0.331 while plagiarised pairs stay at 0.779. The gap goes from
0.310 to 0.448, and accuracy from 0.743 to 0.826.

**Why `CosineSimilarityLoss`?**
It pushes the cosine of a similar pair towards 1 and of a dissimilar pair towards 0.
Cosine similarity is exactly what the detector uses at runtime, so the model is trained on
the same quantity it is judged by.

**Why Quora Question Pairs?**
It is large — about 364,000 labelled pairs — it is free, it downloads without a login, and
its label is precisely "do these two mean the same thing", which is the question we ask.
We used 30,000 pairs so training finishes on a laptop CPU.

**A document is longer than the model input. What happens to the rest?**
It is not dropped. `chunk_text()` cuts the document into chunks of five sentences, every
chunk is embedded, and the document vector is the mean of the chunk vectors. Before we did
this the tail of a long document was silently truncated.

**Is the percentage an average of scores?**
No — it is a count. For every sentence of A we take its best match in B; if that score
clears the threshold the sentence counts as copied. The percentage is copied sentences
divided by total sentences. That is why every point of it can be pointed at on screen.

**What is the accuracy?**
0.826 on 2000 held-out QQP pairs at threshold 0.7, with precision 0.754 and F1 0.746,
against 0.667 for the TF-IDF baseline.

**Where is the model weakest?** *(Ask this of yourself before the panel does.)*
On MRPC — a corpus we did not tune on — our fine-tuned model scores 0.669 against the
pretrained model's 0.748. Tuning on QQP moved it towards QQP's notion of a paraphrase.
That is domain shift, and it is in the report as a limitation rather than left out.

### About the engineering  ·  studied by **Neon**

**How do the frontend and backend connect?**
Vite proxies `/api` to Django on port 8000, so the browser makes a same-origin request. CORS
is also enabled with `CorsMiddleware` for direct cross-origin calls. `api.js` is the only
frontend file that talks to the backend, and it uses the relative base `/api`, so the same
build works either way.

**Why is there no login?**
Nothing is stored. The file is read into memory, compared, and dropped when the response is
sent. There is no account and no saved document, so there is nothing to protect. DRF is
configured with no authentication classes and `AllowAny`.

**Then why is a database configured?**
Django requires the setting. We never write to it — this is shown explicitly in the level 1
data flow diagram, which has no data store.

**Why is a service layer separate from the views?**
The view only parses the request, calls a service and returns JSON. That keeps the
similarity logic testable without starting Django, which is what the tests under
`backend/tests/` do, and it means a new engine or format is a change in one file.

**How was it made faster?**
Two changes. All chunks of all documents now go into one batched `model.encode()` call, so
the model is entered once per request instead of once per document. And a sentence cache
means a sentence appearing in many pairs of the matrix is encoded once. Together: 27.1 s
to 5.3 s on ten documents, a 5.1× speed-up with identical output.

**What happens when a file cannot be read?**
It stays in the response under `skipped`, with the reason. The comparison runs on the rest
and the interface shows an amber panel naming the file. Extraction failures leave as
`ValueError` with a message written for the user, so the API never returns a 500 for a bad
upload.

**What if the network fails during the web check?**
Every network call is wrapped. A search failure returns an empty list, a page that will not
load is skipped, and the request still answers. Explicit URLs can be passed instead of
searching.

**Why does a page with a high score sometimes not appear in the web results?**
Because it shares no sentence. A high document-level score with zero copied sentences is
topical overlap, not plagiarism, so we drop it deliberately.

### About Nepali  ·  studied by **Neon**

**How is Nepali handled?**
Three places. The sentence splitter treats the danda `।` and double danda `॥` as sentence
ends. The tokeniser's character class covers the Devanagari block and the stopword list
includes common Nepali function words. And Tesseract is given `eng+nep` when the Nepali
traineddata is installed, detected at runtime.

**Is Nepali as accurate as English?**
No. The model was fine-tuned on English pairs, so Nepali accuracy is lower. We chose to
write that in the report as a limitation instead of hiding it, and fine-tuning on a Nepali
paraphrase corpus is the first item of future work.

---

## 5. Demo script  ·  studied by **All three**

Have both servers running and `curl http://localhost:8000/api/health/` returning
`model_fine_tuned: true` **before** you begin.

| # | Action | Say |
|---|---|---|
| 1 | Upload the four samples, engine **TF-IDF**, compare | "This is what a word-based checker does. The paraphrase scores 0.468 — below threshold. It is missed." |
| 2 | Switch to **Sentence-BERT**, compare again | "Same files, meaning-based model. 0.668 — caught, 25% copied." |
| 3 | Open the sentence panel | "The percentage is a count of matched sentences, so you can check it yourself." |
| 4 | Point at the unrelated and Nepali rows | "0.006 and -0.018. It is not flagging everything — it separates." |
| 5 | Drag the threshold to 0.65 | "The threshold is a policy choice, sent with each request, not a constant." |
| 6 | **Check against web** tab, paste a paragraph, run | "Sources come back scored and sorted, with links. Pages sharing no sentence are dropped." |
| 7 | Upload a corrupt file with two good ones | "The bad file is named with its reason and the rest still compares. Nothing crashes." |

Close on the point you opened with: a paraphrase defeats a word checker and does not defeat
this one.

---

## 6. If the demo breaks  ·  studied by **All three**

| Symptom | Fix on the spot |
|---|---|
| `model_fine_tuned: false` | Say the checkpoint is not loaded and that the numbers shown are the pretrained model's; the comparison still works |
| Web check returns nothing | The endpoint is rate-limited; pass explicit URLs, the API accepts a `urls` list |
| First request hangs a few seconds | The model is loading — it is a singleton, the next request is fast |
| Scan returns no text | Tesseract missing or the scan is poor; switch to a text file |
| Nepali OCR is gibberish | The `nep` traineddata is not installed on this machine |

Never debug silently in front of the panel. Say what is happening and move to the next step.

---

## 7. Weak points — own them before they are found  ·  studied by **All three**

- **Nepali accuracy is lower than English.** Fine-tuned on English pairs.
- **The fine-tuned model loses on MRPC.** Domain shift from QQP.
- **Sentence splitting is regex-based.** "Dr." can split a sentence early.
- **The web check depends on one search endpoint.** No API key, so rate limits apply.
- **No queue.** A very large batch occupies the request; comparison is in-process.

Each of these is in the report with the reason. Stating a limitation before it is found
reads as understanding the system; being caught by it does not.
