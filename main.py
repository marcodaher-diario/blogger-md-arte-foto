import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = "5852420775961497718"

BASE_DIR = os.getcwd()
CONTENT_DIR = os.path.join(BASE_DIR, "content")

ARTIGO_PATH = os.path.join(CONTENT_DIR, "artigo_pronto.txt")
ASSINATURA_PATH = os.path.join(CONTENT_DIR, "assinatura.html")
TITULO_PATH = os.path.join(CONTENT_DIR, "titulo.txt")

print("📂 Diretório atual:", BASE_DIR)
print("📁 Arquivos em content:", os.listdir(CONTENT_DIR))

def ler_arquivo(caminho):
    if not os.path.exists(caminho):
        print(f"❌ Arquivo não encontrado: {caminho}")
        return ""
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.read().strip()
        print(f"📄 Conteúdo lido ({os.path.basename(caminho)}): {len(conteudo)} caracteres")
        return conteudo

def publicar_post():
    print("🚀 Iniciando automação Blogger")
    print("🔐 Autenticando via BLOGGER_TOKEN")

    token_json = json.loads(os.environ["BLOGGER_TOKEN"])
    creds = Credentials.from_authorized_user_info(token_json)

    service = build("blogger", "v3", credentials=creds)

    titulo = ler_arquivo(TITULO_PATH)
    artigo = ler_arquivo(ARTIGO_PATH)
    assinatura = ler_arquivo(ASSINATURA_PATH)

    if not artigo:
        raise Exception("❌ O artigo está vazio. Publicação cancelada.")

    conteudo_final = artigo + "\n\n<hr>\n\n" + assinatura

    post = {
        "kind": "blogger#post",
        "title": titulo,
        "content": conteudo_final
    }

    response = service.posts().insert(
        blogId=BLOG_ID,
        body=post,
        isDraft=False
    ).execute()

    print("✅ Post publicado com sucesso!")
    print("🔗 URL:", response["url"])

if __name__ == "__main__":
    publicar_post()
