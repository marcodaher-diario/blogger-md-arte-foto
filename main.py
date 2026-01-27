import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# ===============================
# CONFIGURAÇÕES
# ===============================
SCOPES = ["https://www.googleapis.com/auth/blogger"]
BLOG_ID = "5852420775961497718"
CONTENT_DIR = "content"

FILA_PATH = os.path.join(CONTENT_DIR, "fila_temas.json")
CONTROLE_PATH = os.path.join(CONTENT_DIR, "controle_publicacao.json")

INTERVALO_DIAS = 3

print("📂 Diretório atual:", os.getcwd())
os.makedirs(CONTENT_DIR, exist_ok=True)
print("📁 Arquivos em content:", os.listdir(CONTENT_DIR))

# ===============================
# TEMAS / CONTEÚDO
# ===============================
TEMAS = ["erros_fotografia", "iso", "abertura", "velocidade", "composicao"]

CONTEUDO = {
    "erros_fotografia": {
        "titulo": "Erros comuns na fotografia amadora e como evitá-los",
        "imagem": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Photographer_with_camera.jpg",
        "labels": ["Fotografia", "Iniciantes", "Erros Comuns"],
        "introducao": "Muitos iniciantes cometem erros simples que afetam diretamente a qualidade das fotos.",
        "itens": [
            ("ISO alto sem necessidade", "Gera ruído e perda de qualidade."),
            ("Ignorar a luz", "Resulta em fotos mal iluminadas."),
            ("Fotos sem foco", "Comprometem o resultado final."),
        ],
        "dicas": [
            "Observe a iluminação",
            "Use ISO baixo sempre que possível",
            "Confira o foco antes do clique",
        ],
        "conclusao": "Evitar esses erros ajuda a evoluir rapidamente na fotografia.",
    },
    "iso": {
        "titulo": "O que é ISO na fotografia e como usar corretamente",
        "imagem": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Camera_ISO_settings.jpg",
        "labels": ["Fotografia", "ISO"],
        "introducao": "O ISO controla a sensibilidade do sensor à luz.",
        "itens": [
            ("ISO baixo", "Menos ruído e melhor qualidade."),
            ("ISO alto", "Mais luz, porém mais ruído."),
        ],
        "dicas": [
            "Use ISO baixo em ambientes claros",
            "Aumente ISO apenas quando necessário",
        ],
        "conclusao": "Entender o ISO melhora fotos em diferentes condições de luz.",
    },
}

# ===============================
# CONTROLE DE DATA
# ===============================
def pode_publicar():
    if not os.path.exists(CONTROLE_PATH):
        return True
    with open(CONTROLE_PATH, encoding="utf-8") as f:
        dados = json.load(f)
    ultima = datetime.fromisoformat(dados["ultima_publicacao"])
    return datetime.now() >= ultima + timedelta(days=INTERVALO_DIAS)

def registrar_publicacao():
    with open(CONTROLE_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {"ultima_publicacao": datetime.now().isoformat()},
            f,
            ensure_ascii=False,
            indent=2
        )

# ===============================
# FILA DE TEMAS
# ===============================
def obter_proximo_tema():
    if not os.path.exists(FILA_PATH):
        fila = TEMAS.copy()
    else:
        with open(FILA_PATH, encoding="utf-8") as f:
            fila = json.load(f)
    if not fila:
        fila = TEMAS.copy()
    tema = fila.pop(0)
    with open(FILA_PATH, "w", encoding="utf-8") as f:
        json.dump(fila, f, ensure_ascii=False, indent=2)
    return tema

# ===============================
# AUTENTICAÇÃO BLINDADA
# ===============================
def autenticar():
    raw = os.getenv("BLOGGER_TOKEN", "").strip()

    if not raw:
        raise Exception("❌ BLOGGER_TOKEN está vazio no GitHub Secrets")

    try:
        token_info = json.loads(raw)
    except json.JSONDecodeError:
        raise Exception(
            "❌ BLOGGER_TOKEN inválido. "
            "Cole o conteúdo do token.json em UMA ÚNICA LINHA no GitHub Secrets."
        )

    return Credentials.from_authorized_user_info(token_info, SCOPES)

# ===============================
# GERAR CONTEÚDO
# ===============================
def gerar_conteudo():
    tema_key = obter_proximo_tema()
    tema = CONTEUDO[tema_key]

    artigo = [tema["introducao"], "\n\nPrincipais pontos:\n"]
    for t, d in tema["itens"]:
        artigo.append(f"{t}\n{d}")

    artigo.append("\n\nDicas práticas:\n")
    for dica in tema["dicas"]:
        artigo.append(f"- {dica}")

    artigo.append("\n\n" + tema["conclusao"])
    artigo_final = "\n\n".join(artigo)

    with open(f"{CONTENT_DIR}/titulo.txt", "w", encoding="utf-8") as f:
        f.write(tema["titulo"])
    with open(f"{CONTENT_DIR}/artigo_pronto.txt", "w", encoding="utf-8") as f:
        f.write(artigo_final)
    with open(f"{CONTENT_DIR}/imagem.txt", "w", encoding="utf-8") as f:
        f.write(tema["imagem"])
    with open(f"{CONTENT_DIR}/labels.json", "w", encoding="utf-8") as f:
        json.dump(tema["labels"], f, ensure_ascii=False)

    print("🎯 Tema preparado:", tema_key)

# ===============================
# PUBLICAÇÃO
# ===============================
def publicar():
    creds = autenticar()
    service = build("blogger", "v3", credentials=creds)

    with open(f"{CONTENT_DIR}/titulo.txt") as f:
        titulo = f.read()
    with open(f"{CONTENT_DIR}/artigo_pronto.txt") as f:
        artigo = f.read()
    with open(f"{CONTENT_DIR}/imagem.txt") as f:
        imagem = f.read()
    with open(f"{CONTENT_DIR}/labels.json") as f:
        labels = json.load(f)
    with open(f"{CONTENT_DIR}/assinatura.html") as f:
        assinatura = f.read()

    html = f"""
<div class="post-body entry-content">
<h1 style="text-align:center;">{titulo}</h1>
<div style="text-align:center;margin:20px 0;">
<img src="{imagem}" style="max-width:680px;width:100%;" alt="{titulo}">
</div>
<div style="font-size:18px;line-height:1.6;text-align:justify;">
{artigo}
</div>
<div style="margin-top:30px;">{assinatura}</div>
</div>
"""

    service.posts().insert(
        blogId=BLOG_ID,
        body={"title": titulo, "content": html, "labels": labels},
        isDraft=False
    ).execute()

    registrar_publicacao()
    print("✅ Post publicado com sucesso")

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    print("🚀 Publicação a cada 3 dias")
    if pode_publicar():
        gerar_conteudo()
        publicar()
    else:
        print("⏳ Ainda não é dia de publicação")
