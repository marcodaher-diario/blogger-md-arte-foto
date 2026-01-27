import os
import json
import tempfile
import requests
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload

# ===============================
# CONFIGURAÇÕES
# ===============================
SCOPES = ["https://www.googleapis.com/auth/blogger"]
BLOG_ID = "5852420775961497718"
CONTENT_DIR = "content"

FILA_PATH = os.path.join(CONTENT_DIR, "fila_temas.json")
CONTROLE_PATH = os.path.join(CONTENT_DIR, "controle_publicacao.json")

INTERVALO_DIAS = 3

os.makedirs(CONTENT_DIR, exist_ok=True)

# ===============================
# TEMAS
# ===============================
TEMAS = ["erros_fotografia"]

CONTEUDO = {
    "erros_fotografia": {
        "titulo": "Erros comuns na fotografia amadora e como evitá-los",
        "imagem": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Photographer_with_camera.jpg",
        "labels": ["Fotografia", "Iniciantes", "Erros Comuns"],
        "texto": """Muitos iniciantes cometem erros simples que afetam diretamente a qualidade das fotos.

ISO alto sem necessidade gera ruído e perda de qualidade.
Ignorar a luz resulta em fotos mal iluminadas.
Fotos sem foco comprometem o resultado final.

Dicas práticas:
Observe a iluminação.
Use ISO baixo sempre que possível.
Confira o foco antes do clique.

Evitar esses erros ajuda a evoluir rapidamente na fotografia."""
    }
}

# ===============================
# CONTROLE DE DATA
# ===============================
def pode_publicar():
    if not os.path.exists(CONTROLE_PATH):
        return True
    dados = json.load(open(CONTROLE_PATH))
    ultima = datetime.fromisoformat(dados["ultima_publicacao"])
    return datetime.now() >= ultima + timedelta(days=INTERVALO_DIAS)

def registrar_publicacao():
    json.dump(
        {"ultima_publicacao": datetime.now().isoformat()},
        open(CONTROLE_PATH, "w"),
        indent=2
    )

# ===============================
# FILA
# ===============================
def obter_tema():
    if not os.path.exists(FILA_PATH):
        fila = TEMAS.copy()
    else:
        fila = json.load(open(FILA_PATH))

    tema = fila.pop(0)
    json.dump(fila or TEMAS.copy(), open(FILA_PATH, "w"), indent=2)
    return tema

# ===============================
# AUTENTICAÇÃO
# ===============================
def autenticar():
    token = os.getenv("BLOGGER_TOKEN")
    if not token:
        raise Exception("BLOGGER_TOKEN ausente")
    return Credentials.from_authorized_user_info(json.loads(token), SCOPES)

# ===============================
# UPLOAD DE IMAGEM PARA BLOGGER
# ===============================
def upload_imagem(service, image_url):
    response = requests.get(image_url, timeout=20)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    media = MediaFileUpload(tmp_path, mimetype="image/jpeg")
    imagem = service.posts().insert(
        blogId=BLOG_ID,
        body={"title": "Imagem automática"},
        media_body=media
    ).execute()

    os.remove(tmp_path)

    return imagem["url"]

# ===============================
# PUBLICAÇÃO
# ===============================
def publicar():
    tema_key = obter_tema()
    tema = CONTEUDO[tema_key]

    creds = autenticar()
    service = build("blogger", "v3", credentials=creds)

    print("⬆️ Enviando imagem para o Blogger...")
    imagem_url = upload_imagem(service, tema["imagem"])

    html = f"""
<div class="post-body entry-content">
<h1 style="text-align:center;">{tema["titulo"]}</h1>
<div style="text-align:center;margin:20px 0;">
<img src="{imagem_url}" style="max-width:680px;width:100%;">
</div>
<div style="font-size:18px;line-height:1.6;text-align:justify;">
{tema["texto"].replace(chr(10), '<br>')}
</div>
</div>
"""

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
    print("✅ Post publicado com imagem hospedada no Blogger")

# ======================
