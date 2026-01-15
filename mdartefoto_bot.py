import os
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


# ===============================
# CONFIGURAÇÕES
# ===============================
print("Diretório atual:", os.getcwd())
print("Arquivos em content:", os.listdir("content"))
SCOPES = ["https://www.googleapis.com/auth/blogger"]
BLOG_ID = "5852420775961497718"

# ===============================
# AUTENTICAÇÃO
# ===============================
def autenticar():
    # 🔹 GITHUB ACTIONS
    if os.getenv("GITHUB_ACTIONS") == "true":
        print("🔐 Autenticando via BLOGGER_TOKEN (GitHub Secrets)")

        token_info = json.loads(os.environ["BLOGGER_TOKEN"])
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        return creds

    # 🔹 EXECUÇÃO LOCAL
    print("💻 Autenticando localmente via token.json")
    return Credentials.from_authorized_user_file("token.json", SCOPES)

# ===============================
# FORMATA TEXTO EM PARÁGRAFOS
# ===============================
def formatar_artigo_html(texto):
    paragrafos = texto.split("\n\n")
    return "\n".join(f"<p>{p.strip()}</p>" for p in paragrafos if p.strip())

# ===============================
# MONTA HTML FINAL
# ===============================
def montar_conteudo_post(titulo, imagem_url, texto_artigo_html, assinatura_html):
    return f"""
<div class="post-body entry-content">

<h1 style="text-align:center;font-size:26px;color:#686868;">
{titulo}
</h1>

<div style="text-align:center;margin-bottom:20px;">
  <img src="{imagem_url}" style="max-width:680px;width:100%;">
</div>

<div style="font-size:18px;line-height:1.6;text-align:justify;color:#686868;">
{texto_artigo_html}
</div>

<div style="margin-top:30px;">
{assinatura_html}
</div>

</div>
"""

# ===============================
# PUBLICAÇÃO
# ===============================
def publicar_post():
    creds = autenticar()
    service = build("blogger", "v3", credentials=creds)

    with open("content/titulo.txt", "r", encoding="utf-8") as f:
        titulo = f.read().strip()

    with open("content/artigo_pronto.txt", "r", encoding="utf-8") as f:
        texto_raw = f.read()

    with open("content/assinatura.html", "r", encoding="utf-8") as f:
        assinatura_html = f.read()

    texto_html = formatar_artigo_html(texto_raw)

    imagem_url = "https://URL-DA-SUA-IMAGEM.jpg"

    conteudo = montar_conteudo_post(
        titulo,
        imagem_url,
        texto_html,
        assinatura_html
    )

    service.posts().insert(
        blogId=BLOG_ID,
        body={"title": titulo, "content": conteudo},
        isDraft=False
    ).execute()

    print("✅ Post publicado com sucesso!")

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    publicar_post()
