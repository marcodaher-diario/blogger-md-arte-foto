def montar_html_post(titulo, imagem_url, conteudo_html, assinatura_html):

    html = f"""
    <div style="font-family: Arial; color: #686868;">

        <!-- TÍTULO -->
        <div style="text-align: center; font-size: 24px; font-weight: bold; margin-bottom: 15px;">
            {titulo}
        </div>

        <!-- IMAGEM DE CAPA -->
        <div style="text-align: center;">
            <img src="{imagem_url}" style="max-width: 680px; width: 100%; height: auto;" />
        </div>

        <br><br>

        <!-- CONTEÚDO -->
        <div style="font-size: 12px; text-align: justify;">
            {conteudo_html}
        </div>

        <br><br>

        <!-- ASSINATURA -->
        {assinatura_html}

    </div>
    """

    return html

