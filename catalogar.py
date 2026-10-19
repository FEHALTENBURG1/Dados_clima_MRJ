#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o catálogo do data lake do município do Rio de Janeiro.

Entrada : datalake/ (Parquet particionado por ano e alguns CSV)
Saída   : datalake/CATALOGO.md   (leitura humana)
          datalake/catalogo.csv  (leitura por máquina, uma linha por conjunto)

O catálogo só lê os metadados dos arquivos Parquet (número de linhas, colunas e
tamanho), sem carregar os dados. Não grava data nem hora, para que uma execução
sem dados novos não produza um commit.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import pyarrow.parquet as pq

# Conjuntos Parquet: (pasta relativa, rótulo de partição, descrição)
CONJUNTOS_PARQUET = [
    ("silver/sim/ocorrencia_mrj", "ano_arquivo",
     "Declarações de óbito do SIM com ocorrência no município do Rio de Janeiro (código IBGE 330455)."),
    ("silver/sim/residencia_mrj", "ano_arquivo",
     "Declarações de óbito do SIM de residentes no município do Rio de Janeiro, qualquer que seja o local de ocorrência."),
]
FONTE_SIM = "OpenDATASUS, Sistema de Informações sobre Mortalidade (SIM), Ministério da Saúde"
FONTE_CLIMA = "INMET e Alerta Rio (Prefeitura do Rio de Janeiro)"

DESCRICAO_CLIMA = {
    "horario": "Valor horário por estação, hora em UTC.",
    "diario": "Resumo diário por estação, dia local (UTC-3).",
    "municipal": "Média das estações do município por dia local.",
}

CSVS = [
    ("clima_municipal_diario.csv", "dia", FONTE_CLIMA, "Tabela larga com o clima municipal diário (todas as variáveis)."),
    ("haat_diario_municipal.csv", "dia", FONTE_CLIMA,
     "Índice de calor e métrica HAAT diários do município, calculados a partir do clima municipal."),
    ("obitos_diarios_ocorrencia_mrj.csv", "dia", FONTE_SIM,
     "Contagem diária de óbitos por ocorrência, por faixa etária e capítulo da CID-10."),
    ("clima/estacoes.csv", None, FONTE_CLIMA, "Cadastro das estações meteorológicas usadas."),
    ("qa/resumo_ocorrencia.csv", None, FONTE_SIM, "Controle de qualidade por ano: óbitos no Brasil e no recorte de ocorrência."),
    ("qa/resumo_residencia.csv", None, FONTE_SIM, "Controle de qualidade por ano: óbitos no Brasil e no recorte de residência."),
    ("qa/resumo_clima.csv", None, FONTE_CLIMA, "Controle de qualidade do clima por estação, ano e variável."),
]


def _mb(n: int) -> float:
    return round(n / 1024 / 1024, 2)


def _parquet(pasta: Path) -> dict | None:
    arqs = sorted(pasta.glob("*=*/part-0.parquet"))
    if not arqs:
        return None
    linhas = 0
    for a in arqs:
        linhas += pq.ParquetFile(a).metadata.num_rows
    anos = sorted(int(re.search(r"=(\d{4})", a.parent.name).group(1)) for a in arqs)
    esquema = pq.ParquetFile(arqs[-1]).schema_arrow
    return {
        "arquivos": len(arqs),
        "linhas": linhas,
        "ano_inicio": anos[0],
        "ano_fim": anos[-1],
        "mb": _mb(sum(a.stat().st_size for a in arqs)),
        "colunas": [f.name for f in esquema],
    }


def _csv(arq: Path, col_data: str | None) -> dict:
    with arq.open(encoding="utf-8", newline="") as f:
        leitor = csv.reader(f)
        cab = next(leitor)
        n = 0
        primeiro = ultimo = ""
        i = cab.index(col_data) if col_data and col_data in cab else None
        for linha in leitor:
            n += 1
            if i is not None and linha[i]:
                v = linha[i]
                if not primeiro or v < primeiro:
                    primeiro = v
                if not ultimo or v > ultimo:
                    ultimo = v
    return {"linhas": n, "mb": _mb(arq.stat().st_size), "colunas": cab, "de": primeiro, "ate": ultimo}


def montar(raiz: Path) -> list[dict]:
    regs: list[dict] = []
    for rel, part, desc in CONJUNTOS_PARQUET:
        m = _parquet(raiz / rel)
        if m:
            regs.append({"conjunto": rel, "formato": "parquet", "particao": part, "fonte": FONTE_SIM,
                         "descricao": desc, **m})
    clima = raiz / "clima"
    for camada in ("horario", "diario", "municipal"):
        base = clima / camada
        if not base.is_dir():
            continue
        for var in sorted(p for p in base.iterdir() if p.is_dir()):
            m = _parquet(var)
            if m:
                regs.append({"conjunto": f"clima/{camada}/{var.name}", "formato": "parquet", "particao": "ano",
                             "fonte": FONTE_CLIMA, "descricao": f"{DESCRICAO_CLIMA[camada]} Variável: {var.name}.", **m})
    for rel, col_data, fonte, desc in CSVS:
        arq = raiz / rel
        if arq.is_file():
            m = _csv(arq, col_data)
            regs.append({"conjunto": rel, "formato": "csv", "particao": "", "fonte": fonte, "descricao": desc,
                         "arquivos": 1, "linhas": m["linhas"], "ano_inicio": m["de"][:4] if m["de"] else "",
                         "ano_fim": m["ate"][:4] if m["ate"] else "", "mb": m["mb"], "colunas": m["colunas"],
                         "de": m["de"], "ate": m["ate"]})
    return regs


def escrever_csv(regs: list[dict], saida: Path) -> None:
    campos = ["conjunto", "formato", "particao", "fonte", "arquivos", "linhas", "ano_inicio", "ano_fim", "de", "ate", "mb", "descricao"]
    with saida.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in regs:
            w.writerow({**{c: "" for c in campos}, **r})


def _n(x: int) -> str:
    return f"{x:,}".replace(",", ".")


def escrever_md(regs: list[dict], saida: Path) -> None:
    L: list[str] = []
    L.append("# Catálogo do data lake do município do Rio de Janeiro\n")
    L.append("Gerado por `catalogar.py` a cada atualização. Não edite à mão.\n")
    grupos = [
        ("Mortalidade (SIM)", lambda r: r["conjunto"].startswith("silver/sim/")),
        ("Clima", lambda r: r["conjunto"].startswith("clima/") and r["formato"] == "parquet"),
        ("Tabelas derivadas e controle de qualidade", lambda r: r["formato"] == "csv"),
    ]
    for titulo, filtro in grupos:
        sel = [r for r in regs if filtro(r)]
        if not sel:
            continue
        L.append(f"\n## {titulo}\n")
        L.append("| Conjunto | Formato | Partição | Arquivos | Linhas | Período | Tamanho (MB) |")
        L.append("|---|---|---|---:|---:|---|---:|")
        for r in sel:
            if r["formato"] == "csv" and r.get("de"):
                periodo = f"{r['de']} a {r['ate']}"
            elif r["ano_inicio"] != "":
                periodo = f"{r['ano_inicio']} a {r['ano_fim']}"
            else:
                periodo = ""
            tam = f"{r['mb']:.1f}".replace(".", ",")
            L.append(f"| `{r['conjunto']}` | {r['formato']} | {r['particao'] or 'sem partição'} | {r['arquivos']} | "
                     f"{_n(r['linhas'])} | {periodo} | {tam} |")
    L.append("\n## Descrição e colunas\n")
    for r in regs:
        L.append(f"<details><summary><code>{r['conjunto']}</code></summary>\n")
        L.append(f"{r['descricao']}\n")
        L.append(f"Fonte: {r['fonte']}.\n")
        L.append(f"Colunas ({len(r['colunas'])}): " + ", ".join(f"`{c}`" for c in r["colunas"]) + "\n")
        L.append("</details>\n")
    saida.write_text("\n".join(L), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raiz", default="datalake", type=Path)
    a = ap.parse_args()
    regs = montar(a.raiz)
    escrever_csv(regs, a.raiz / "catalogo.csv")
    escrever_md(regs, a.raiz / "CATALOGO.md")
    print(f"{len(regs)} conjuntos catalogados em {a.raiz}")


if __name__ == "__main__":
    main()
