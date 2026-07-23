# Demo sample documents

Upload all three at once to see the detector in action:

- **doc1_original.txt** and **doc2_paraphrased.txt** say the same thing about photosynthesis
  in different words → they should light up **red** in the matrix (high % copied). This proves
  the model catches *paraphrasing*, not just exact copies.
- **doc3_unrelated.txt** is about the French Revolution → it should stay **green** (low similarity).

Expected result: the pair **doc1 vs doc2** is flagged with a high "% copied" score, while
doc3 matches neither.
