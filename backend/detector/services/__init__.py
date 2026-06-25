"""Service layer: all business logic lives here.

Each module has a single responsibility so the code stays easy to read and test:
  text_extraction  -> uploaded file  -> plain text
  preprocess       -> plain text     -> cleaned text / sentences
  similarity       -> texts          -> similarity scores (TF-IDF baseline + SBERT)
  highlighter      -> two texts      -> matched sentences + % copied
  web_scraper      -> one text       -> similarity vs web pages
"""
