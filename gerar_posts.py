import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as ServiceCredentials
from openai import OpenAI

# ===============================
# CONFIGURAÇÕES
# ===============================
SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = "posts"
SCOPES_SHEETS = ["https://www.googleapis.com/auth/spreadsheets"]

TOTAL_POSTS = 30
INTERVALO_DIAS = 3
PALAVRAS_MIN = 800

TEMAS = [
    ("erros_fotografia", "Erros comuns na fotografia amadora"),
    ("iso", "ISO na fotografia para iniciantes"),
    ("abertura", "Abertura do diafragma explicada"),
    ("velocidade", "Velocidade do obturador e movimento"),
    ("composicao", "Composição fotográfica para iniciantes"),
    ("luz_natural", "Luz natural vs luz artificial"),
    ("paisagem", "Fotografia de paisagem para iniciantes"),
    ("retrato", "Fotografia de retrato: primeiros passos"),
    ("fotografia_celular", "Fotografia com celular: dicas práticas"),
    ("equipamentos_iniciantes", "Equipamentos básicos para começar")
]

# ===============================
# AUTENTICAÇÃO
# ===============================
def sheets_service():
    creds_info = json.loads(os.environ["GOOGLE_SHEETS_CREDENTIALS"])
    creds = ServiceCredentials.from_service_account_info(
        creds_info, scopes=SCOPES_SHEETS
    )
    return build("sheets", "v4", credentials=creds)

def openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ===============================
# PROMPT PADRÃO
# ===============================
def montar_prompt(tema):
    return f"""
Você é um redator especialista em fotografia para iniciantes, com linguagem simples, didática e fácil de entender.

Crie um artigo AUTORAL para blog sobre o tema:
{tema}

Requisitos obrigatórios:
- Texto com NO MÍNIMO {PALAVRAS_MIN} palavras.
- Linguagem clara e acessível.
- Texto 100% autoral.
- Não usar HTML.
- Não usar emojis.

Estrutura:
1. Introdução
2. Explicação do conceito
3. Erros comuns
4. Dicas práticas
5. Exemplos simples
6. Conclusão

Além do texto, gere:
A) TÍTULO
B) LABELS (3 a 5, separadas por vírgula)
C) DUAS DESCRIÇÕES DE IMAGENS (descrições, não links)

Formato da resposta:
TÍTULO:
...
TEXTO:
...
IMAGEM 1:
...
IMAGEM 2:
...
LABELS:
...
""".strip()

# ===============================
# PARSER DA RESPOSTA
# ===============================
def parse_resposta(txt):
    def extrair(chave):
        ini = txt.find(chave)
        if ini == -1:
            return ""
        ini += len(chave)
        fim = txt.find("\nIMAGEM", ini)
        if fim == -1:
            fim = len(txt)
        return txt[ini:fim].strip()

    titulo = extrair("TÍTULO:")
    texto = extrair("TEXTO:")
    img1 = extrair("IMAGEM 1:")
    img2 = extrair("IMAGEM 2:")
    labels = extrair("LABELS:")
    return titulo, texto, img1, img2, labels

# ===============================
# INSERIR NA PLANILHA
# ===============================
def append_linha(valores):
    service = sheets_service()
    service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_NAME}!A:I",
        valueInputOption="RAW",
        body={"values": [valores]}
    ).execute()

# ===============================
# EXECUÇÃO
# ===============================
def main():
    client = openai_client()
    hoje = datetime.now().date()

    for i in range(TOTAL_POSTS):
        tema_key, tema_nome = TEMAS[i % len(TEMAS)]
        data_pub = hoje + timedelta(days=i * INTERVALO_DIAS)

        prompt = montar_prompt(tema_nome)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        conteudo = resp.choices[0].message.content
        titulo, texto, img1_desc, img2_desc, labels = parse_resposta(conteudo)

        # nomes de arquivos sugeridos (você pode gerar as imagens depois)
        img1_nome = f"{tema_key}_{i+1:02d}_01.jpg"
        img2_nome = f"{tema_key}_{i+1:02d}_02.jpg"

        linha = [
            i + 1,
            data_pub.strftime("%Y-%m-%d"),
            tema_key,
            titulo,
            texto,
            img1_nome,
            img2_nome,
            labels.replace(" ", ""),
            "pendente"
        ]

        append_linha(linha)
        print(f"✅ Post {i+1}/{TOTAL_POSTS} criado: {titulo}")

if __name__ == "__main__":
    main()
