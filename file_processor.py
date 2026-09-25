import html
import os
from pathlib import Path
import platform
import subprocess

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

try:
    from actions.document_engine import handler as document_handler
except ImportError:
    document_handler = None


_UNICODE_FONT_CANDIDATES = (
    # Windows
    r"C:\Windows\Fonts\Nirmala.ttf",
    r"C:\Windows\Fonts\NirmalaUI.ttf",
    r"C:\Windows\Fonts\vrinda.ttf",
    r"C:\Windows\Fonts\SolaimanLipi.ttf",
    # Linux
    "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansBengali-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    # macOS / user-installed fonts
    str(Path.home() / "Library/Fonts/NotoSansBengali-Regular.ttf"),
    str(Path.home() / ".fonts/NotoSansBengali-Regular.ttf"),
)


def _register_unicode_font() -> tuple[str, bool]:
    """Prefer a Bengali-capable system font for generated PDFs."""
    for raw_path in _UNICODE_FONT_CANDIDATES:
        path = Path(raw_path).expanduser()
        if not path.is_file():
            continue
        try:
            font_name = "NexaUnicode"
            if font_name not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(font_name, str(path)))
                addMapping(font_name, 0, 0, font_name)
            return font_name, True
        except Exception:
            continue
    return "Helvetica", False


def make_pdf(text: str, filename: str) -> tuple[str, bool]:
    desk = Path(os.path.expanduser("~/Desktop"))
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"
    desk.mkdir(parents=True, exist_ok=True)
    out = desk / filename

    font_name, unicode_ready = _register_unicode_font()
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "NexaBody",
        parent=styles["BodyText"],
        fontName=font_name,
        fontSize=11,
        leading=17,
        alignment=TA_LEFT,
        spaceAfter=5,
    )
    document = SimpleDocTemplate(
        str(out),
        pagesize=letter,
        rightMargin=48,
        leftMargin=48,
        topMargin=48,
        bottomMargin=48,
        title="Nexa PDF",
    )
    story = []
    for raw_line in text.splitlines() or [""]:
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 8))
            continue
        safe = html.escape(line).replace("\n", "<br/>")
        story.append(Paragraph(safe, body))
    document.build(story)
    return str(out), unicode_ready


def _resolve_existing(fpath: str):
    target = Path(fpath.strip().strip('"')).expanduser()
    if target.exists():
        return target
    for base in (
        Path.home() / "Desktop",
        Path.home() / "Downloads",
        Path.home() / "Documents",
    ):
        check = base / fpath
        if check.exists():
            return check
        check = base / Path(fpath).name
        if check.exists():
            return check
    return None


def handler(args: dict, ctx: dict = None) -> str:
    act = str(args.get("action", "read") or "read").lower()
    fpath = str(args.get("file_path", "") or "")
    text = str(args.get("content", "") or "")
    out_name = str(args.get("output_name", "solution.pdf") or "solution.pdf")

    if act == "create_pdf":
        if not text.strip():
            return "Error: No content provided to create PDF. Pass the full text in 'content'."
        path, unicode_ready = make_pdf(text, out_name)
        message = f"PDF successfully created and saved on Desktop at: {path}"
        if not unicode_ready:
            message += (
                " Warning: no Bengali-capable font was found; install Nirmala UI "
                "or Noto Sans Bengali to render Bengali text correctly."
            )
        return message

    if act == "open_file":
        target = _resolve_existing(fpath)
        if target is None:
            return f"Error: File '{fpath}' not found on Desktop, Downloads, or Documents."
        try:
            if platform.system() == "Windows":
                os.startfile(str(target))
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", str(target)])
            else:
                subprocess.Popen(["xdg-open", str(target)])
            return f"Opened file: {target.name}"
        except Exception as exc:
            return f"Failed to open file: {exc}"

    if act == "read":
        target = _resolve_existing(fpath)
        if target is None:
            return f"Error: File '{fpath}' not found on Desktop, Downloads, or Documents."
        if target.suffix.lower() not in {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}:
            return f"Error: '{target.name}' is not a supported PDF or image."
        if document_handler is None:
            return "PDF engine is unavailable. Ensure actions/document_engine.py is installed."

        forwarded = dict(args)
        forwarded["file_path"] = str(target)
        forwarded["mode"] = forwarded.get("mode") or (
            "search" if forwarded.get("query") else "overview"
        )
        return document_handler(forwarded, ctx)

    return "Invalid action. Use create_pdf, open_file, or read."


TOOL = {
    "name": "file_processor",
    "handler": handler,
    "description": (
        "Create/open PDFs, or read a PDF page-by-page with search, OCR, "
        "selected-page reading, numbered-question lookup, and repeated-question detection. "
        "For Banglish requests, preserve exact extracted question text when creating "
        "a Desktop PDF."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "create_pdf, open_file, or read"},
            "file_path": {"type": "STRING", "description": "Path or name of the file."},
            "content": {"type": "STRING", "description": "Text for a new PDF."},
            "output_name": {"type": "STRING", "description": "Output PDF filename."},
            "mode": {"type": "STRING", "description": "overview, search, read_pages, question, or repeated"},
            "query": {"type": "STRING", "description": "Text to find in the PDF."},
            "page_start": {"type": "INTEGER"},
            "page_end": {"type": "INTEGER"},
            "question_number": {"type": "INTEGER"},
            "year": {"type": "INTEGER"},
            "max_results": {"type": "INTEGER"},
            "max_chars": {"type": "INTEGER"},
            "ocr": {"type": "BOOLEAN"},
        },
        "required": ["action"],
    },
}