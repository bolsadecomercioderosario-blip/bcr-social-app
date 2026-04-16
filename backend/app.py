from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import shutil
import uuid
from typing import Optional

from processor import extract_pdf_data, generate_pdf_thumbnail, create_ig_mockup, to_bold_serif

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
@app.post("/api/pre-procesar")
async def pre_procesar(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    pdf_path = os.path.join(STATIC_DIR, f"{session_id}_pre.pdf")
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        data = extract_pdf_data(pdf_path)
        # Generar una miniatura para la vista previa en el paso 2
        thumb_filename = f"pre_{session_id}.jpg"
        thumb_path = os.path.join(STATIC_DIR, thumb_filename)
        generate_pdf_thumbnail(pdf_path, thumb_path)
        
        return {
            "session_id": session_id, 
            "title": data["title"], 
            "pdf_path": pdf_path,
            "preview_url": f"/static/{thumb_filename}"
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/generar")
async def generar_piezas(
    session_id: str = Form(...),
    pdf_path: str = Form(...),
    title: str = Form(...)
):
    try:
        data = extract_pdf_data(pdf_path)
        data["title"] = title
        
        twitter_text = f"{to_bold_serif(data['title'])}\n\n{data['intro']}"
        
        thumb_filename = f"comunicado_{session_id}.jpg"
        thumb_path = os.path.join(STATIC_DIR, thumb_filename)
        generate_pdf_thumbnail(pdf_path, thumb_path)
        
        story_filename = f"story_instagram_{session_id}.jpg"
        story_path = os.path.join(STATIC_DIR, story_filename)
        create_ig_mockup(data, thumb_path, ASSETS_DIR, story_path)
        
        return {
            "twitter_text": twitter_text,
            "comunicado_url": f"/api/descargar/{thumb_filename}?name=comunicado.jpg",
            "story_url": f"/api/descargar/{story_filename}?name=story_instagram.jpg",
            "comunicado_img": f"/static/{thumb_filename}",
            "story_img": f"/static/{story_filename}"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/descargar/{filename}")
async def descargar(filename: str, name: str):
    file_path = os.path.join(STATIC_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=name, media_type='image/jpeg')
    return {"error": "Archivo no encontrado"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
