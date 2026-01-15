def formatar_artigo(texto_bruto):

    linhas = texto_bruto.split("\n")
    html = ""

    for linha in linhas:
        linha = linha.strip()

        if not linha:
            html += "<br>"
            continue

        if linha.isupper():
            html += f"""
            <div style="font-size:16px; font-weight:bold; text-align:left; margin-top:20px;">
                {linha}
            </div>
            """
        else:
            html += f"<p>{linha}</p>"

    return html

