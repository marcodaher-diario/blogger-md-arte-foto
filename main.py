import os
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from openai import OpenAI

# ===============================
# CONFIGURAÇÕES
# ===============================
SCOPES = ["https://www.googleapis.com/auth/blogger"]
BLOG_ID = "5852420775961497718"
CONTENT_DIR = "content"

print("📂 Diretório atual:", os.getcwd())
print("📁 Arquivos em content:", os.listdir(CONTENT_DIR))

# ===============================
# IA – GERA CONTEÚDO
# ===============================
def gerar_conteudo_ia():
    print("🤖 Gerando conteúdo com IA...")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = """
    Crie um artigo educativo para um blog de fotografia amadora.
    Tema: Erros comuns que iniciantes cometem ao fotografar.
    Linguagem clara, didática e envolvente.
    Gere:
    1) Um título chamativo
    2) Um artigo com cerca de 600 palavras
    """

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    texto = resposta.choices[0].message.content.strip()

    # Separação simples
    linhas = texto.split("\n")
    titulo = linhas[0]
    artigo = "\n".join(linhas[1:]).strip()

    os.makedirs(CONTENT_DIR, exist_ok=True)

    with open(f"{CONTENT_DIR}/titulo.txt", "w", encoding="utf-8") as f:
        f.write(titulo)

    with open(f"{CONTENT_DIR}/artigo_pronto.txt", "w", encoding="utf-8") as f:
        f.write(artigo)

    print("✅ Conteúdo gerado com sucesso")

# ===============================
# AUTENTICAÇÃO BLOGGER
# ===============================
def autenticar():
    print("🔐 Autenticando no Blogger")

    token_info = json.loads(os.environ["BLOGGER_TOKEN"])
    creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    return creds

# ===============================
# FORMATA HTML
# ===============================
def formatar_artigo_html(texto):
    paragrafos = texto.split("\n\n")
    return "\n".join(f"<p>{p.strip()}</p>" for p in paragrafos if p.strip())

# ===============================
# PUBLICAR POST
# ===============================
def publicar_post():
    print("🚀 Publicando no Blogger")

    creds = autenticar()
    service = build("blogger", "v3", credentials=creds)

    with open("content/titulo.txt", "r", encoding="utf-8") as f:
        titulo = f.read().strip()

    with open("content/artigo_pronto.txt", "r", encoding="utf-8") as f:
        artigo = f.read().strip()

    with open("content/assinatura.html", "r", encoding="utf-8") as f:
        assinatura = f.read()

    if not titulo or not artigo:
        raise Exception("❌ Conteúdo vazio. Publicação abortada.")

    artigo_html = formatar_artigo_html(artigo)

    conteudo = f"""
    <div class="post-body entry-content">
        <h1 style="text-align:center;">{titulo}</h1>
        {artigo_html}
        <div style="margin-top:30px;">
            {assinatura}
        </div>
    </div>
    """

    service.posts().insert(
        blogId=BLOG_ID,
        body={"title": titulo, "content": conteudo},
        isDraft=False
    ).execute()

    print("✅ Post publicado com sucesso")

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    gerar_conteudo_ia()
    publicar_post()
