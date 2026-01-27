import os
import json
import random
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# ===============================
# CONFIGURAÇÕES GERAIS
# ===============================
SCOPES = ["https://www.googleapis.com/auth/blogger"]
BLOG_ID = "5852420775961497718"
CONTENT_DIR = "content"

print("📂 Diretório atual:", os.getcwd())
os.makedirs(CONTENT_DIR, exist_ok=True)
print("📁 Arquivos em content:", os.listdir(CONTENT_DIR))

# ===============================
# TEMAS DINÂMICOS DE FOTOGRAFIA
# ===============================
TEMAS = {
    "erros_fotografia": {
        "titulo": "Erros comuns na fotografia amadora e como evitá-los",
        "introducao": (
            "Muitos iniciantes na fotografia enfrentam dificuldades logo no começo, "
            "não por falta de equipamento, mas por cometer erros simples que afetam "
            "diretamente a qualidade das fotos."
        ),
        "itens": [
            ("Usar ISO alto sem necessidade",
             "Aumentar o ISO sem necessidade gera ruído e reduz a qualidade da imagem."),
            ("Ignorar a iluminação",
             "Não observar a luz resulta em fotos escuras, estouradas ou sem contraste."),
            ("Fotos sem foco",
             "A falta de atenção ao foco é uma das principais causas de imagens ruins."),
            ("Confiar apenas no modo automático",
             "O modo automático limita o controle criativo do fotógrafo."),
            ("Não estabilizar a câmera",
             "Baixa velocidade sem apoio causa fotos tremidas."),
        ],
        "dicas": [
            "Observe a luz antes de fotografar",
            "Use o ISO mais baixo possível",
            "Confira o foco antes do clique",
            "Experimente modos semi-manuais",
            "Use tripé em pouca luz",
        ],
        "conclusao": (
            "Evitar esses erros ajuda o fotógrafo iniciante a evoluir rapidamente e "
            "obter imagens com melhor qualidade."
        ),
    },

    "iso": {
        "titulo": "O que é ISO na fotografia e como usar corretamente",
        "introducao": (
            "O ISO é um dos principais ajustes da câmera e influencia diretamente "
            "na luminosidade e na qualidade da imagem."
        ),
        "itens": [
            ("ISO baixo",
             "Ideal para ambientes bem iluminados, garantindo imagens mais limpas."),
            ("ISO alto",
             "Usado em pouca luz, mas pode gerar ruído."),
            ("Ruído digital",
             "Aumenta conforme o ISO sobe."),
        ],
        "dicas": [
            "Use ISO baixo sempre que possível",
            "Aumente o ISO apenas quando faltar luz",
            "Prefira boa iluminação ao invés de ISO alto",
        ],
        "conclusao": (
            "Entender o ISO permite fotografar melhor em diferentes condições de luz."
        ),
    },

    "abertura": {
        "titulo": "Abertura do diafragma explicada para iniciantes",
        "introducao": (
            "A abertura do diafragma controla a entrada de luz e a profundidade de campo."
        ),
        "itens": [
            ("Abertura grande (f/1.8)",
             "Permite mais luz e fundo desfocado."),
            ("Abertura pequena (f/16)",
             "Menos luz e maior nitidez geral."),
            ("Profundidade de campo",
             "Relacionada diretamente à abertura."),
        ],
        "dicas": [
            "Use abertura grande para retratos",
            "Use abertura pequena para paisagens",
        ],
        "conclusao": (
            "Controlar a abertura melhora o resultado estético das fotos."
        ),
    },
}

# ===============================
# GERADOR DE CONTEÚDO DINÂMICO
# ===============================
def gerar_conteudo_fotografia():
    print("📝 Gerando conteúdo automático (tema dinâmico)")

    tema_key = random.choice(list(TEMAS.keys()))
    tema = TEMAS[tema_key]

    artigo = []
    artigo.append(tema["introducao"])
    artigo.append("\n\nPrincipais pontos:\n")

    for titulo_item, descricao in tema["itens"]:
        artigo.append(f"{titulo_item}\n{descricao}")

    artigo.append("\n\nDicas práticas:\n")

    for dica in tema["dicas"]:
        artigo.append(f"- {dica}")

    artigo.append("\n\n" + tema["conclusao"])

    artigo_final = "\n\n".join(artigo)

    with open(f"{CONTENT_DIR}/titulo.txt", "w", encoding="utf-8") as f:
        f.write(tema["titulo"])

    with open(f"{CONTENT_DIR}/artigo_pronto.txt", "w", encoding="utf-8") as f:
        f.write(artigo_final)

    print("✅ Conteúdo gerado")
    print("🎯 Tema:", tema_key)
    print("📄 Artigo:", len(artigo_final), "caracteres")

# ===============================
# AUTENTICAÇÃO BLOGGER
# ===============================
def autenticar():
    blogger_token = os.getenv("BLOGGER_TOKEN")
    if not blogger_token:
        raise Exception("❌ BLOGGER_TOKEN não encontrado")

    token_info = json.loads(blogger_token)
    return Credentials.from_authorized_user_info(token_info, SCOPES)

# ===============================
# FORMATA HTML
# ===============================
def formatar_artigo_html(texto):
    paragrafos = texto.split("\n\n")
    html = []

    for p in paragrafos:
        p = p.strip()
        if p.startswith("- "):
            html.append(f"<li>{p[2:]}</li>")
        else:
            html.append(f"<p>{p}</p>")

    if any("<li>" in h for h in html):
        html = ["<ul>"] + html + ["</ul>"]

    return "\n".join(html)

# ===============================
# PUBLICAÇÃO
# ===============================
def publicar_post():
    print("🚀 Publicando no Blogger")

    creds = autenticar()
    service = build("blogger", "v3", credentials=creds)

    with open(f"{CONTENT_DIR}/titulo.txt", encoding="utf-8") as f:
        titulo = f.read().strip()

    with open(f"{CONTENT_DIR}/artigo_pronto.txt", encoding="utf-8") as f:
        artigo = f.read().strip()

    with open(f"{CONTENT_DIR}/assinatura.html", encoding="utf-8") as f:
        assinatura = f.read()

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
        body={"title": titulo, "content": conteudo},
        isDraft=False
    ).execute()

    print("✅ Post publicado com sucesso")
    print("🔗 URL:", response.get("url"))

# ===============================
# EXECUÇÃO
# ===============================
if __name__ == "__main__":
    print("🚀 FASE 1 / PASSO 1 - Tema dinâmico")
    gerar_conteudo_fotografia()
    publicar_post()
