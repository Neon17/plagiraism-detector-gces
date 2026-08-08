# User Manual — Plagiarism Detector

For the person using the system. For setup and code details see [GUIDE.md](../GUIDE.md).

---

## 1. What the system does

- Compares a batch of documents against each other and shows who copied from whom.
- Compares one document against public web pages.
- Marks the copied sentences inside the document and shows a percentage.

Nothing is stored. The uploaded file is read in memory, used for the comparison and
dropped as soon as the answer is sent back.

---

## 2. Files you can upload

| Type | Extensions | Notes |
|---|---|---|
| Text | `.txt`, `.md` | Read directly |
| Word | `.docx` | Paragraph text only |
| PDF | `.pdf` | Scanned PDFs go through OCR automatically |
| Image | `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff` | Read with Tesseract OCR |

English and Nepali (Devanagari) are both accepted. Nepali OCR needs the `nep`
traineddata installed; without it the scan is read as English.

---

## 3. Comparing documents against each other

1. Open the **Compare documents** tab.
2. Drag at least two files onto the upload box, or click it and pick them.
3. Choose the settings if you want to change them:
   - **Engine** — *Sentence-BERT* catches paraphrasing, *TF-IDF* only catches repeated
     words. Sentence-BERT is the default.
   - **Threshold** — how close two sentences must be before they count as copied. The
     default is 0.70.
4. Press **Compare**. Large batches take longer; the button shows the progress state.
5. Read the result:
   - **Similarity matrix** — every document against every other one.
   - **Legend** — what the colours and the score bands mean.
   - **Highlights** — each flagged pair with its copied sentences marked.

---

## 4. Checking a document against the web

1. Open the **Check against web** tab.
2. Paste the text or upload one file.
3. Optionally paste specific URLs to check against. Leave it empty to let the system
   search for the pages itself.
4. Press **Check**. The result lists each page with its link, its score and the
   sentences that also appear in your document.

A page that cannot be opened is skipped, and the rest of the check continues.

---

## 5. Reading the score

| Score | Meaning |
|---|---|
| Below 0.40 | Unrelated documents |
| 0.40 – 0.70 | Same topic, worth reading before deciding |
| Above 0.70 | Flagged as copied |

The score is the similarity between the meanings of the sentences, not the number of
matching words. Two sentences that say the same thing in different words still score
high. The system reports a similarity, so the final judgement stays with the teacher.

---

## 6. Messages you may see

| Message | What to do |
|---|---|
| Upload at least 2 readable documents | One of the files gave no text; check the skipped list below the result |
| The file is empty | The file has no content |
| Unsupported file type | Convert it to one of the formats in section 2 |
| No text could be read | The scan is too poor; rescan it or use a clearer image |
| Request failed | The backend is not running, or the network is down |

---

## 7. Limitations

- Nepali accuracy is lower than English accuracy.
- The web check depends on the search results being reachable at that moment.
- A low quality scan gives poor OCR output, and the comparison is only as good as the
  text that was read.
- Source code and mathematical notation are not handled.
