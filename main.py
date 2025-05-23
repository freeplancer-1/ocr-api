import os
from typing import List

import aiofiles
import aiofiles.os as aios

import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.api_core import retry

from prompts.prompts import gemini_prompt
from utils.util import parse_gemini_output

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
request_opts = {
    'retry': retry.Retry(initial=1, multiplier=2, maximum=60, deadline=300)
}

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


@api_router.post("/upload-image")
async def upload_image(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Chưa upload file nào")

    for f in files:
        if not f.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Chỉ cho phép upload file hình ảnh")

    if len(files) == 1:
        contents = [gemini_prompt, Image.open(files[0].file)]
    else:
        saved_paths = [await save_file(f) for f in files]
        file_refs = [genai.upload_file(path) for path in saved_paths]
        contents = [gemini_prompt, *file_refs]

    response = model.generate_content(
        contents=contents,
        request_options=request_opts
    )

    if len(files) > 1:
        await remove_all_files_async()

    return JSONResponse(
        status_code=200,
        content={"data": parse_gemini_output(response.text)}
    )


async def remove_all_files_async(folder_path: str = "images") -> None:
    names = await aios.listdir(folder_path)
    for name in names:
        path = os.path.join(folder_path, name)
        try:
            await aios.remove(path)
        except Exception as e:
            print(f"Failed to delete {path}: {e}")


async def save_file(fileUpload: UploadFile = File(...)):
    os.makedirs("images", exist_ok=True)

    save_path = os.path.join("images", fileUpload.filename)

    await fileUpload.seek(0)

    async with aiofiles.open(save_path, "wb") as out_file:
        while chunk := await fileUpload.read(1024):
            await out_file.write(chunk)

    await fileUpload.close()
    return save_path


app.include_router(api_router)
