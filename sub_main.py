import json
import re
from PIL import Image
import google.generativeai as genai
from rapidfuzz import process, fuzz

gemini_prompt = """
You are a precise OCR and invoice table extractor.

Inputs:
- image: URL or Base64 of the invoice image.
- currency: currency symbol or code (e.g. "₫", "VND").

Instructions:
1. Run OCR on the provided image with high accuracy.
2. Identify the product table and extract each row into JSON objects with:
   - code (string)
   - name (string)
   - unit_price (number)
   - quantity (integer)
   - total_price (number)
3. After extraction, apply simple normalization:
   - Trim whitespace
   - Replace common OCR errors (e.g., U → V in product codes)
4. Compute summary fields:
   - total_quantity: sum of all quantities
   - subtotal: sum of (unit_price × quantity)
   - tax_amount (if present on invoice)
   - grand_total
5. Respond with a single JSON object containing:
{
  "items": [ /* array of row-objects */ ],
  "total_quantity":  /* integer */,
  "subtotal":        /* number */,
  "tax_amount":      /* number or null */,
  "grand_total":     /* number */
}

Output strictly as JSON, no additional text.
"""


# load_dotenv()
# api_key = os.getenv("")

# Cấu hình Gemini API
genai.configure(api_key="AIzaSyCAFTn17y-E2tAFaRdROKe1qN-FTSoKCuA")

model = genai.GenerativeModel("gemini-2.0-flash")

image_path = "/Users/quangtin/Desktop/ocr-preview/images/edae1624cee0639f_1739589984932999.jpg"

# Mở hình ảnh
with Image.open(image_path) as img:
    print("Result: ", img)
    response = model.generate_content(
        contents=[gemini_prompt, img]
    )

catalog = [
    "GVS BLESS YOU H.M/ALAVIE CUON×20",
]

def correct_name(scanned: str) -> str:
    match, score, _ = process.extractOne(
        scanned,
        catalog,
        scorer=fuzz.token_sort_ratio
    )

    return match if score > 80 else scanned

def parse_gemini_output(raw_text: str) -> dict:
    match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
    if not match:
        raise ValueError("Không tìm thấy JSON trong đầu ra của Gemini")
    json_str = match.group(1)

    return json.loads(json_str)

print(response.text)
json_data = parse_gemini_output(response.text)
text = correct_name(json_data["items"][1]["name"])
print(json_data)