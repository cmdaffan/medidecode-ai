import os
import time
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

# 1. Connect to your Pinecone account
PINECONE_API_KEY = "pcsk_LT4VB_Gx8wj8F7xGU7KHbW72xb9TFvnXJxHgGRdHFRoBMSNqVKmjN5uQxfG4LJd41FbH1"

# THE FIX: Force the key into the environment variables so LangChain can see it
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "medidecode-kb"

def setup_database():
    existing_indexes = [idx.name for idx in pc.list_indexes()]
    
    # 2. Check if the database exists
    if index_name not in existing_indexes:
        print(f"Creating Pinecone index: {index_name} (this takes about 30 seconds)...")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        while not pc.describe_index(index_name).status['ready']:
            time.sleep(1)
            
    print("Database is ready!")

    # 3. Load the free HuggingFace embedding model
    print("Loading free AI text model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Create our "Medical Glossary"
    medical_definitions = [
        "Hemoglobin: A protein in red blood cells that carries oxygen. Normal range for women is 12.0 to 15.5 g/dL. Low hemoglobin indicates fatigue and a condition known as anemia.",
        "Cholesterol: A waxy substance in the blood. A normal, healthy level is below 200 mg/dL. Levels above 240 mg/dL are considered high and can increase cardiovascular risk."
    ]

    # 5. Upload the knowledge to Pinecone
    print("Uploading medical definitions into the Pinecone Vector Database...")
    PineconeVectorStore.from_texts(
        texts=medical_definitions,
        embedding=embeddings,
        index_name=index_name
    )
    print("Upload complete! Your AI's medical brain is now online.")

if __name__ == "__main__":
    setup_database()