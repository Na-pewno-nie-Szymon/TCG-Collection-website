from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import urllib.parse
import json
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect('kolekcja.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_id TEXT UNIQUE,
            card_data TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Mała funkcja pomocnicza: usuwa wiodące zera (np. "071" -> "71")
def clean_number(val: str):
    val = val.strip()
    if val.isdigit():
        return val.lstrip('0') or '0'
    return val

@app.get("/search/{query:path}")
def search_card(query: str):
    query = urllib.parse.unquote(query).strip()
    
    # Kiedy wpisujesz kod z ukośnikiem (np. 071/086)
    if "/" in query:
        parts = query.split("/")
        if len(parts) == 2:
            # Używamy naszej funkcji, żeby wyczyścić zera!
            card_num = clean_number(parts[0])   # Zrobi z "071" -> "71"
            set_total = clean_number(parts[1])  # Zrobi z "086" -> "86"
            
            api_query = f'number:"{card_num}"'
            url = f"https://api.pokemontcg.io/v2/cards?q={api_query}"
            
            try:
                response = requests.get(url)
                data = response.json()
                
                if 'data' in data:
                    exact_matches = [
                        card for card in data['data'] 
                        if str(card.get('set', {}).get('printedTotal')) == set_total
                    ]
                    data['data'] = exact_matches
                    
                return data
            except Exception as e:
                return {"error": str(e)}

    # Standardowe wyszukiwanie
    else:
        # Jeśli ktoś wpisze po prostu "071" w wyszukiwarkę
        clean_q = clean_number(query)
        api_query = f'name:"{query}" OR id:"{query}" OR number:"{clean_q}"'
        url = f"https://api.pokemontcg.io/v2/cards?q={api_query}"
        
        try:
            response = requests.get(url)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
        
@app.get("/collection")
def get_my_collection():
    try:
        conn = sqlite3.connect('kolekcja.db')
        c = conn.cursor()
        c.execute("SELECT card_data FROM collected_cards ORDER BY added_at DESC")
        rows = c.fetchall()
        conn.close()
        
        cards = [json.loads(row[0]) for row in rows]
        return {"data": cards}
    except Exception as e:
        return {"error": str(e)}
    
@app.delete("/collection/remove/{api_id}")
def remove_from_collection(api_id: str):
    try:
        conn = sqlite3.connect('kolekcja.db')
        c = conn.cursor()
        c.execute("DELETE FROM collected_cards WHERE api_id = ?", (api_id,))
        conn.commit()
        conn.close()
        return {"status": "Card removed from collection"}
    except Exception as e:
        return {"status": "error", "message": str(e)}