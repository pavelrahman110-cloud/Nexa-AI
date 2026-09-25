"""Reusable page-aware PDF document service for Nexa."""
from __future__ import annotations

from pathlib import Path

from actions.document_engine import (
    extract_document_pages,
    extract_pdf_pages,
    find_questions,
    find_repeated_questions,
    resolve_pdf_path,
    _search_pages,
)


class DocumentEngine:
    def __init__(self):
        self.active_documents: dict[str, dict] = {}

    def process_file(self, file_path: str, ocr: bool = True) -> dict:
        path = resolve_pdf_path(file_path) or Path(file_path)
        if not path.exists():
            return {"error": "File does not exist."}

        if path.suffix.lower() == ".pdf":
            try:
                metadata, pages = extract_document_pages(path, ocr=ocr)
                doc_info = {
                    "type": "pdf",
                    **metadata,
                    "pages": pages,
                    "is_scanned": metadata["text_pages"] == 0,
                }
                self.active_documents[path.name] = doc_info
                return doc_info
            except Exception as exc:
                return {"error": f"{type(exc).__name__}: {exc}"}

        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            doc_info = {"type": "image", "name": path.name, "path": str(path)}
            self.active_documents[path.name] = doc_info
            return doc_info

        return {"error": f"Unsupported document type: {path.suffix}"}

    def search(self, file_path: str, query: str, **kwargs) -> str:
        doc = self.process_file(file_path, ocr=kwargs.pop("ocr", True))
        if "error" in doc:
            return doc["error"]
        return _search_pages(
            doc["pages"],
            query,
            max_results=kwargs.get("max_results", 5),
            max_chars=kwargs.get("max_chars", 28000),
        )

    def repeated_questions(self, file_path: str, **kwargs) -> str:
        doc = self.process_file(file_path, ocr=kwargs.pop("ocr", True))
        if "error" in doc:
            return doc["error"]
        return find_repeated_questions(
            doc["pages"], max_results=kwargs.get("max_results", 30)
        )

    def question(
        self,
        file_path: str,
        question_number: int | None = None,
        year: int | None = None,
        **kwargs,
    ) -> str:
        doc = self.process_file(file_path, ocr=kwargs.pop("ocr", True))
        if "error" in doc:
            return doc["error"]
        return find_questions(
            doc["pages"],
            question_number=question_number,
            year=year,
            max_results=kwargs.get("max_results", 10),
        )


DOC_ENGINE = DocumentEngine()