"""
Gemini embeddings API connection test.

Sirf ek sample text ko embedding (meaning-fingerprint) mein convert
karke check karta hai ke API key sahi set hui hai aur connection
kaam kar raha hai.

Run: backend/ folder se (venv active):
    python test_gemini.py
"""

import os

from dotenv import load_dotenv

load_dotenv()

from google import genai

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY .env file mein nahi mili. Pehle .env check karo.")
    exit(1)

client = genai.Client(api_key=api_key)

print("Test text ko embedding mein convert kar rahe hain...")

result = client.models.embed_content(
    model="gemini-embedding-2",
    contents="Wireless bluetooth headphones with noise cancellation",
)

embedding = result.embeddings[0].values

print("\nSuccess! Embedding ban gayi.")
print(f"Embedding mein numbers ki tadaad (dimensions): {len(embedding)}")
print(f"Pehle 5 numbers (sample): {embedding[:5]}")
