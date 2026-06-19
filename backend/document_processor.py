# MOCK AZURE PROCESSOR - No API Keys Needed

def extract_document_data(file_bytes: bytes):
    """
    This is a simulator. It bypasses Azure so you can build the 
    rest of the AI RAG pipeline without needing cloud keys right now.
    """
    print("Mocking Azure Document Intelligence extraction...")
    
    return {
        "text": "PATIENT NAME: Jane Doe\nDATE: 2026-06-17\nNOTES: Patient reports slight fatigue. Blood work ordered.",
        "tables": [
            [
                {"row": 0, "column": 0, "text": "Biomarker"},
                {"row": 0, "column": 1, "text": "Result"},
                {"row": 0, "column": 2, "text": "Normal Range"},
                {"row": 1, "column": 0, "text": "Hemoglobin"},
                {"row": 1, "column": 1, "text": "11.2 g/dL"},
                {"row": 1, "column": 2, "text": "12.0 - 15.5 g/dL"},
                {"row": 2, "column": 0, "text": "Cholesterol"},
                {"row": 2, "column": 1, "text": "240 mg/dL"},
                {"row": 2, "column": 2, "text": "< 200 mg/dL"}
            ]
        ]
    }