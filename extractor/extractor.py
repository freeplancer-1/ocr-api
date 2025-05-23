from PIL import Image

from prompts.prompts import gemini_prompt


def extract_invoice(model, image_path: str) -> str:
    with Image.open(image_path) as img:
        response = model.generate_content(contents=[gemini_prompt, img])
    return response.text
