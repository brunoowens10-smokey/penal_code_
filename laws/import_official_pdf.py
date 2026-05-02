import os
import re
import sys
from pathlib import Path

from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "Offences_and_penalties_in_general_2018.pdf"

sys.path.append(str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "penal_code.settings")

import django

django.setup()

from laws.models import Article

LANGUAGES = {
    "rw": {
        "field": "content_rw",
        "x_min": 80,
        "x_max": 315,
        "regex": re.compile(r"Ingingo\s*ya\s*(mbere|\d{1,3})(.*)$", re.IGNORECASE),
        "label": "Ingingo ya",
    },
    "en": {
        "field": "content_en",
        "x_min": 315,
        "x_max": 545,
        "regex": re.compile(r"Article\s*(One|\d{1,3})(.*)$", re.IGNORECASE),
        "label": "Article",
    },
    "fr": {
        "field": "content_fr",
        "x_min": 500,
        "x_max": 805,
        "regex": re.compile(r"Article\s*(premier|\d{1,3})(.*)$", re.IGNORECASE),
        "label": "Article",
    },
}


def normalize_number(value):
    lowered = value.lower()
    if lowered in {"one", "premier", "mbere"}:
        return "1"
    return str(int(value))


def clean_line(line):
    line = re.sub(r"\s+", " ", line).strip()
    replacements = {
        "Rwandaregistered": "Rwanda-registered",
        "donot": "do not",
        "isnot": "is not",
        "doesnot": "does not",
        "cyangwauri": "cyangwa uri",
        "nibihano": "n'ibihano",
        "nest": "n'est",
        "quune": "qu'une",
    }
    for old, new in replacements.items():
        line = line.replace(old, new)
    return line


def column_lines(page, x_min, x_max):
    parts = []

    def visitor(text, cm, tm, font_dict, font_size):
        if not text.strip():
            return
        x = tm[4]
        y = tm[5]
        if x_min <= x < x_max and 65 < y < 535:
            parts.append((round(y, 1), x, text))

    page.extract_text(visitor_text=visitor)
    lines = []
    for y in sorted({item[0] for item in parts}, reverse=True):
        row_parts = [item for item in parts if item[0] == y]
        row = "".join(text for _, _, text in sorted(row_parts, key=lambda item: item[1]))
        row = clean_line(row)
        if row:
            lines.append(row)
    return lines


def extract_articles(pdf_path, config):
    reader = PdfReader(str(pdf_path))
    extracted = {}
    current_number = None
    current_lines = []
    expected = 1

    for page in reader.pages[43:]:
        for line in column_lines(page, config["x_min"], config["x_max"]):
            match = config["regex"].search(line)
            if match:
                number = normalize_number(match.group(1))
                if number != str(expected) and str(expected).startswith(number):
                    number = str(expected)
                if int(number) >= expected and int(number) <= expected + 5:
                    if current_number and current_lines:
                        extracted[current_number] = "\n".join(current_lines).strip()
                    suffix = clean_line(match.group(2))
                    current_number = number
                    current_lines = [clean_line(f"{config['label']} {number}{suffix}")]
                    expected = int(number) + 1
                    continue
            if current_number:
                current_lines.append(line)

    if current_number and current_lines:
        extracted[current_number] = "\n".join(current_lines).strip()

    return extracted


def run():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Missing official PDF: {PDF_PATH}")

    totals = {}
    missing_by_lang = {}
    extracted_by_lang = {lang: extract_articles(PDF_PATH, config) for lang, config in LANGUAGES.items()}

    for lang, config in LANGUAGES.items():
        updated = 0
        missing = []
        field = config["field"]
        extracted = extracted_by_lang[lang]

        for article in Article.objects.order_by("id"):
            text = extracted.get(article.number)
            if not text:
                missing.append(article.number)
                continue
            setattr(article, field, text)
            article.save(update_fields=[field])
            updated += 1

        totals[lang] = updated
        missing_by_lang[lang] = missing

    for lang, updated in totals.items():
        print(f"Updated {updated} {lang} articles.")
        if missing_by_lang[lang]:
            print(f"Missing {lang} article text for: {', '.join(missing_by_lang[lang])}")


if __name__ == "__main__":
    run()
