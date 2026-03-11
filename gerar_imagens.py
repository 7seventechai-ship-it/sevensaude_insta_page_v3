#!/usr/bin/env python3
"""
gerar_imagens.py — SevenIndica · Campanha de Indicação Mês do Consumidor 2026
Gera as 5 imagens da campanha usando Gemini Imagen 3 (imagen-3.0-generate-002).

Uso:
    pip install google-genai pillow python-dotenv
    python gerar_imagens.py

    # Para gerar apenas uma imagem específica:
    python gerar_imagens.py --imagem hero-bg

Saída:
    images/campanha-indicacao/hero-bg.webp
    images/campanha-indicacao/produto-ponto-vr.webp
    images/campanha-indicacao/produto-vale-refeicao-vr.webp
    images/campanha-indicacao/produto-seven-saude.webp
    images/campanha-indicacao/cta-celebracao.webp
"""

import os
import sys
import argparse
from pathlib import Path
from io import BytesIO

# Carrega variáveis do arquivo .env — busca em ordem de prioridade:
# 1. Pasta central: ~/Local-projects/Seventech/gemini/.env  (localização canônica)
# 2. Pasta do próprio script (fallback local)
try:
    from dotenv import load_dotenv
    _env_central = Path.home() / "Local-projects" / "Seventech" / "gemini" / ".env"
    _env_local   = Path(__file__).parent / ".env"
    load_dotenv(_env_central if _env_central.exists() else _env_local)
except ImportError:
    pass  # python-dotenv opcional; GEMINI_API_KEY pode vir do ambiente do sistema

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌  Pacote google-genai não encontrado. Execute: pip install google-genai")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("❌  Pacote Pillow não encontrado. Execute: pip install pillow")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

OUTPUT_DIR = Path(__file__).parent / "images" / "campanha-indicacao"
MODEL = "imagen-4.0-generate-001"

# ---------------------------------------------------------------------------
# Definição das imagens (seguindo BRIEFING_IMAGENS_CAMPANHA_INDICACAO.md)
# ---------------------------------------------------------------------------

IMAGENS = [
    {
        "id": "hero-bg",
        "arquivo": "hero-bg.webp",
        "aspect_ratio": "16:9",
        "prompt": (
            "Professional lifestyle editorial photo of a Brazilian businesswoman, "
            "40 years old, white skin, wearing elegant business casual attire in neutral or cool tones. "
            "She is in a modern premium coworking space or bright corporate office with natural light. "
            "She is confident, in control — either on a phone call, lightly smiling at camera, "
            "or reviewing something with a focused expression. "
            "She is positioned to the RIGHT side of the frame, leaving open space on the left. "
            "Background shows modern office furniture, large windows with soft natural daylight. "
            "Lighting: soft box or natural window light, cool-neutral color temperature (no golden hour). "
            "Photo style: editorial corporate lifestyle, not generic stock. "
            "High resolution, sharp focus on subject, slightly blurred background (shallow depth of field). "
            "No handshakes, no hospitals, no pure white background, no stethoscopes."
        ),
    },
    {
        "id": "produto-ponto-vr",
        "arquivo": "produto-ponto-vr.webp",
        "aspect_ratio": "4:3",
        "prompt": (
            "Editorial lifestyle photo of a Brazilian employee or manager, 25–40 years old, "
            "naturally clocking in or registering their time using a smartphone app or modern digital tablet device. "
            "The gesture is fluid and natural, not posed. "
            "Setting: modern office reception, clean factory floor entrance, or corporate building lobby. "
            "Lighting: real ambient light — clean fluorescent or natural daylight, not studio. "
            "The focus is on the person interacting with the device. "
            "Color mood: cool whites and grays, professional. "
            "No old mechanical punch clocks, no messy environments, no bored expressions."
        ),
    },
    {
        "id": "produto-vale-refeicao-vr",
        "arquivo": "produto-vale-refeicao-vr.webp",
        "aspect_ratio": "4:3",
        "prompt": (
            "Editorial lifestyle photo of a Brazilian person, 25–45 years old, "
            "paying for a meal or food using a contactless card or mobile payment at a casual restaurant, "
            "bakery counter, or supermarket checkout. "
            "The gesture is simple and fluid — tapping the card or phone at the payment terminal. "
            "The scene conveys convenience and lightness, not necessity or stress. "
            "If visible, the card has a green color. "
            "Lighting: warm ambient restaurant or shop light, inviting and comfortable. "
            "Style: editorial lifestyle, authentic, not generic stock. "
            "No fast food settings, no long queues, no rushed expressions."
        ),
    },
    {
        "id": "produto-seven-saude",
        "arquivo": "produto-seven-saude.webp",
        "aspect_ratio": "4:3",
        "prompt": (
            "Editorial lifestyle photo of a Brazilian person, 25–45 years old, "
            "in a telemedicine video consultation — holding a smartphone or looking at a tablet screen "
            "showing a doctor in a video call. "
            "The person looks comfortable, relaxed, and engaged — in a home office, modern apartment, or coworking space. "
            "The device screen is visible but not necessarily readable, just suggested. "
            "Lighting: bright natural daylight, positive and clear tone. "
            "Setting: home, apartment, or professional office — anywhere that is NOT a hospital or clinic. "
            "Style: editorial corporate wellness lifestyle. "
            "No white lab coats, no stethoscopes, no hospital beds, no expressions of pain or worry."
        ),
    },
    {
        "id": "cta-celebracao",
        "arquivo": "cta-celebracao.webp",
        "aspect_ratio": "16:9",
        "prompt": (
            "Editorial lifestyle photo of a Brazilian business professional, manager or entrepreneur, "
            "30–45 years old, in a moment of professional achievement and positive financial result. "
            "They are looking at a smartphone with a satisfied expression, or making a subtle fist pump gesture, "
            "or smiling confidently at the camera — conveying 'I just hit my target' or 'I just received good news'. "
            "Setting: modern office or neutral dark background that works with dark overlay. "
            "Lighting: slightly dramatic or high-contrast — can have moody office lighting. "
            "Style: editorial, authentic — not exaggerated celebration. "
            "No physical money in scene, no confetti, no overly theatrical expressions, no unprofessional settings."
        ),
    },
]

# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        print("❌  Variável de ambiente GEMINI_API_KEY não definida.")
        print("    Execute: export GEMINI_API_KEY='sua_chave_aqui'")
        sys.exit(1)
    return key


def gerar_imagem(client: genai.Client, imagem: dict) -> None:
    arquivo_saida = OUTPUT_DIR / imagem["arquivo"]
    print(f"\n🎨  Gerando {imagem['id']} → {imagem['arquivo']}")
    print(f"    Aspect ratio: {imagem['aspect_ratio']}")

    try:
        response = client.models.generate_images(
            model=MODEL,
            prompt=imagem["prompt"],
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=imagem["aspect_ratio"],
                # safety_filter_level="block_only_high",  # descomente se necessário
            ),
        )

        if not response.generated_images:
            print(f"    ⚠️  Nenhuma imagem gerada para {imagem['id']} (possível bloqueio de filtro).")
            return

        img_bytes = response.generated_images[0].image.image_bytes
        img = Image.open(BytesIO(img_bytes))
        img.save(arquivo_saida, "WEBP", quality=88, method=6)

        tamanho_kb = arquivo_saida.stat().st_size / 1024
        print(f"    ✅  Salvo: {arquivo_saida}  ({tamanho_kb:.0f} KB)")

    except Exception as e:
        print(f"    ❌  Erro ao gerar {imagem['id']}: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Gera imagens da campanha SevenIndica via Gemini Imagen 3"
    )
    parser.add_argument(
        "--imagem",
        help="ID de uma imagem específica para gerar (ex: hero-bg). Omita para gerar todas.",
        choices=[img["id"] for img in IMAGENS],
        default=None,
    )
    args = parser.parse_args()

    # Garante que o diretório de saída existe
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    api_key = get_api_key()
    client = genai.Client(api_key=api_key)

    # Seleciona imagens a gerar
    if args.imagem:
        selecionadas = [img for img in IMAGENS if img["id"] == args.imagem]
    else:
        selecionadas = IMAGENS

    print(f"🚀  SevenIndica — Geração de Imagens via Imagen 3")
    print(f"    Modelo: {MODEL}")
    print(f"    Saída: {OUTPUT_DIR}")
    print(f"    Imagens a gerar: {len(selecionadas)}")
    print(f"    Custo estimado: ~${len(selecionadas) * 0.03:.2f} USD")

    for imagem in selecionadas:
        gerar_imagem(client, imagem)

    print(f"\n✅  Concluído! Imagens salvas em: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
