import os
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from openai import OpenAI

# ===============================
# CONFIGURAÇÕES GERAIS
# ===============================
SCOPES = ["https://www.googleapis.com/auth/blogger"]
BLOG_ID = "5852420775961497718"
CONTENT_DIR = "content"

print("📂 Diretório atual:", os.getcwd())

# Garante que a pasta content exista
os.makedirs(CONTENT_DIR, exist_ok=True)
print("📁 Arquivos em content:", os.listdir(CONTENT_DIR))

# ===============================
# GERA CONTEÚDO COM IA
# ===============================
def gerar_conteudo_ia():
    print("🤖 Gerando conteúdo com IA...")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("❌ OPENAI_API_KEY não encontrada no ambiente")

    # Remove qualquer espaço ou quebra invisível
    api_key = api_key.strip()

    client = OpenAI(api_key=api_key)

    prompt = (
        "Crie um artigo educativo para um blog de fotografia amadora.\n"
        "Tema: Erros comuns que iniciantes cometem ao fotografar.\n"
        "Linguagem clara, didática e envolvente.\n\n"
        "Retorne no seguinte formato:\n"
        "TÍTULO:\n"
        "texto do título\n\n"
        "ARTIGO:\n"
        "texto do artigo com cerca de 600 palavras"
    )

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    texto = resposta.choices[0].message.content.strip()

    # ===============================
    # PARSE SEGURO DO TEXTO
    # ===============================
    if "TÍTULO:" not in texto or "ARTIGO:" not in texto:
        raise Exception("❌ Resposta da IA fora do formato esperado")

    titulo = texto.split("TÍTULO:")[1].split("ARTIGO:")[0].strip()
    artigo = texto.split("ARTIGO:")[1].strip()

    # Salva os arquivos de conteúdo
    with open(f"{CONTENT_DIR}/titulo.txt", "w", encoding="utf-8") as f:
        f.write(titulo)

    with open(f"{CONTENT_DIR}/artigo_pronto.txt", "w", encoding="utf-8") as f:
        f.write(artigo)

    print("✅ Conteúdo gerado com sucesso")
    print(f"📝 Título gerado: {len(titulo)} caracteres")
    print(f"📄 Artigo gerado: {len(artigo)} caracteres")

# ===============================
# AUTENTICAÇÃO BLOGGER
# ===============================
def autenticar():
    print("🔐 Autenticando no Blogger")

    blogger_token = os.getenv("BLOGGER_TOKEN")
    if not blogger_token:
        raise Exception("❌ BLOGGER_TOKEN não encontrado no ambiente")

    token_info = json.loads(blogger_token)
    creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    return creds

# ===============================
# FORMATA ARTIGO EM HTML
# ===============================
def formatar_artigo_html(texto):
    paragrafos = texto.split("\n\n")
    return "\n".join(
        f"<p>{p.strip()}</p>" for p in paragrafos if p.strip()
    )

# ===============================
# PUBLICA NO BLOGGER
# ===============================
def publicar_post():
    print("🚀 Publicando no Blogger")

    creds = autenticar()
    service = build("blogger", "v3", credentials=creds)

    with open(f"{CONTENT_DIR}/titulo.txt", "r", encoding="utf-8") as f:
        titulo = f.read().strip()

    with open(f"{CONTENT_DIR}/artigo_pronto.txt", "r", encoding="utf-8") as f:
        artigo = f.read().strip()

    with open(f"{CONTENT_DIR}/assinatura.html", "r", encoding="utf-8") as f:
        assinatura = f.read()

    if not titulo or not artigo:
        raise Exception("❌ Título ou artigo vazio. Publicação cancelada.")

    artigo_html = formatar_artigo_html(artigo)

    conteudo = f"""
<div class="post-body entry-content">
  <h1 style="text-align:center;">{titulo}</h1>

  <div style="font-size:18px;line-height:1.6;text-align:justify;">
    {artigo_html}
  </div>

  <div style="margin-top:30px;">
    {assinatura}
  </div>
</div>
"""

    response = service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": titulo,
            "content": conteudo
        },
        isDraft=False
    ).execute()

    print("✅ Post publicado com sucesso")
    print("🔗 URL:", response.get("url"))

# ===============================
# EXECUÇÃO PRINCIPAL
# ===============================
if __name__ == "__main__":
    print("🚀 Iniciando automação completa")
    gerar_conteudo_ia()
    publicar_post()
