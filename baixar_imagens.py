import os
import json
import requests
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as ServiceCredentials

# ===============================
# CONFIGURAÇÕES
# ===============================
SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = "posts"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
IMAGENS_DIR = "content/imagens"

os.makedirs(IMAGENS_DIR, exist_ok=True)

# ===============================
# GOOGLE SHEETS
# ===============================
def sheets_service():
    creds_info = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS"])
    creds = ServiceCredentials.from_service_account_info(creds_info, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)

def ler_posts():
    service = sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_NAME}!A2:I"
    ).execute()
    return result.get("values", [])

# ===============================
# PEXELS
# ===============================
def buscar_imagens(query, quantidade=2):
    headers = {"Authorization": PEXELS_API_KEY}
    url = "https://api.pexels.com/v1/search"
    params = {
        "query": query,
        "per_page": quantidade,
        "orientation": "landscape"
    }
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()["photos"]

def baixar_imagem(url, destino):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    with open(destino, "wb") as f:
        f.write(r.content)

# ===============================
# EXECUÇÃO
# ===============================
def main():
    posts = ler_posts()

    for post in posts:
        if len(post) < 9:
            continue

        tema = post[2]
        img1_nome = post[5]
        img2_nome = post[6]
        status = post[8]

        if status != "pendente":
            continue

        caminho1 = os.path.join(IMAGENS_DIR, img1_nome)
        caminho2 = os.path.join(IMAGENS_DIR, img2_nome)

        if os.path.exists(caminho1) and os.path.exists(caminho2):
            print(f"✔ Imagens já existem para tema: {tema}")
            continue

        print(f"⬇️ Buscando imagens para: {tema}")
        fotos = buscar_imagens(tema, quantidade=2)

        baixar_imagem(fotos[0]["src"]["large"], caminho1)
        baixar_imagem(fotos[1]["src"]["large"], caminho2)

        print(f"✅ Imagens salvas: {img1_nome}, {img2_nome}")

if __name__ == "__main__":
    main()
