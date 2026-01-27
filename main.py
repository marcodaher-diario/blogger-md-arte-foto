import os
import json
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
# GERADOR DE CONTEÚDO (SEM IA)
# ===============================
def gerar_conteudo_fotografia():
    print("📝 Gerando conteúdo automático (sem IA)")

    titulo = "Erros comuns na fotografia amadora e como evitá-los"

    introducao = (
        "Muitos iniciantes na fotografia enfrentam dificuldades logo no começo, "
        "não por falta de equipamento, mas por cometer erros simples que afetam "
        "diretamente a qualidade das fotos. Conhecer esses erros é o primeiro "
        "passo para evoluir e obter imagens mais nítidas, bem iluminadas e "
        "visualmente agradáveis."
    )

    erros = [
        (
            "Usar ISO alto sem necessidade",
            "Um erro comum é aumentar o ISO mesmo quando há boa iluminação. "
            "Isso gera ruído desnecessário na imagem, reduzindo a qualidade da foto."
        ),
        (
            "Ignorar a iluminação do ambiente",
            "Fotografar sem observar a direção, intensidade e qualidade da luz "
            "resulta em imagens escuras, estouradas ou sem contraste."
        ),
        (
            "Não prestar atenção no foco",
            "Fotos desfocadas acontecem quando o fotógrafo não confere o ponto de foco, "
            "principalmente em retratos ou objetos próximos."
        ),
        (
            "Confiar apenas no modo automático",
            "O modo automático facilita, mas limita o controle criativo. "
            "Aprender os ajustes básicos ajuda a melhorar significativamente os resultados."
        ),
        (
            "Não estabilizar a câmera",
            "Segurar a câmera de forma incorreta ou fotografar em baixa velocidade "
            "sem apoio causa imagens tremidas."
        ),
    ]

    dicas = [
        "Observe a luz antes de fotografar",
        "Use o ISO mais baixo possível",
        "Verifique sempre o foco antes do clique",
        "Experimente os modos semi-manuais da câmera",
        "Utilize tripé ou apoio em baixa luz",
    ]

    conclusao = (
        "Evitar esses erros comuns permite que o fotógrafo iniciante evolua mais rápido "
        "e aproveite melhor o potencial da câmera. Com prática, atenção aos detalhes "
        "e ajustes simples, é possível obter fotos muito melhores sem precisar "
        "de equipamentos caros."
    )

    # ===============================
    # MONTAGEM DO TEXTO FINAL
    # ===============================
    artigo = []
    artigo.append(introducao)
    artigo.append("\n\nErros mais comuns na fotografia amadora:\n")

    for titulo_erro, descricao in erros:
        artigo.append(f"{titulo_erro}\n{descricao}")

    artigo.append("\n\nDicas práticas para evitar esses erros:\n")

    for dica in dicas:
        artigo.append(f"- {dica}")

    artigo.append("\n\n" + conclusao)

    artigo_final = "\n\n".join(artigo)

    # ===============================
    # SALVA OS ARQUIVOS
    # ===============================
    with open(f"{CONTENT_DIR}/titulo.txt", "w", encoding="utf-8") as f:
        f.write(titulo)

    with open(f"{CONTENT_DIR}/artigo_pronto.txt", "w", encoding="utf-8") as f:
        f.write(artigo_final)

    print("✅ Conteúdo gerado com sucesso")
    print(f"📝 Título: {titulo}")
    print(f"📄 Artigo: {len(artigo_final)} caracteres")

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
# FORMATA ARTIGO EM HTML
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
# PUBLICA NO BLOGGER
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
# EXECUÇÃO PRINCIPAL
# ===============================
if __name__ == "__main__":
    print("🚀 Iniciando FASE 1 - Fotografia sem IA")
    gerar_conteudo_fotografia()
    publicar_post()
