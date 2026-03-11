#!/bin/bash
# deploy.sh — sobe todas as alterações para produção
# Uso: ./deploy.sh "mensagem do commit"
#      ./deploy.sh  (usa mensagem padrão)

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

MSG="${1:-chore: atualiza arquivos do projeto}"

echo "🔄  Regenerando páginas das vendedoras..."
python3 gerar_paginas_vendedoras.py

echo "📦  Staging..."
git add -A -- ':!.env' ':!*.env'   # garante que .env nunca entre

echo "📝  Commit: $MSG"
git commit -m "$MSG" || echo "ℹ️  Nada novo para commitar."

echo "🚀  Push para produção..."
git push

echo "✅  Deploy concluído!"
