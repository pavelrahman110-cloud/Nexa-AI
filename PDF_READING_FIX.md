# Nexa PDF reading fix

Replace these files in the original project:

- `actions/document_engine.py`
- `actions/file_processor.py`
- `core/document_engine.py`
- `core/prompt.txt`
- `requirements.txt`

What changed:

- The complete PDF is indexed page-by-page instead of reading only the first 3 pages.
- Search results are ranked across all pages.
- `mode="read_pages"` reads a selected page range.
- PDF and image files (`png`, `jpg`, `jpeg`, `webp`, `bmp`, `tif`, `tiff`) use
  the same OCR/document pipeline.
- `mode="question"` finds a numbered question by page and/or year.
- `mode="repeated"` finds repeated question groups and reports page numbers.
- `mode="export_questions"` writes all detected questions to a Desktop PDF.
- `mode="export_repeated"` writes repeated/similar question patterns to a Desktop PDF.
- `mode="export_text"` writes the complete extracted document text to a Desktop PDF.
- Image-only pages use optional Tesseract OCR when available.
- The old `file_processor` 8,000-character truncation is removed.
- Generated PDFs use a Bengali-capable system font when one is installed.

Install after replacing the files:

```bash
python -m pip install -r requirements.txt
```

For scanned Bengali PDFs, also install the Tesseract program and its Bengali
language data (`ben`) on the computer. Selectable-text PDFs do not need OCR.

Example tool calls:

```json
{"file_path": "C:/Users/you/Downloads/questions.pdf", "mode": "overview"}
{"file_path": "C:/Users/you/Downloads/questions.pdf", "mode": "repeated"}
{"file_path": "C:/Users/you/Downloads/questions.pdf", "mode": "search", "query": "2023"}
{"file_path": "C:/Users/you/Downloads/questions.pdf", "mode": "read_pages", "page_start": 12, "page_end": 15}
{"file_path": "C:/Users/you/Downloads/questions.pdf", "mode": "question", "page_start": 2, "page_end": 2, "question_number": 2}
{"file_path": "C:/Users/you/Downloads/questions.pdf", "mode": "question", "year": 2021, "question_number": 2}
{"file_path": "C:/Users/you/Downloads/questions.pdf", "mode": "export_questions", "output_name": "all_questions.pdf"}
{"file_path": "C:/Users/you/Downloads/questions.pdf", "mode": "export_repeated", "output_name": "repeated_patterns.pdf"}
```