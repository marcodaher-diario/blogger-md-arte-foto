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

INTERVALO_DIAS = 0  # teste imediato

os.makedirs(CONTENT_DIR, exist_ok=True)

# ===============================
# TEMAS
# ===============================
TEMAS = ["erros_fotografia"]

CONTEUDO = {
    "erros_fotografia": {
        "titulo": "Erros comuns na fotografia amadora e como evitá-los",
        # ✅ URL COMPATÍVEL COM BLOGGER
        "imagem": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgRZ5K7N9nZ9O4Zx3f3gQb8uP8Yl4eRzJtY2p8s4rYw5j0zFj1Q6UOZ9pLx2l2x4bH1y/s1600/fotografia-camera.jpg",
        "labels": ["Fotografia", "Iniciantes", "Erros Comuns"],
        "texto": (
            "Muitos iniciantes cometem erros simples que afetam diretamente a qualidade das fotos.\n\n"
            "ISO alto sem necessidade gera ruído e perda de qualidade.\n"
            "Ignorar a luz resulta em fotos mal iluminadas.\n"
            "Fotos sem foco comprometem o resultado final.\n\n"
            "Dicas práticas:\n"
            "Observe a iluminação.\n"
            "Use ISO baixo sempre que possível.\n"
            "Confira o foco antes do clique.\n\n"
            "Evitar esses erros ajuda a evoluir rapidamente na fotografia."
        )
    }
}

# ===============================
# CONTROLE DE PUBLICAÇÃO
# ===============================
def pode_publicar():
    if not os.path.exists(CONTROLE_PATH):
        print("🟢 Nenhum controle encontrado. Publicação liberada.")
        return True

    with open(CONTROLE_PATH, encoding="utf-8") as f:
        dados = json.load(f)

    ultima = datetime.fromisoformat(dados["ultima_publicacao"])
    proxima = ultima + timedelta(days=INTERVALO_DIAS)

    return datetime.now() >= proxima


def registrar_publicacao():
    with open(CONTROLE_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {"ultima_publicacao": datetime.now().isoformat()},
            f,
            indent=2,
            ensure_ascii=False
        )

# ===============================
# FILA DE TEMAS
# ===============================
def obter_tema():
    if not os.path.exists(FILA_PATH):
        fila = TEMAS.copy()
    else:
        with open(FILA_PATH, encoding="utf-8") as f:
            fila = json.load(f)

    tema = fila.pop(0)

    with open(FILA_PATH, "w", encoding="utf-8") as f:
        json.dump(fila or TEMAS.copy(), f, indent=2, ensure_ascii=False)

    return tema

# ===============================
# AUTENTICAÇÃO
# ===============================
def autenticar():
    token = os.getenv("BLOGGER_TOKEN", "").strip()
    if not token:
        raise Exception("BLOGGER_TOKEN ausente")
    return Credentials.from_authorized_user_info(json.loads(token), SCOPES)

# ===============================
# PUBLICAÇÃO
# ===============================
def publicar():
    print("🚀 Publicando no Blogger")

    tema_key = obter_tema()
    tema = CONTEUDO[tema_key]

    creds = autenticar()
    service = build("blogger", "v3", credentials=creds)

    texto_html = tema["texto"].replace("\n", "<br>")

    html = (
        '<div class="post-body entry-content">'
        f'<h1 style="text-align:center;">{tema["titulo"]}</h1>'
        '<div style="text-align:center;margin:20px 0;">'
        f'<img src="{tema["imagem"]}" style="max-width:680px;width:100%;" alt="{tema["titulo"]}">'
        '</div>'
        '<div style="font-size:18px;line-height:1.6;text-align:justify;">'
        f'{texto_html}'
        '</div>'
        '</div>'
    )

    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": tema["titulo"],
            "content": html,
            "labels": tema["labels"]
        },
        isDraft=False
    ).execute()

    registrar_publicacao()
    print("✅ Post publicado com imagem visível")

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    if pode_publicar():
        publicar()
    else:
        print("⏹️ Execução finalizada sem publicação")
