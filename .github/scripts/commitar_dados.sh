#!/usr/bin/env bash
# Commita no repositório as mudanças em datalake/ e atualiza o catálogo.
#
# Uso: .github/scripts/commitar_dados.sh "mensagem do commit"
#
# O catálogo é regenerado depois do rebase, para que duas execuções (SIM e clima)
# não gerem conflito nos arquivos CATALOGO.md e catalogo.csv.
set -euo pipefail

msg="${1:?informe a mensagem do commit}"
branch="${GITHUB_REF_NAME:-main}"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

git add --all -- datalake ':(exclude)datalake/CATALOGO.md' ':(exclude)datalake/catalogo.csv'
if ! git diff --cached --quiet; then
  git commit -m "$msg"
else
  echo "Nenhuma mudança nos dados."
fi

for tentativa in 1 2 3; do
  git pull --rebase origin "$branch"
  python catalogar.py --raiz datalake
  git add datalake/CATALOGO.md datalake/catalogo.csv
  if ! git diff --cached --quiet; then
    git commit -m "catálogo: atualização automática"
  fi
  if git push origin "HEAD:${branch}"; then
    exit 0
  fi
  echo "Push recusado (tentativa ${tentativa} de 3); tentando de novo." >&2
  sleep $((tentativa * 5))
done

echo "Não foi possível publicar os dados no repositório." >&2
exit 1
