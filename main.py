import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceCredentials

# ===============================
# CONFIGURAÇÕES
# ===============================
BLOG_ID = "5852420775961497718"

SCOPES_BLOGGER = ["https://www.googleapis.com/auth/blogger"]
SCOPES_SHEETS = ["https://www.googleapis.com/auth/spreadsheets"]

SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = "posts"

ASSINATURA_PATH = "content/assinatura.html"

INTERVALO_DIAS = 3

# ===============================
# AUTENTICAÇÃO
# ===============================
def autenticar_blogger():
    token_info = json.loads(os.environ["BLOGGER_TOKEN"])
    return Credentials.from_authorized_user_info(token_info, SCOPES_BLOGGER)

def autenticar_sheets():
    creds_info = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS"])
    return ServiceCredentials.from_service_account_info(
        creds_info,
        scopes=SCOPES_SHEETS
    )

# ===============================
# LER PLANILHA
# ===============================
def ler_posts():
    service = build("sheets", "v4", credentials=autenticar_sheets())
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_NAME}!A2:I"
    ).execute()
    return result.get("values", [])

# ===============================
# ATUALIZAR STATUS
# ===============================
def atualizar_status(linha, status):
    service = build("sheets", "v4", credentials=autenticar_sheets())
    service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_NAME}!I{linha}",
        valueInputOption="RAW",
        body={"values": [[status]]}
    ).execute()

# ===============================
# DATA DO ÚLTIMO POST
# ===============================
def ultima_data_publicada(posts):
    datas = []
    for post in posts:
        if len(post) >= 9 and post[8].lower() == "publicado":
            datas.append(datetime.strptime(post[1], "%Y-%m-%d"))
    return max(datas) if datas else None

# ===============================
# MONTAR HTML COM IMAGENS DISTRIBUÍDAS
# ===============================
def montar_html(titulo, texto, assinatura):
    paragrafos = texto.split("\n\n")

    html = []
    html.append(f'<h1 style="text-align:center;">{titulo}</h1>')

    for i, p in enumerate(paragrafos):
        html.append(
            f'<p style="text-align:justify;font-size:18px;line-height:1.7;">{p}</p>'
        )

        # Espaços reservados para imagens (manual depois)
        if i == 1:
            html.append("<!-- IMAGEM_1_AQUI -->")
        if i == len(paragrafos) // 2:
            html.append("<!-- IMAGEM_2_AQUI -->")

    html.append(assinatura)

    return '<div class="post-body entry-content">' + "".join(html) + "</div>"

# ===============================
# PUBLICAR POST
# ===============================
def publicar_post(post, linha):
    creds = autenticar_blogger()
    service = build("blogger", "v3", credentials=creds)

    titulo = post[3]
    texto = post[4]
    labels = post[7].split(",")

    with open(ASSINATURA_PATH, encoding="utf-8") as f:
        assinatura = f.read()

    html = montar_html(titulo, texto, assinatura)

    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": titulo,
            "content": html,
            "labels": labels
        },
        isDraft=False
    ).execute()

    atualizar_status(linha, "publicado")

# ===============================
# EXECUÇÃO PRINCIPAL
# ===============================
def main():
    posts = ler_posts()
    hoje = datetime.now()

    ultima = ultima_data_publicada(posts)
    if ultima and hoje < ultima + timedelta(days=INTERVALO_DIAS):
        print("⏳ Intervalo de 3 dias ainda não cumprido.")
        return

    for idx, post in enumerate(posts, start=2):
        if post[8].lower() == "pendente":
            data_post = datetime.strptime(post[1], "%Y-%m-%d")
            if data_post <= hoje:
                print(f"📝 Publicando post ID {post[0]}")
                publicar_post(post, idx)
                print("✅ Post publicado com sucesso")
                return

    print("⏳ Nenhum post pendente para publicar hoje.")

if __name__ == "__main__":
    main()
