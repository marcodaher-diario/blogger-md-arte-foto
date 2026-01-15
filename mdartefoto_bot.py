import os
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/blogger']
BLOG_ID = '5852420775961497718'


# 🔧 FUNÇÃO DE MONTAGEM DO HTML
def montar_conteudo_post(titulo, imagem_url, texto_artigo, assinatura_html):

    html = f"""
<div class="post-body entry-content">

<h1 style="text-align:center;font-family:Arial;font-size:24px;font-weight:bold;color:#686868;margin:20px 0;">
{titulo}
</h1>

<div style="text-align:center;margin-bottom:20px;">
  <img src="{imagem_url}"
       alt="{titulo}"
       style="max-width:680px;width:100%;height:auto;" />
</div>

<br><br>

<div style="font-family:Arial;font-size:12px;color:#686868;text-align:justify;line-height:1.3;">
{texto_artigo}
</div>

<div style="margin-top:30px;">
{assinatura_html}
</div>

</div>
"""
    return html


# 🚀 FUNÇÃO PRINCIPAL
def publicar_post():
    if "BLOGGER_TOKEN" in os.environ:
        token_info = json.loads(os.environ["BLOGGER_TOKEN"])
    else:
        raise Exception("Variável de ambiente BLOGGER_TOKEN não encontrada.")
    
   # 🖥️ Execução local
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build('blogger', 'v3', credentials=creds)

    # 📂 LEITURA DOS ARQUIVOS
    with open("content/titulo.txt", "r", encoding="utf-8") as f:
        titulo = f.read().strip()

    with open("content/artigo_pronto.txt", "r", encoding="utf-8") as f:
        texto_artigo = f.read()

    with open("content/assinatura.html", "r", encoding="utf-8") as f:
        assinatura_html = f.read()

    # 🖼️ URL DA IMAGEM (depois automatizamos)
    imagem_url = "https://URL-DA-SUA-IMAGEM.jpg"

    # 🧠 MONTA HTML FINAL
    conteudo_html = montar_conteudo_post(
        titulo,
        imagem_url,
        texto_artigo,
        assinatura_html
    )

    post = {
        "title": titulo,
        "content": conteudo_html
    }

    service.posts().insert(
        blogId=BLOG_ID,
        body=post,
        isDraft=False
    ).execute()

    print("Post publicado com sucesso!")


if __name__ == "__main__":
    publicar_post()
