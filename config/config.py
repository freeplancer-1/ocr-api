import os

import google.generativeai as genai


def configure(api_key: str = None):
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Bạn cần truyền GEMINI_API_KEY hoặc cài đặt biến môi trường tương ứng.")
    genai.configure(api_key=key)


def get_model(name: str = "gemini-2.0-flash"):
    return genai.GenerativeModel(name)
