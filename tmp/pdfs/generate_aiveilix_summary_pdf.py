from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph


PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_X = 15 * mm
MARGIN_TOP = 14 * mm
MARGIN_BOTTOM = 12 * mm
GUTTER = 6 * mm
HEADER_H = 29 * mm
CARD_PAD_X = 5 * mm
CARD_PAD_TOP = 4.5 * mm
CARD_PAD_BOTTOM = 4 * mm

CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN_X)
COLUMN_W = (CONTENT_WIDTH - GUTTER) / 2
COL1_X = MARGIN_X
COL2_X = MARGIN_X + COLUMN_W + GUTTER
BODY_TOP = PAGE_HEIGHT - MARGIN_TOP - HEADER_H - 4 * mm

OUT_PATH = Path("/Volumes/KIOXIA/AIveilix/output/pdf/aiveilix-app-summary.pdf")


def build_styles():
    styles = getSampleStyleSheet()
    return {
        "eyebrow": ParagraphStyle(
            "Eyebrow",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.8,
            leading=9,
            textColor=colors.HexColor("#BFDBFE"),
            spaceAfter=0,
        ),
        "title": ParagraphStyle(
            "Title",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=22,
            textColor=colors.white,
            alignment=TA_LEFT,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=11,
            textColor=colors.HexColor("#DBEAFE"),
        ),
        "section": ParagraphStyle(
            "Section",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.1,
            leading=9,
            textColor=colors.HexColor("#0F172A"),
        ),
        "body": ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.7,
            leading=10.4,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=0,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.55,
            leading=10.1,
            leftIndent=9,
            firstLineIndent=0,
            bulletIndent=0,
            textColor=colors.HexColor("#0F172A"),
        ),
        "step": ParagraphStyle(
            "Step",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.35,
            leading=9.85,
            leftIndent=11,
            firstLineIndent=0,
            bulletIndent=0,
            textColor=colors.HexColor("#0F172A"),
        ),
        "note": ParagraphStyle(
            "Note",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.7,
            leading=9.2,
            textColor=colors.HexColor("#334155"),
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.6,
            leading=8.8,
            textColor=colors.HexColor("#64748B"),
        ),
    }


WHAT_IT_IS = (
    "Aiveilix is a bucket-based document platform for persistent AI knowledge. "
    "The repo shows a React frontend and FastAPI backend that upload files, process "
    "them into searchable layouts and embeddings, and answer bucket questions with sourced results."
)

WHO_ITS_FOR = (
    "Primary persona: developers and knowledge-heavy professionals who want a persistent, "
    "AI-queryable document bucket instead of re-uploading context every session."
)

FEATURES = [
    "Email/password auth plus Google, GitHub, JWT refresh, password reset, and 2FA endpoints.",
    "Bucket creation, update, deletion, and per-bucket conversations from the dashboard API.",
    "Multi-file upload to a bucket with background processing, retry support, and file event traces.",
    "Layout JSON and chunk inspection endpoints for processed files.",
    "Hybrid bucket search over indexed chunks with page-level source metadata.",
    "Bucket chat that combines bucket retrieval, conversation memory, optional web search, and multi-provider LLM answering.",
]

HOW_IT_WORKS = [
    "Frontend: React 18 + Vite + Tailwind in `frontend/`; API base comes from `VITE_API_URL`.",
    "API: FastAPI app in `backend/app/main.py` mounts `/v1` routers for auth, buckets, files, search, conversations, notifications, billing, and MCP.",
    "Upload path: file upload -> Cloudflare R2 raw storage + PostgreSQL file row -> background `process_file(...)` task.",
    "Processing path: Docling extracts structure, Gemini describes image blocks, `layout_builder` merges both into Layout JSON and saves it back to R2.",
    "Index path: `chunker` splits layout content, BGE-M3 and CLIP create vectors, and Qdrant stores searchable chunk/image data while PostgreSQL tracks file state.",
    "Query path: question embedding -> Qdrant dense/hybrid retrieval -> optional DuckDuckGo web results -> selected LLM provider -> answer with sources.",
]

RUN_STEPS = [
    "Copy `backend/.env.example` to `.env` or use the repo root `.env`; set required database, R2, and API-key values.",
    "From repo root, start local services with the provided scripts: PostgreSQL (`backend/database/postgres/...`), embedded Qdrant (`backend/database/qdrant/...`), and Valkey (`backend/database/valkey/...`).",
    "Backend: `cd backend`, create a venv, install `requirements.txt`, then run `python run.py`.",
    "Frontend: `cd frontend`, run `npm install`, then `npm run dev`. `frontend/.env` points the UI to `http://localhost:4565`.",
]

NOTES = [
    "MCP bucket/account handlers and bucket MCP URL actions: Not found in repo (stubbed endpoints).",
    "Billing actions and notification delete endpoint: Not found in repo (stubbed endpoints).",
]

EVIDENCE = (
    "Evidence: repo docs in `docs/`, frontend config/API files, backend requirements, and backend app/router/service code."
)


def draw_paragraph(canvas, text, style, x, top_y, width, bullet=None):
    paragraph = Paragraph(text, style, bulletText=bullet)
    _, height = paragraph.wrap(width, 1000)
    paragraph.drawOn(canvas, x, top_y - height)
    return top_y - height


def section_height(title, body_texts, styles, width, bullets=False):
    total = CARD_PAD_TOP + CARD_PAD_BOTTOM + 6
    header = Paragraph(title, styles["section"])
    _, header_h = header.wrap(width - (2 * CARD_PAD_X), 1000)
    total += header_h + 4

    style_name = "bullet" if bullets else "body"
    bullet_token = "\u2022" if bullets else None
    for text in body_texts:
        paragraph = Paragraph(text, styles[style_name], bulletText=bullet_token)
        _, para_h = paragraph.wrap(width - (2 * CARD_PAD_X), 1000)
        total += para_h + 2
    return total


def draw_section(canvas, x, top_y, width, title, body_texts, styles, *, bullets=False, accent="#1D4ED8"):
    height = section_height(title, body_texts, styles, width, bullets=bullets)
    bottom_y = top_y - height
    canvas.setFillColor(colors.white)
    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.roundRect(x, bottom_y, width, height, 9, stroke=1, fill=1)

    canvas.setFillColor(colors.HexColor(accent))
    canvas.roundRect(x, top_y - 15, width, 15, 9, stroke=0, fill=1)
    canvas.rect(x, top_y - 15, width, 7, stroke=0, fill=1)

    text_top = top_y - CARD_PAD_TOP
    text_top = draw_paragraph(canvas, title, styles["section"], x + CARD_PAD_X, text_top, width - (2 * CARD_PAD_X))
    text_top -= 4
    for text in body_texts:
        text_top = draw_paragraph(
            canvas,
            text,
            styles["bullet" if bullets else "body"],
            x + CARD_PAD_X,
            text_top,
            width - (2 * CARD_PAD_X),
            bullet="\u2022" if bullets else None,
        )
        text_top -= 2
    return bottom_y


def generate_pdf():
    from reportlab.pdfgen import canvas

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    styles = build_styles()
    c = canvas.Canvas(str(OUT_PATH), pagesize=A4)
    c.setTitle("Aiveilix App Summary")
    c.setAuthor("OpenAI Codex")

    # Background
    c.setFillColor(colors.HexColor("#F8FAFC"))
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    # Header
    header_y = PAGE_HEIGHT - MARGIN_TOP
    c.setFillColor(colors.HexColor("#0F172A"))
    c.roundRect(MARGIN_X, header_y - HEADER_H, CONTENT_WIDTH, HEADER_H, 12, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#1D4ED8"))
    c.circle(MARGIN_X + 12 * mm, header_y - 10 * mm, 9 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(MARGIN_X + 12 * mm, header_y - 10.9 * mm, "AI")

    header_text_x = MARGIN_X + 27 * mm
    title_top = header_y - 6.5 * mm
    title_top = draw_paragraph(c, "APP SUMMARY", styles["eyebrow"], header_text_x, title_top, CONTENT_WIDTH - 34 * mm)
    title_top -= 1
    title_top = draw_paragraph(c, "Aiveilix", styles["title"], header_text_x, title_top, CONTENT_WIDTH - 34 * mm)
    title_top -= 1
    draw_paragraph(
        c,
        "One-page repo-grounded snapshot of product scope, architecture, and local startup path.",
        styles["subtitle"],
        header_text_x,
        title_top,
        CONTENT_WIDTH - 34 * mm,
    )

    # Left column
    left_y = BODY_TOP
    left_y = draw_section(c, COL1_X, left_y, COLUMN_W, "What It Is", [WHAT_IT_IS], styles, bullets=False, accent="#2563EB")
    left_y -= 8
    left_y = draw_section(c, COL1_X, left_y, COLUMN_W, "Who It's For", [WHO_ITS_FOR], styles, bullets=False, accent="#0F766E")
    left_y -= 8
    left_y = draw_section(c, COL1_X, left_y, COLUMN_W, "What It Does", FEATURES, styles, bullets=True, accent="#7C3AED")

    # Right column
    right_y = BODY_TOP
    right_y = draw_section(c, COL2_X, right_y, COLUMN_W, "How It Works", HOW_IT_WORKS, styles, bullets=True, accent="#EA580C")
    right_y -= 8
    right_y = draw_section(c, COL2_X, right_y, COLUMN_W, "How to Run", RUN_STEPS, styles, bullets=True, accent="#059669")
    right_y -= 8
    right_y = draw_section(c, COL2_X, right_y, COLUMN_W, "Repo Gaps", NOTES, styles, bullets=True, accent="#DC2626")

    # Footer
    footer_y = MARGIN_BOTTOM + 3
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.line(MARGIN_X, footer_y + 10, PAGE_WIDTH - MARGIN_X, footer_y + 10)
    draw_paragraph(c, EVIDENCE, styles["footer"], MARGIN_X, footer_y + 8, CONTENT_WIDTH)

    c.showPage()
    c.save()


if __name__ == "__main__":
    generate_pdf()
