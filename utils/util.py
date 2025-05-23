import json
import re

from rapidfuzz import process, fuzz

CATALOG = [
    "GVS BLESS YOU H.M/ALAVIE CUON×20",
]

def correct_name(scanned: str) -> str:
    match, score, _ = process.extractOne(
        scanned,
        CATALOG,
        scorer=fuzz.WRatio,
        processor=lambda x: x
    )
    return match if score > 80 else scanned


def parse_gemini_output(raw_text: str) -> dict:
    m = re.search(r'(\{.*\})', raw_text, re.DOTALL)
    if not m:
        raise ValueError("Không tìm thấy JSON trong đầu ra của Gemini")
    return json.loads(m.group(1))
