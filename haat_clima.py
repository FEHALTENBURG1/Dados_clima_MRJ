#!/usr/bin/env python3
"""
Índice de calor e métrica HAAT (heat area above threshold) a partir do data lake de clima.

Reproduz, com os dados horários do lago (INMET + Alerta Rio), as variáveis diárias usadas por
Morais et al. (repositório heat_mortality_MRJ_article, arquivo data/temp_df.csv):

  t_med, t_max          média e máximo dos valores horários municipais de temperatura (°C)
  hi_med, hi_max        média e máximo dos valores horários municipais do índice de calor (°C)
  num_hr_32 ... num_hr_44   horas do dia com índice de calor >= limiar
  auc32, auc36          HAAT: soma, nas horas do dia, de max(índice de calor - limiar, 0)  (°C·h)

Como cada pedaço é calculado
  1. Para cada estação e hora, índice de calor com a fórmula do NWS (regressão de Rothfusz com os dois
     ajustes de umidade), exatamente como em 00_aux_functions.R do artigo (calculate_heat_index_celsius).
  2. Valor municipal da hora = média entre as estações com temperatura e umidade válidas naquela hora
     (mínimo de estações por hora: --min-estacoes).
  3. Dia local = UTC-3. Dia com menos de --min-horas horas municipais válidas fica sem valor.

Uso
  python haat_clima.py --raiz datalake/clima --saida haat_diario_municipal.csv
  python haat_clima.py --raiz datalake/clima --ano-ini 2012 --ano-fim 2024 --comparar dados/temp_df.csv
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger("haat")
FUSO_HORAS = -3
LIMIARES_PADRAO = list(range(32, 45))          # 32 ... 44
AUC_LIMIARES = (32, 36)


def indice_calor_celsius(temp_c, umid):
    """Índice de calor (°C) pela fórmula do NWS, igual a calculate_heat_index_celsius() do artigo."""
    tf = np.asarray(temp_c, dtype=float) * 9 / 5 + 32
    rh = np.asarray(umid, dtype=float)
    simples = 0.5 * (tf + 61 + (tf - 68) * 1.2 + rh * 0.094)
    c = [-42.379, 2.04901523, 10.14333127, -0.22475541, -6.83783e-03,
         -5.481717e-02, 1.22874e-03, 8.5282e-04, -1.99e-06]
    reg = (c[0] + c[1] * tf + c[2] * rh + c[3] * tf * rh + c[4] * tf ** 2 + c[5] * rh ** 2
           + c[6] * tf ** 2 * rh + c[7] * tf * rh ** 2 + c[8] * tf ** 2 * rh ** 2)
    with np.errstate(invalid="ignore"):
        aj1 = reg - ((13 - rh) / 4) * np.sqrt((17 - np.abs(tf - 95)) / 17)
        aj2 = reg + ((rh - 85) / 10) * ((87 - tf) / 5)
    hi = np.where(simples < 80, simples,
         np.where((rh < 13) & (tf >= 80) & (tf <= 112), aj1,
         np.where((rh > 85) & (tf >= 80) & (tf <= 87), aj2, reg)))
    hi = np.where(np.isnan(tf) | np.isnan(rh), np.nan, hi)
    return (hi - 32) / 1.8


def _ler_horario(raiz: Path, variavel: str, anos: list[int]) -> pd.DataFrame:
    partes = []
    for ano in anos:
        arq = raiz / "horario" / variavel / f"ano={ano}" / "part-0.parquet"
        if arq.exists():
            partes.append(pd.read_parquet(arq, columns=["fonte", "estacao_id", "dt_utc", "valor"]))
        else:
            log.warning("sem dados de %s em %d (%s)", variavel, ano, arq)
    if not partes:
        return pd.DataFrame(columns=["fonte", "estacao_id", "dt_utc", "valor"])
    return pd.concat(partes, ignore_index=True)


def horario_municipal(raiz: Path, anos: list[int], min_estacoes: int = 3) -> pd.DataFrame:
    """Temperatura e índice de calor municipais por hora (UTC)."""
    t = _ler_horario(raiz, "temperatura", anos)
    u = _ler_horario(raiz, "umidade", anos)
    m = t.merge(u, on=["fonte", "estacao_id", "dt_utc"], suffixes=("_t", "_u"))
    m = m.dropna(subset=["valor_t", "valor_u"])
    m = m[(m["valor_u"] >= 0) & (m["valor_u"] <= 100)]
    m["hi"] = indice_calor_celsius(m["valor_t"], m["valor_u"])
    g = m.groupby("dt_utc")
    h = g.agg(temperatura=("valor_t", "mean"), indice_calor=("hi", "mean"), n_estacoes=("hi", "size"))
    h = h[h["n_estacoes"] >= min_estacoes].reset_index()
    return h


def diario(h: pd.DataFrame, limiares: list[int], min_horas: int = 18) -> pd.DataFrame:
    h = h.copy()
    h["dia"] = (h["dt_utc"] + pd.Timedelta(hours=FUSO_HORAS)).dt.normalize()
    g = h.groupby("dia")
    out = pd.DataFrame({
        "n_horas": g.size(),
        "n_estacoes_medio": g["n_estacoes"].mean().round(1),
        "t_med": g["temperatura"].mean(), "t_max": g["temperatura"].max(),
        "hi_med": g["indice_calor"].mean(), "hi_max": g["indice_calor"].max(),
    })
    for k in limiares:
        out[f"num_hr_{k}"] = g["indice_calor"].apply(lambda s, k=k: int((s >= k).sum()))
    for k in AUC_LIMIARES:
        out[f"auc{k}"] = g["indice_calor"].apply(lambda s, k=k: float((s - k).clip(lower=0).sum()))
    bom = out["n_horas"] >= min_horas
    cols = [c for c in out.columns if c not in ("n_horas", "n_estacoes_medio")]
    out.loc[~bom, cols] = np.nan
    out.index.name = "dia"
    return out.reset_index()


def comparar(meu: pd.DataFrame, caminho: Path) -> pd.DataFrame:
    j = pd.read_csv(caminho, parse_dates=["dia"])
    x = meu.merge(j, on="dia", suffixes=("", "_joao"))
    linhas = []
    for c in ["t_med", "t_max", "hi_med", "hi_max", "num_hr_32", "num_hr_36", "auc32", "auc36"]:
        if c in x and c + "_joao" in x:
            d = (x[c] - x[c + "_joao"]).dropna()
            linhas.append(dict(variavel=c, dias=len(d), correlacao=round(x[c].corr(x[c + "_joao"]), 4),
                               vies=round(d.mean(), 3), erro_absoluto_medio=round(d.abs().mean(), 3)))
    return pd.DataFrame(linhas)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", required=True, help="pasta do lago de clima (a que contém horario/)")
    ap.add_argument("--saida", default="haat_diario_municipal.csv")
    ap.add_argument("--ano-ini", type=int, default=2012)
    ap.add_argument("--ano-fim", type=int, default=2024)
    ap.add_argument("--min-estacoes", type=int, default=3)
    ap.add_argument("--min-horas", type=int, default=18)
    ap.add_argument("--limiares", type=int, nargs="+", default=LIMIARES_PADRAO)
    ap.add_argument("--comparar", help="CSV de Morais et al. (temp_df.csv) para conferir os valores")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    anos = list(range(a.ano_ini, a.ano_fim + 1))
    # um dia local precisa de horas de dois anos UTC (virada de ano): lê um ano antes e depois
    anos_leitura = sorted(set(anos) | {a.ano_ini - 1, a.ano_fim + 1})
    h = horario_municipal(Path(a.raiz), anos_leitura, a.min_estacoes)
    if h.empty:
        sys.exit("Sem dados horários de temperatura e umidade no intervalo.")
    d = diario(h, a.limiares, a.min_horas)
    d = d[(d["dia"] >= f"{a.ano_ini}-01-01") & (d["dia"] <= f"{a.ano_fim}-12-31")]
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    num = d.select_dtypes("number").columns
    d = d.assign(**{c: d[c].round(3) for c in num})
    d.to_csv(a.saida, index=False, date_format="%Y-%m-%d")
    log.info("%d dias gravados em %s (%d sem valor por falta de horas)", len(d), a.saida, int(d["hi_max"].isna().sum()))
    if a.comparar:
        print(comparar(d, Path(a.comparar)).to_string(index=False))


if __name__ == "__main__":
    main()
