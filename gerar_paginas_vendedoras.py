#!/usr/bin/env python3
"""
gerar_paginas_vendedoras.py — SevenIndica · Campanha de Indicação 2026

Gera páginas personalizadas para cada vendedora a partir de
campanha-indicacao.html (fonte única de verdade).

Cada página gerada:
  - Está em campanha-indicacao/{nome}/index.html
  - Exibe um banner de boas-vindas personalizado (ex: "Você foi convidado(a) por Giselle")
  - Redireciona todos os CTAs para https://gentilezaseventech.lovable.app/?ref={nome}

Uso:
    python gerar_paginas_vendedoras.py

URLs geradas (via GitHub Pages):
    https://seventechoficial.com/campanha-indicacao/giselle
    https://seventechoficial.com/campanha-indicacao/josi
    ... etc
"""

from pathlib import Path
import re

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

VENDEDORAS = [
    "giselle",
    "josi",
    "beatriz",
    "beatrizroveri",
    "victoria",
    "bruna",
    "rayanne",
    "nicole",
    "karol",
]

# Mapeamento nome_url → nome de exibição bonito
DISPLAY_NAMES = {
    "giselle":      "Giselle",
    "josi":         "Josi",
    "beatriz":      "Beatriz",
    "beatrizroveri":"Beatriz Roveri",
    "victoria":     "Victoria",
    "bruna":        "Bruna",
    "rayanne":      "Rayanne",
    "nicole":       "Nicole",
    "karol":        "Karol",
}

BASE_HTML     = Path(__file__).parent / "campanha-indicacao.html"
OUTPUT_BASE   = Path(__file__).parent / "campanha-indicacao"
CTA_BASE_URL  = "https://gentilezaseventech.lovable.app/"

# ---------------------------------------------------------------------------
# Banner HTML personalizado
# ---------------------------------------------------------------------------

BANNER_CSS = """
  <!-- ════════ BANNER VENDEDORA ════════ -->
  <style>
    .ref-banner {
      background: var(--dark);
      border-bottom: 2px solid var(--teal);
      text-align: center;
      padding: 10px 5%;
      font-family: 'Poppins', sans-serif;
      font-size: 13px;
      color: rgba(255,255,255,0.75);
      letter-spacing: 0.2px;
    }
    .ref-banner strong {
      color: var(--teal);
      font-weight: 700;
    }
  </style>
"""

def make_banner(display_name: str) -> str:
    return (
        BANNER_CSS +
        f'  <div class="ref-banner">'
        f'Você foi convidado(a) por <strong>{display_name}</strong> · Seventech'
        f'</div>\n'
    )

# ---------------------------------------------------------------------------
# Geração de página
# ---------------------------------------------------------------------------

def gerar_pagina(nome: str) -> None:
    display = DISPLAY_NAMES.get(nome, nome.title())
    cta_url  = f"{CTA_BASE_URL}?ref={nome}"

    html = BASE_HTML.read_text(encoding="utf-8")

    # 1. Substituir todos os CTAs externos pelo link personalizado com ref
    html = html.replace(
        f'href="{CTA_BASE_URL}"',
        f'href="{cta_url}"'
    )

    # 2. Injetar banner logo após a tag <body>
    banner = make_banner(display)
    html = html.replace("<body>", f"<body>\n{banner}", 1)

    # 3. Ajustar caminhos relativos de imagens e assets
    #    A página ficará em campanha-indicacao/{nome}/index.html
    #    então precisamos subir dois níveis para chegar ao root
    html = html.replace('src="images/', 'src="../../images/')
    html = html.replace("src='images/", "src='../../images/")
    html = html.replace('href="favicon.ico"', 'href="../../favicon.ico"')

    # 4. Salvar
    out_dir = OUTPUT_BASE / nome
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.html"
    out_file.write_text(html, encoding="utf-8")

    size_kb = out_file.stat().st_size / 1024
    print(f"  ✅  {nome:15s} → campanha-indicacao/{nome}/index.html  ({size_kb:.0f} KB)")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"\n🚀  Gerando páginas personalizadas para {len(VENDEDORAS)} vendedoras...\n")
    print(f"    Base: {BASE_HTML}")
    print(f"    Saída: {OUTPUT_BASE}/\n")

    for nome in VENDEDORAS:
        gerar_pagina(nome)

    print(f"\n✅  Concluído! {len(VENDEDORAS)} páginas geradas em campanha-indicacao/\n")
    print("URLs de produção:")
    for nome in VENDEDORAS:
        print(f"    https://seventechoficial.com/campanha-indicacao/{nome}")
    print()

if __name__ == "__main__":
    main()
