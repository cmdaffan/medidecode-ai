import os
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pypdf
from PIL import Image  # Our new image handler
import google.generativeai as genai  # Direct access to Gemini for image OCR
import uvicorn

from agent import decode_medical_text

app = FastAPI(title="MediDecode Multi-Format API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure the underlying Gemini API for direct multimodal processing
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

@app.get("/")
def home():
    return {"status": "healthy", "message": "MediDecode Multi-Format Backend is running"}

@app.post("/api/analyze")
async def analyze_document(file: UploadFile = File(...)):
    print(f"\n--- New Multi-Format Request ---")
    print(f"Received file: {file.filename} ({file.content_type})")
    
    file_extension = file.filename.lower().split('.')[-1]
    extracted_text = ""
    
    try:
        file_content = await file.read()
        
        # === PATH A: HANDLE PDF ===
        if file_extension == 'pdf':
            print("[Server] Processing PDF file...")
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
                    
        # === PATH B: HANDLE IMAGES (PNG, JPG, JPEG) ===
        elif file_extension in ['png', 'jpg', 'jpeg']:
            print("[Server] Processing Image file via Gemini OCR...")
            # Open the image file in Python
            image = Image.open(io.BytesIO(file_content))
            
            # Use Gemini's multimodal power to extract text cleanly from the image
            ocr_model = genai.GenerativeModel("gemini-2.5-flash")
            ocr_response = ocr_model.generate_content([
                "Extract every single piece of text, numbers, names, and medical data from this lab report image verbatim. Do not summarize.", 
                image
            ])
            extracted_text = ocr_response.text

        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported format .{file_extension}. Please upload a PDF, PNG, or JPG."
            )
            
        # Check if we successfully grabbed text
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract readable text from the file.")
            
        print(f"[Server] Text extraction successful! Characters read: {len(extracted_text)}")
        
        # === PATH C: RUN RAG AGENT ===
        print("[Server] Sending text to RAG agent...")
        real_ai_summary = decode_medical_text(extracted_text)
        
        return {
            "fileName": file.filename,
            "extractedData": {
                "patientName": "Extracted from File",
                "fileType": file_extension
            },
            "aiSummary": real_ai_summary,
            "safetyGuardrailTriggered": False
        }
        
    except Exception as e:
        print(f"[Server Error] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)