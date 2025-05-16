import os
from typing import Union

from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import google.generativeai as genai
from google.api_core import retry

from prompts.prompts import gemini_prompt
from utils.util import parse_gemini_output

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

app = FastAPI()

api_router = APIRouter(prefix="/api")

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api_router.get("/")
def read_root():
    return {"Hello": "World"}


@api_router.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@api_router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Chỉ cho phép upload file hình ảnh")

    image = Image.open(file.file)
    response = model.generate_content(
        contents=[gemini_prompt, image],
        request_options={
            'retry': retry.Retry(
                initial=1,
                multiplier=2,
                maximum=60,
                deadline=300
            )
        }
    )

    return JSONResponse(
        status_code=200,
        content={
            "data": parse_gemini_output(response.text)
        },
    )


app.include_router(api_router)
