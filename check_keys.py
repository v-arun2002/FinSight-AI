import os
from dotenv import load_dotenv

load_dotenv()

keys = ['GROQ_API_KEY', 'ALPHA_VANTAGE_API_KEY', 'FRED_API_KEY', 'TAVILY_API_KEY']

for key in keys:
    val = os.getenv(key)
    print(f"{key}: {'SET' if val else 'MISSING'}")