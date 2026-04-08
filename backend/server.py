from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS = {"X-Api-Key": "TWOJ_KLUCZ_JESLI_MASZ"}

@app.get('/search/{name}')
def seqrch_card(name: str):
    url = f"https://api.pokemontcg.io/v2/cards?q=name:{name}"
    try:
        response = requests.get(url, headers=HEADERS)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get('/my-collection')
def get_collection():
    # Future DB
    return {"message": "Tu będą zapisane karty"}