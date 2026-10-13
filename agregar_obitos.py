#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agrega os óbitos por OCORRÊNCIA no MRJ em contagens diárias (arquivo leve para o painel).

Entrada : datalake/silver/sim/ocorrencia_mrj/ano_arquivo=AAAA/part-0.parquet
Saída   : obitos_diarios_ocorrencia_mrj.csv  (dia, faixa_etaria, cid_capitulo, cid_capitulo_desc, n)

Só conta dias com data de óbito válida. Dias sem óbito em uma célula simplesmente não
aparecem; o painel completa com zero.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

COLS = ["DTOBITO", "idade_anos", "cid_capitulo", "cid_capitulo_desc", "ocorrencia_mrj"]


def agregar(raiz: Path) -> pd.DataFrame:
    base = raiz / "silver" / "sim" / "ocorrencia_mrj"
    arqs = sorted(base.glob("ano_arquivo=*/part-0.parquet"))
    if not arqs:
        raise FileNotFoundError(f"Nenhuma partição em {base}")
    partes = []
    for arq in arqs:
        df = pd.read_parquet(arq, columns=COLS)
        df = df[df["ocorrencia_mrj"].astype(bool)]
        df = df[df["DTOBITO"].notna()].copy()
        idade = pd.to_numeric(df["idade_anos"], errors="coerce")
        df["faixa_etaria"] = "Idade ignorada"
        df.loc[idade < 65, "faixa_etaria"] = "0-64 anos"
        df.loc[idade >= 65, "faixa_etaria"] = "65+ anos"
        df["dia"] = pd.to_datetime(df["DTOBITO"]).dt.normalize()
        df["cid_capitulo"] = df["cid_capitulo"].astype("string").fillna("Sem capítulo")
        df["cid_capitulo_desc"] = df["cid_capitulo_desc"].astype("string").fillna("Sem capítulo")
        partes.append(
            df.groupby(["dia", "faixa_etaria", "cid_capitulo", "cid_capitulo_desc"], observed=True)
            .size().rename("n").reset_index()
        )
    out = pd.concat(partes, ignore_index=True)
    # um óbito pode estar em arquivo de ano diferente do ano do óbito (data de entrada); soma por célula
    out = (out.groupby(["dia", "faixa_etaria", "cid_capitulo", "cid_capitulo_desc"], as_index=False)["n"].sum()
              .sort_values(["dia", "faixa_etaria", "cid_capitulo"]))
    out["dia"] = out["dia"].dt.strftime("%Y-%m-%d")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raiz", default="datalake", type=Path)
    ap.add_argument("--saida", default="obitos_diarios_ocorrencia_mrj.csv", type=Path)
    a = ap.parse_args()
    out = agregar(a.raiz)
    out.to_csv(a.saida, index=False)
    print(f"{len(out):,} linhas | {out['dia'].min()} a {out['dia'].max()} | {int(out['n'].sum()):,} óbitos -> {a.saida}")


if __name__ == "__main__":
    main()
