# Demo sample documents

Upload all four at once. Scores below are what the fine-tuned model actually returns.

| Pair | Score | At the 0.70 default |
|---|---|---|
| **doc1_original** vs **doc2_paraphrased** | 0.6676 | **not flagged** |
| doc1_original vs doc3_unrelated | 0.0062 | not flagged |
| doc2_paraphrased vs doc3_unrelated | 0.0967 | not flagged |
| doc1_original vs doc4_nepali | -0.0181 | not flagged |

- **doc1_original** and **doc2_paraphrased** say the same thing about photosynthesis in
  almost entirely different words. The model puts them at **0.6676**, which is close to
  the default threshold but under it, so the pair is reported as similar without being
  flagged. Move the threshold to **0.50** and it flags at **75 % copied**, with the
  reworded sentences marked. The word-based TF-IDF baseline scores the same pair at
  0.4676. At the 0.70 default, one of the four sentences still clears the bar on its own.
- **doc3_unrelated** is about the French Revolution and **doc4_nepali** is in Devanagari.
  Both sit near zero against everything, which is the behaviour you want.

Four short sentences rewritten end to end is the hardest case for the model, which is
why this pair lands where it does. For a demo where the pair flags at the default
threshold, use `tests/en_01_original.txt` with `tests/en_03_near_copy.txt` (0.9835), and
keep this set for showing what the threshold control is for.
