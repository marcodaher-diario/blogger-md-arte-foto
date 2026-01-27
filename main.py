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

INTERVALO_DIAS = 0  # para teste

os.makedirs(CONTENT_DIR, exist_ok=True)

# ===============================
# TEMAS
# ===============================
TEMAS = ["erros_fotografia"]

CONTEUDO = {
    "erros_fotografia": {
        "titulo": "Erros comuns na fotografia amadora e como evitá-los",
        "imagem": "https://images.unsplash.com/photo-1519183071298-a2962be96c5f",
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

    print(f"⏳ Última publicação: {ultima}")
    print(f"📅 Próxima permitida: {proxima}")

    return datetime.now() >= proxima

def registrar_publicacao():
    with open(CONTROLE_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {"ultima_publicacao": datetime.now().isoformat()},
            f,
            indent=2,
            ensure_ascii=False
        )
    print("📁 controle_publicacao.json criado/atualizado")

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
    print("🚀 Iniciando publicação")

    tema_key = obter_tema()
    tema = CONTEUDO[tema_key]

    creds = autenticar()
    service = build("blogger", "v3", credentials=creds)

    html = f"""
<div class="post-body entry-content">
<h1 style="
