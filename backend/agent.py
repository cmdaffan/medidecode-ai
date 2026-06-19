import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

# Load environment variables (for Gemini key)
load_dotenv()

# 1. Force your Pinecone key directly into the environment variables
PINECONE_API_KEY = "pcsk_LT4VB_Gx8wj8F7xGU7KHbW72xb9TFvnXJxHgGRdHFRoBMSNqVKmjN5uQxfG4LJd41FbH1"  # <-- Make sure to paste your Pinecone key here!
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# 2. Initialize our free HuggingFace text-comparison tool
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 3. Connect to our existing Pinecone medical knowledge index
index_name = "medidecode-kb"
vector_store = PineconeVectorStore(index_name=index_name, embedding=embeddings)

# 4. Initialize the Google Gemini AI Model
# Lowered temperature to 0.1 to make the AI more deterministic and strict with JSON formatting
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.1 
)

def decode_medical_text(raw_report_text: str) -> dict:
    """
    Takes raw medical text, searches Pinecone, and returns a STRICT JSON dictionary 
    for the React frontend to render as a table.
    """
    print("\n[Agent] Searching vector database for complex medical terms...")
    
    try:
        search_results = vector_store.similarity_search(raw_report_text, k=2)
        context_knowledge = "\n".join([doc.page_content for doc in search_results])
    except Exception as e:
        print(f"[Agent Warning] Pinecone search failed: {e}. Proceeding without context.")
        context_knowledge = "No additional context found."
    
    print("[Agent] Context gathered. Asking Gemini to extract structured JSON data...")

# The updated prompt for ultra-simple, emoji-friendly English
    system_prompt = f"""
    You are a warm, empathetic health guide talking to a patient. 
    The patient can already see their exact numbers in a data table, so absolutely DO NOT repeat specific numbers, ranges, or units. 
    DO NOT use any brackets like [ ] or ( ) or technical symbols.

    Your goal is to provide a brief, "big picture" overview of their lab results in extremely simple, everyday English that anyone can understand.
    
    Guidelines for the summary:
    - Use friendly emojis to make it visual and less intimidating (e.g., 🩸, 🛡️, ⚡, ❤️).
    - Group insights by simple body functions like "Oxygen & Energy" or "Immune System".
    - Talk like a normal, caring human friend. Zero medical jargon.
    - Never diagnose. Always end by warmly encouraging them to consult their doctor.

    Use the following verified medical references to ground your explanation:
    {context_knowledge}

    You MUST respond with strictly valid JSON matching this exact structure. Do NOT wrap the response in ```json markdown blocks.
    {{
        "patientName": "Extract the patient's name, or 'Unknown'",
        "biomarkers": [
            {{
                "name": "Name of test (e.g., Hemoglobin)",
                "value": "The exact number",
                "unit": "The unit (e.g., g/dL)",
                "range": "The normal reference range",
                "status": "NORMAL, HIGH, or LOW"
            }}
        ],
        "summary": "Write your warm, emoji-filled, number-free explanation here. Use HTML tags like <br><br> for paragraph spacing and <strong> for emphasis."
    }}
    """

    full_query = f"{system_prompt}\n\nPatient Report Transcript:\n{raw_report_text}"
    
    try:
        # Call Gemini
        response = llm.invoke(full_query)
        raw_text = response.content
        
        # Clean up potential Markdown formatting just in case the AI adds it
        cleaned_text = raw_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        # Parse the string into a real Python dictionary
        parsed_data = json.loads(cleaned_text)
        return parsed_data
        
    except json.JSONDecodeError as e:
        print(f"[Agent Error] Failed to parse JSON: {e}")
        # Safe Fallback so the server doesn't crash
        return {
            "patientName": "Unknown", 
            "biomarkers": [], 
            "summary": "We extracted the text, but the AI could not format the data table correctly."
        }
    except Exception as e:
        print(f"[Agent Error] LLM generation failed: {e}")
        return {
            "patientName": "Unknown",
            "biomarkers": [],
            "summary": "An error occurred while generating the report."
        }

if __name__ == "__main__":
    sample_ocr_input = "LAB REQ: #4412 -- PATIENT FEMALE: Jane Doe -- HEMOGLOBIN VAL: 10.5 g/dL (LOW) -- CHOLESTEROL TOTAL: 245 mg/dL (HIGH)"
    
    print("Testing the Medical Translation Agent...")
    translation_dict = decode_medical_text(sample_ocr_input)
    
    print("\n===== FINAL AI TRANSLATION (JSON DICT) =====")
    print(json.dumps(translation_dict, indent=2))
    