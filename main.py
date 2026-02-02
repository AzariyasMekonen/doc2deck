from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from datetime import datetime
from dotenv import load_dotenv
from bson import ObjectId

from app.auth.models import User, Presentation, get_database
from app.auth.auth import AuthService
from app.pdf.processor import PDFProcessor
from app.ai.service import AIService
from app.ppt.generator import PPTGenerator

load_dotenv()

app = FastAPI(title="Doc2Deck")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
auth_service = AuthService()
pdf_processor = PDFProcessor()
ai_service = AIService()
ppt_generator = PPTGenerator()

security = HTTPBearer(auto_error=False)

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if token.startswith("Bearer "):
        token = token[7:]
    
    user = await auth_service.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    error = request.query_params.get("error")
    success = request.query_params.get("success")
    return templates.TemplateResponse("login.html", {"request": request, "error": error, "success": success})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse("register.html", {"request": request, "error": error})

@app.post("/register")
async def register(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        await auth_service.create_user(username, email, password)
        return RedirectResponse(url="/?success=Registration successful", status_code=303)
    except ValueError as e:
        return RedirectResponse(url="/register?error=" + str(e), status_code=303)

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    token = await auth_service.authenticate_user(username, password)
    if not token:
        return RedirectResponse(url="/?error=Invalid credentials", status_code=303)
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: User = Depends(get_current_user)):
    db = await get_database()
    presentations_cursor = db.presentations.find({"user_id": str(user.id)}).sort("created_at", -1)
    presentations = []
    async for doc in presentations_cursor:
        doc["_id"] = str(doc["_id"])
        presentations.append(Presentation(**doc))
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "presentations": presentations})

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("upload.html", {"request": request, "user": user})

@app.get("/presentations", response_class=HTMLResponse)
async def presentations_page(request: Request, user: User = Depends(get_current_user)):
    db = await get_database()
    presentations_cursor = db.presentations.find({"user_id": str(user.id)}).sort("created_at", -1)
    presentations = []
    async for doc in presentations_cursor:
        doc["_id"] = str(doc["_id"])
        presentations.append(Presentation(**doc))
    return templates.TemplateResponse("presentations.html", {"request": request, "user": user, "presentations": presentations})

@app.get("/notes/{presentation_id}", response_class=HTMLResponse)
async def notes_page_by_id(request: Request, presentation_id: str, user: User = Depends(get_current_user)):
    db = await get_database()
    presentation_doc = await db.presentations.find_one({"_id": ObjectId(presentation_id), "user_id": str(user.id)})
    if not presentation_doc:
        raise HTTPException(status_code=404, detail="Presentation not found")
    presentation_doc["_id"] = str(presentation_doc["_id"])
    presentation = Presentation(**presentation_doc)
    return templates.TemplateResponse("notes.html", {"request": request, "user": user, "presentation": presentation})

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    pages: str = Form("all"),
    title: str = Form(""),
    user: User = Depends(get_current_user)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    file_path = f"uploads/{user.id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    extracted_text = pdf_processor.extract_text(file_path, pages)
    notes = await ai_service.generate_notes(extracted_text)
    
    presentation_title = title or f"{file.filename} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    presentation = Presentation(
        user_id=str(user.id),
        title=presentation_title,
        notes=notes,
        pdf_filename=file.filename
    )
    
    db = await get_database()
    result = await db.presentations.insert_one(presentation.dict(by_alias=True, exclude={"id"}))
    
    return RedirectResponse(url=f"/notes/{result.inserted_id}", status_code=303)

@app.get("/notes", response_class=HTMLResponse)
async def notes_page(request: Request, user: User = Depends(get_current_user)):
    db = await get_database()
    presentation_doc = await db.presentations.find_one({"user_id": str(user.id)}, sort=[("created_at", -1)])
    if not presentation_doc:
        return RedirectResponse(url="/upload", status_code=303)
    presentation_doc["_id"] = str(presentation_doc["_id"])
    presentation = Presentation(**presentation_doc)
    return templates.TemplateResponse("notes.html", {"request": request, "user": user, "presentation": presentation})

@app.post("/notes/save")
async def save_notes(notes: str = Form(...), user: User = Depends(get_current_user)):
    db = await get_database()
    presentation_doc = await db.presentations.find_one({"user_id": str(user.id)}, sort=[("created_at", -1)])
    if not presentation_doc:
        raise HTTPException(status_code=404, detail="No presentation found")
    
    await db.presentations.update_one(
        {"_id": presentation_doc["_id"]},
        {"$set": {"notes": notes}}
    )
    return {"status": "saved"}

@app.post("/generate-ppt")
async def generate_ppt(user: User = Depends(get_current_user)):
    db = await get_database()
    presentation_doc = await db.presentations.find_one({"user_id": str(user.id)}, sort=[("created_at", -1)])
    if not presentation_doc or not presentation_doc.get("notes"):
        raise HTTPException(status_code=400, detail="No notes available")
    
    ppt_path = ppt_generator.create_presentation(presentation_doc["notes"], str(user.id))
    feedback = await ai_service.review_presentation(presentation_doc["notes"])
    
    return {"ppt_path": ppt_path, "feedback": feedback}

@app.get("/ppt-review", response_class=HTMLResponse)
async def ppt_review_page(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("ppt_review.html", {"request": request, "user": user})

@app.get("/view-ppt", response_class=HTMLResponse)
async def view_ppt_page(request: Request, user: User = Depends(get_current_user)):
    db = await get_database()
    presentation_doc = await db.presentations.find_one({"user_id": str(user.id)}, sort=[("created_at", -1)])
    if not presentation_doc:
        return RedirectResponse(url="/upload", status_code=303)
    presentation_doc["_id"] = str(presentation_doc["_id"])
    presentation = Presentation(**presentation_doc)
    return templates.TemplateResponse("view_ppt.html", {"request": request, "user": user, "presentation": presentation})

@app.get("/view-ppt/{presentation_id}", response_class=HTMLResponse)
async def view_ppt_by_id(request: Request, presentation_id: str, user: User = Depends(get_current_user)):
    db = await get_database()
    presentation_doc = await db.presentations.find_one({"_id": ObjectId(presentation_id), "user_id": str(user.id)})
    if not presentation_doc:
        raise HTTPException(status_code=404, detail="Presentation not found")
    presentation_doc["_id"] = str(presentation_doc["_id"])
    presentation = Presentation(**presentation_doc)
    return templates.TemplateResponse("view_ppt.html", {"request": request, "user": user, "presentation": presentation})

@app.get("/present-ppt", response_class=HTMLResponse)
async def present_ppt_page(request: Request, user: User = Depends(get_current_user)):
    db = await get_database()
    presentation_doc = await db.presentations.find_one({"user_id": str(user.id)}, sort=[("created_at", -1)])
    if not presentation_doc:
        return RedirectResponse(url="/upload", status_code=303)
    presentation_doc["_id"] = str(presentation_doc["_id"])
    presentation = Presentation(**presentation_doc)
    return templates.TemplateResponse("present_ppt.html", {"request": request, "user": user, "presentation": presentation})

@app.get("/present-ppt/{presentation_id}", response_class=HTMLResponse)
async def present_ppt_by_id(request: Request, presentation_id: str, user: User = Depends(get_current_user)):
    db = await get_database()
    presentation_doc = await db.presentations.find_one({"_id": ObjectId(presentation_id), "user_id": str(user.id)})
    if not presentation_doc:
        raise HTTPException(status_code=404, detail="Presentation not found")
    presentation_doc["_id"] = str(presentation_doc["_id"])
    presentation = Presentation(**presentation_doc)
    return templates.TemplateResponse("present_ppt.html", {"request": request, "user": user, "presentation": presentation})

@app.get("/download-ppt")
async def download_ppt(user: User = Depends(get_current_user)):
    ppt_path = f"uploads/presentation_{user.id}.pptx"
    if os.path.exists(ppt_path):
        return FileResponse(ppt_path, filename=f"{user.username}_presentation.pptx")
    raise HTTPException(status_code=404, detail="Presentation not found")

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)