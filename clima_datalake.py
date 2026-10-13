#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data lake de clima - Município do Rio de Janeiro

Fontes
------
INMET      : dados históricos anuais (zip com todas as estações do país). Usadas as 4 estações
             automáticas do município: A602 Marambaia, A621 Vila Militar, A636 Jacarepaguá,
             A652 Forte de Copacabana. Dados horários, hora em UTC.
Alerta Rio : dados meteorológicos das estações do Sistema Alerta Rio (Prefeitura do Rio),
             leituras a cada 5 ou 15 min (varia por ano), hora local (UTC-3, sem horário de verão).

Estrutura (um conjunto de dados por tipo de aferição)
-----------------------------------------------------
clima/horario/<variavel>/ano=AAAA/part-0.parquet    por estação, 1 linha por hora (UTC)
clima/diario/<variavel>/ano=AAAA/part-0.parquet     por estação, 1 linha por dia local
clima/municipal/<variavel>/ano=AAAA/part-0.parquet  média das estações do município, por dia local
clima/estacoes.csv                                   cadastro das estações
clima_municipal_diario.csv                           tabela larga com a média municipal diária (todas as variáveis)
qa/resumo_clima.csv                                  cobertura e faixas de valores por estação/ano/variável

Convenções
----------
- Hora: dt_utc é o carimbo da hora em UTC. Dia local = (dt_utc - 3 h). O Brasil usa UTC-3 fixo
  desde 2019 e as séries do Alerta Rio são normalizadas para horário padrão, então o fuso fixo vale
  para todo o período.
- INMET carimba a hora cheia (precipitação = acumulado da hora que termina no carimbo). O Alerta Rio é
  agregado pela mesma regra: o carimbo é o fim da hora (leituras em (H-1, H]).
- Valores ausentes (-9999, ND, vazio) viram nulo. Valores fora de faixa física também viram nulo e
  são contados no QA.
- Dia local só recebe estatística com pelo menos MIN_HORAS_DIA horas com valor (18; para radiação, que só
  existe de dia, 8); abaixo disso fica nulo.

Uso
---
python clima_datalake.py --anos 2023 2024 2025 2026
python clima_datalake.py --ano-ini 2006 --ano-fim 2026
python clima_datalake.py --fontes inmet --anos 2024
"""
from __future__ import annotations

import argparse
import io
import logging
import re
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests

log = logging.getLogger("clima")

ANO_INI_PADRAO = 2006
FUSO_HORAS = 3          # UTC-3
MIN_HORAS_DIA = 18

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"}

# --------------------------------------------------------------------------
# Variáveis
# --------------------------------------------------------------------------
# nome -> (unidade, faixa física válida, estatísticas diárias, estatística principal)
VARIAVEIS: dict[str, dict] = {
    "temperatura":       dict(un="°C",    faixa=(-5, 46),    stats=["media", "min", "max"], desc="Temperatura do ar (bulbo seco)"),
    "temperatura_max":   dict(un="°C",    faixa=(-5, 46),    stats=["max"],                 desc="Temperatura máxima na hora"),
    "temperatura_min":   dict(un="°C",    faixa=(-5, 50),    stats=["min"],                 desc="Temperatura mínima na hora"),
    "ponto_orvalho":     dict(un="°C",    faixa=(-15, 40),   stats=["media"],               desc="Temperatura do ponto de orvalho"),
    "umidade":           dict(un="%",     faixa=(1, 100),    stats=["media", "min", "max"], desc="Umidade relativa do ar"),
    "precipitacao":      dict(un="mm",    faixa=(0, 300),    stats=["soma"],                desc="Precipitação (acumulado na hora)"),
    "pressao":           dict(un="hPa",   faixa=(900, 1100), stats=["media"],               desc="Pressão atmosférica na estação"),
    "vento_velocidade":  dict(un="m/s",   faixa=(0, 60),     stats=["media", "max"],        desc="Velocidade do vento"),
    "vento_direcao":     dict(un="graus", faixa=(0, 360),    stats=["media"],               desc="Direção do vento (média circular)"),
    "vento_rajada":      dict(un="m/s",   faixa=(0, 90),     stats=["max"],                 desc="Rajada máxima do vento"),
    "radiacao":          dict(un="kJ/m²", faixa=(-50, 5000), stats=["soma"],                desc="Radiação global (acumulado na hora)", min_horas=8),
}

# --------------------------------------------------------------------------
# Estações
# --------------------------------------------------------------------------
INMET_ESTACOES = {"A602", "A621", "A636", "A652"}

# id do formulário do Alerta Rio -> (id no lago, nome, lat, lon, altitude)
ALERTARIO = {
    1:  ("AR01", "Vidigal",           None,      None,      None),
    11: ("AR11", "Irajá",             -22.82694, -43.33694, 20.0),
    16: ("AR16", "Jardim Botânico",   -22.97278, -43.22389, 0.0),
    19: ("AR19", "Barra/Riocentro",   -22.97721, -43.39155, 0.0),
    20: ("AR20", "Guaratiba",         -23.05028, -43.59472, 0.0),
    22: ("AR22", "Santa Cruz",        -22.90944, -43.68444, 15.0),
    28: ("AR28", "Alto da Boa Vista", -22.96583, -43.27833, 355.0),
    32: ("AR32", "São Cristóvão",     -22.89667, -43.22167, 25.0),
}
URL_INMET = "https://portal.inmet.gov.br/uploads/dadoshistoricos/{ano}.zip"
URL_ALERTARIO = "http://websempre.rio.rj.gov.br/dados/pluviometricos/met/"

# posição das colunas nos CSVs do INMET (estável de 2007 a 2026) -> (variável, fator)
INMET_POS = {
    2: "precipitacao", 3: "pressao", 6: "radiacao", 7: "temperatura", 8: "ponto_orvalho",
    9: "temperatura_max", 10: "temperatura_min", 15: "umidade", 16: "vento_direcao",
    17: "vento_rajada", 18: "vento_velocidade",
}
INMET_PALAVRAS = {  # confere o cabeçalho para falhar cedo se o layout mudar
    2: "PRECIPITA", 3: "PRESSAO ATMOSFERICA AO NIVEL", 6: "RADIACAO", 7: "BULBO SECO",
    8: "PONTO DE ORVALHO", 9: "MAXIMA NA HORA", 10: "MINIMA NA HORA", 15: "UMIDADE RELATIVA DO AR",
    16: "DIRE", 17: "RAJADA", 18: "VELOCIDADE",
}


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def _sem_acento(s: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).upper()


def _http(sessao: requests.Session, metodo: str, url: str, tentativas: int = 4, **kw) -> requests.Response:
    ultimo = None
    for t in range(1, tentativas + 1):
        try:
            r = sessao.request(metodo, url, timeout=kw.pop("timeout", 180), **kw)
            r.raise_for_status()
            return r
        except Exception as e:  # noqa: BLE001
            ultimo = e
            log.warning("  tentativa %d/%d falhou (%s): %s", t, tentativas, url, e)
            time.sleep(4 * t)
    raise RuntimeError(f"Falha em {url}: {ultimo}")


def _media_circular(graus: pd.Series) -> float:
    g = graus.dropna()
    if g.empty:
        return np.nan
    r = np.deg2rad(g.to_numpy(float))
    ang = np.degrees(np.arctan2(np.sin(r).mean(), np.cos(r).mean()))
    return float(ang % 360)


def _numero(s: pd.Series) -> pd.Series:
    """Texto com vírgula decimal ou ponto, 'ND', '-9999' e vazio -> float com NaN."""
    t = s.astype("string").str.strip().str.replace(",", ".", regex=False)
    v = pd.to_numeric(t, errors="coerce")
    return v.mask(v <= -9990)


# --------------------------------------------------------------------------
# INMET
# --------------------------------------------------------------------------
def baixar_inmet(ano: int, pasta: Path, forcar: bool = False) -> Path:
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"inmet_{ano}.zip"
    hoje = datetime.now().year
    if destino.exists() and not forcar and ano < hoje:
        return destino
    url = URL_INMET.format(ano=ano)
    log.info("INMET %d: baixando %s", ano, url)
    s = requests.Session()
    s.headers.update(UA)
    ultimo = None
    for t in range(1, 4):
        try:
            with s.get(url, stream=True, timeout=(30, 300)) as r:
                r.raise_for_status()
                tmp = destino.with_suffix(".part")
                with open(tmp, "wb") as f:
                    for bloco in r.iter_content(1 << 20):
                        f.write(bloco)
            tmp.replace(destino)
            return destino
        except Exception as e:  # noqa: BLE001
            ultimo = e
            log.warning("  tentativa %d/3 falhou: %s", t, e)
            time.sleep(5 * t)
    raise RuntimeError(f"Falha ao baixar {url}: {ultimo}")


def _fim_do_arquivo_inmet(nome: str) -> datetime:
    m = re.search(r"_A_(\d{2})-(\d{2})-(\d{4})\.CSV$", nome, flags=re.I)
    return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else datetime.min


def _ler_csv_inmet(raw: bytes, nome: str) -> tuple[dict, pd.DataFrame]:
    texto = raw.decode("latin-1")
    linhas = texto.splitlines()
    meta: dict = {}
    ini = None
    for i, l in enumerate(linhas[:30]):
        if re.match(r"^DATA\s*(\(|;)", l.upper()) and "HORA" in l.upper():
            ini = i
            break
        if ":;" in l:
            k, v = l.split(":;", 1)
            meta[_sem_acento(k).strip()] = v.strip().rstrip(";")
    if ini is None:
        raise ValueError(f"{nome}: cabeçalho de dados não encontrado")
    cab = [_sem_acento(c) for c in linhas[ini].split(";")]
    for pos, palavra in INMET_PALAVRAS.items():
        if pos >= len(cab) or palavra not in cab[pos]:
            raise ValueError(f"{nome}: coluna {pos} ('{cab[pos] if pos < len(cab) else '?'}') não contém '{palavra}'; "
                             "o layout do INMET mudou")
    df = pd.read_csv(io.StringIO("\n".join(linhas[ini + 1:])), sep=";", header=None, dtype=str,
                     keep_default_na=False, usecols=range(19))
    return meta, df


def _coord(txt: str | None) -> float | None:
    try:
        return float(str(txt).replace(",", "."))
    except (TypeError, ValueError):
        return None


def processar_inmet(ano: int, zip_path: Path) -> tuple[pd.DataFrame, list[dict]]:
    """Devolve (longo: estacao_id, estacao_nome, variavel, dt_utc, valor, n_obs) e cadastro."""
    escolhidos: dict[str, str] = {}
    with zipfile.ZipFile(zip_path) as z:
        for nome in z.namelist():
            base = nome.rsplit("/", 1)[-1]
            m = re.match(r"INMET_[A-Z]{2}_RJ_(A\d{3})_", base, flags=re.I)
            if not m or m.group(1).upper() not in INMET_ESTACOES:
                continue
            cod = m.group(1).upper()
            # o zip do ano corrente traz várias versões do mesmo arquivo: fica a mais recente
            if cod not in escolhidos or _fim_do_arquivo_inmet(base) > _fim_do_arquivo_inmet(escolhidos[cod].rsplit("/", 1)[-1]):
                escolhidos[cod] = nome
        partes, cadastro = [], []
        for cod, nome in sorted(escolhidos.items()):
            meta, df = _ler_csv_inmet(z.read(nome), nome)
            data = df[0].str.strip().str.replace("/", "-", regex=False)
            hora = df[1].str.extract(r"(\d{1,2}):?(\d{2})").fillna("0")
            hhmm = hora[0].str.zfill(2) + hora[1].str.zfill(2)
            dt = pd.to_datetime(data + " " + hhmm, format="%Y-%m-%d %H%M", errors="coerce")
            nome_est = meta.get("ESTACAO", cod)
            cadastro.append(dict(fonte="INMET", estacao_id=cod, estacao_nome=nome_est,
                                 latitude=_coord(meta.get("LATITUDE")), longitude=_coord(meta.get("LONGITUDE")),
                                 altitude=_coord(meta.get("ALTITUDE"))))
            for pos, var in INMET_POS.items():
                v = pd.DataFrame({"dt_utc": dt, "valor": _numero(df[pos])})
                v = v[v["dt_utc"].notna()]
                v["estacao_id"], v["estacao_nome"], v["variavel"], v["n_obs"] = cod, nome_est, var, 1
                partes.append(v)
    if not partes:
        return pd.DataFrame(), cadastro
    return pd.concat(partes, ignore_index=True), cadastro


# --------------------------------------------------------------------------
# Alerta Rio
# --------------------------------------------------------------------------
def _sessao_alertario() -> tuple[requests.Session, str]:
    s = requests.Session()
    s.headers.update(UA)
    r = _http(s, "GET", URL_ALERTARIO, timeout=60)
    m = re.search(r"csrfmiddlewaretoken' value='([^']+)'", r.text)
    if not m:
        raise RuntimeError("Alerta Rio: token CSRF não encontrado; o formulário mudou")
    return s, m.group(1)


def baixar_alertario(ano: int, est: int, sessao: requests.Session, token: str) -> bytes | None:
    r = _http(sessao, "POST", URL_ALERTARIO, timeout=300,
              data={"csrfmiddlewaretoken": token, f"{est}-check": "on", f"{est}-choice": str(ano)},
              headers={"Referer": URL_ALERTARIO})
    if "zip" not in r.headers.get("content-type", ""):
        return None
    return r.content


def _ler_txt_alertario(texto: str, nome: str) -> pd.DataFrame:
    colunas = ["dia", "hora", "chuva", "dir", "vel", "temp", "pres", "umid"]
    texto = texto.lstrip("﻿")
    if not texto.strip():
        # a fonte publica alguns meses como arquivo vazio (estação sem dados, p. ex. São Cristóvão 2022-05)
        log.warning("  %s: arquivo vazio na fonte; mês sem dados", nome)
        return pd.DataFrame(columns=colunas)
    linhas = texto.splitlines()
    ini = next((i for i, l in enumerate(linhas) if l.lstrip().startswith("Dia")), None)
    if ini is None:
        raise ValueError(f"{nome}: cabeçalho não encontrado (o arquivo tem conteúdo, mas não o layout esperado)")
    cab = linhas[ini].split()
    if cab[:3] != ["Dia", "Hora", "HBV"] or cab[3:] != ["Chuva", "DirVento", "VelVento", "Temperatura", "Pressao", "Umidade"]:
        raise ValueError(f"{nome}: colunas inesperadas {cab}")
    out = []
    for l in linhas[ini + 2:]:
        p = l.split()
        if len(p) < 8:
            continue
        if p[2] == "HBV":          # marcador de horário de verão: o campo vem preenchido
            p = p[:2] + p[3:]
        out.append(p[:8])
    return pd.DataFrame(out, columns=colunas)


def processar_alertario(ano: int, est: int, conteudo: bytes) -> pd.DataFrame:
    eid, nome_est = ALERTARIO[est][0], ALERTARIO[est][1]
    frames = []
    with zipfile.ZipFile(io.BytesIO(conteudo)) as z:
        for nome in z.namelist():
            frames.append(_ler_txt_alertario(z.read(nome).decode("utf-8", errors="replace"), nome))
    if not frames:
        return pd.DataFrame()
    d = pd.concat([f for f in frames if not f.empty], ignore_index=True) if any(not f.empty for f in frames) else pd.DataFrame()
    if d.empty:
        return pd.DataFrame()
    local = pd.to_datetime(d["dia"] + " " + d["hora"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
    d["dt_utc"] = local + pd.Timedelta(hours=FUSO_HORAS)
    d = d[d["dt_utc"].notna()].copy()
    # leitura que cai em H:00 pertence à hora que termina em H:00
    d["dt_utc"] = d["dt_utc"].dt.ceil("h")
    num = {c: _numero(d[c]) for c in ["chuva", "dir", "vel", "temp", "pres", "umid"]}
    d = d.assign(**num)
    d["vel"] = d["vel"] / 3.6                      # km/h -> m/s
    g = d.groupby("dt_utc")
    resumo = {
        "precipitacao":     g["chuva"].agg(lambda x: x.sum(min_count=1)),
        "temperatura":      g["temp"].mean(),
        "temperatura_max":  g["temp"].max(),
        "temperatura_min":  g["temp"].min(),
        "umidade":          g["umid"].mean(),
        "pressao":          g["pres"].mean(),
        "vento_velocidade": g["vel"].mean(),
        "vento_direcao":    g["dir"].agg(_media_circular),
    }
    n_leituras = g.size()
    partes = []
    for var, serie in resumo.items():
        v = serie.rename("valor").reset_index()
        v["n_obs"] = v["dt_utc"].map(n_leituras)
        v["estacao_id"], v["estacao_nome"], v["variavel"] = eid, nome_est, var
        partes.append(v)
    return pd.concat(partes, ignore_index=True)


# --------------------------------------------------------------------------
# Padronização, grade horária e gravação
# --------------------------------------------------------------------------
def aplicar_faixas(longo: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Valores fora da faixa física viram nulo. Devolve também a contagem por (estacao, variavel)."""
    fora: dict = {}
    longo = longo.copy()
    for var, info in VARIAVEIS.items():
        m = longo["variavel"] == var
        lo, hi = info["faixa"]
        ruim = m & longo["valor"].notna() & ((longo["valor"] < lo) | (longo["valor"] > hi))
        if ruim.any():
            for est, n in longo.loc[ruim].groupby("estacao_id").size().items():
                fora[(est, var)] = int(n)
            longo.loc[ruim, "valor"] = np.nan
    return longo, fora


def gravar_particao(df: pd.DataFrame, base: Path, ano: int) -> None:
    pasta = base / f"ano={ano}"
    pasta.mkdir(parents=True, exist_ok=True)
    df.to_parquet(pasta / "part-0.parquet", index=False)


def gravar_horario(longo: pd.DataFrame, raiz: Path, ano: int, fonte: str) -> None:
    """Grava horario/<variavel>/ano=AAAA, preservando as linhas das outras fontes do mesmo ano."""
    for var, g in longo.groupby("variavel"):
        base = raiz / "horario" / var
        arq = base / f"ano={ano}" / "part-0.parquet"
        novo = g.drop(columns=["variavel"]).assign(fonte=fonte)
        cols = ["fonte", "estacao_id", "estacao_nome", "dt_utc", "valor", "n_obs"]
        novo = novo[cols]
        if arq.exists():
            antigo = pd.read_parquet(arq)
            antigo = antigo[antigo["fonte"] != fonte]
            novo = pd.concat([antigo, novo], ignore_index=True)
        novo = novo.sort_values(["fonte", "estacao_id", "dt_utc"]).reset_index(drop=True)
        gravar_particao(novo, base, ano)


def _agregar_dia(h: pd.DataFrame, var: str) -> pd.DataFrame:
    """h: horário de uma variável (várias fontes). Devolve por estação e dia local."""
    h = h[h["valor"].notna()].copy()
    h["dia"] = (h["dt_utc"] - pd.Timedelta(hours=FUSO_HORAS)).dt.normalize()
    g = h.groupby(["fonte", "estacao_id", "dia"])
    out = g.size().rename("n_horas").to_frame()
    for st in VARIAVEIS[var]["stats"]:
        if st == "media":
            out[st] = _media_circular_grupo(g) if var == "vento_direcao" else g["valor"].mean()
        elif st == "soma":
            out[st] = g["valor"].sum()
        elif st == "min":
            out[st] = g["valor"].min()
        elif st == "max":
            out[st] = g["valor"].max()
    out = out.reset_index()
    cols_stat = VARIAVEIS[var]["stats"]
    out.loc[out["n_horas"] < VARIAVEIS[var].get("min_horas", MIN_HORAS_DIA), cols_stat] = np.nan
    return out


def _media_circular_grupo(g) -> pd.Series:
    return g["valor"].agg(_media_circular)


def recalcular_diario_municipal(raiz: Path, anos_locais: set[int]) -> None:
    for var in VARIAVEIS:
        base_h = raiz / "horario" / var
        disponiveis = {int(p.name.split("=")[1]) for p in base_h.glob("ano=*")} if base_h.exists() else set()
        for L in sorted(anos_locais):
            fontes = [a for a in (L - 1, L, L + 1) if a in disponiveis]
            if not fontes:
                continue
            h = pd.concat([pd.read_parquet(base_h / f"ano={a}" / "part-0.parquet") for a in fontes], ignore_index=True)
            d = _agregar_dia(h, var)
            d = d[d["dia"].dt.year == L]
            if d.empty:
                continue
            stats = VARIAVEIS[var]["stats"]
            gravar_particao(d.sort_values(["fonte", "estacao_id", "dia"]).reset_index(drop=True),
                            raiz / "diario" / var, L)
            principal = stats[0]
            comp = d[d[principal].notna()]
            if var == "vento_direcao":
                m = comp.groupby("dia")[principal].agg(_media_circular).rename(principal).to_frame()
            else:
                m = comp.groupby("dia")[stats].mean()
            m["n_estacoes"] = comp.groupby("dia")["estacao_id"].nunique()
            m = m.reset_index().sort_values("dia")
            gravar_particao(m, raiz / "municipal" / var, L)


def exportar_csv_municipal(raiz: Path, saida: Path) -> None:
    """Uma tabela larga com a média municipal diária de todas as variáveis (para painéis/planilhas)."""
    wide = None
    for var in VARIAVEIS:
        arqs = sorted((raiz / "municipal" / var).glob("ano=*/part-0.parquet"))
        if not arqs:
            continue
        d = pd.concat([pd.read_parquet(a) for a in arqs], ignore_index=True)
        d = d.rename(columns={c: f"{var}_{c}" for c in d.columns if c not in ("dia", "n_estacoes")})
        d = d.rename(columns={"n_estacoes": f"{var}_n_estacoes"})
        wide = d if wide is None else wide.merge(d, on="dia", how="outer")
    if wide is None:
        return
    wide = wide.sort_values("dia")
    wide["dia"] = pd.to_datetime(wide["dia"]).dt.strftime("%Y-%m-%d")
    wide.round(3).to_csv(saida, index=False)
    log.info("CSV municipal diário: %s linhas -> %s", f"{len(wide):,}", saida)


# --------------------------------------------------------------------------
# QA e cadastro
# --------------------------------------------------------------------------
def resumo_qa(longo: pd.DataFrame, ano: int, fonte: str, fora: dict) -> pd.DataFrame:
    linhas = []
    horas_ano = 8784 if (ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)) else 8760
    for (est, var), g in longo.groupby(["estacao_id", "variavel"]):
        v = g["valor"].dropna()
        linhas.append(dict(
            fonte=fonte, estacao_id=est, ano=ano, variavel=var,
            n_horas_com_valor=int(v.size),
            cobertura_pct=round(100 * v.size / horas_ano, 1),
            minimo=float(v.min()) if v.size else np.nan,
            maximo=float(v.max()) if v.size else np.nan,
            fora_de_faixa=fora.get((est, var), 0),
            primeiro=g["dt_utc"].min(), ultimo=g["dt_utc"].max(),
        ))
    return pd.DataFrame(linhas)


def salvar_qa(novo: pd.DataFrame, raiz_qa: Path) -> None:
    raiz_qa.mkdir(parents=True, exist_ok=True)
    arq = raiz_qa / "resumo_clima.csv"
    if arq.exists() and not novo.empty:
        antigo = pd.read_csv(arq)
        chaves = novo[["fonte", "ano"]].drop_duplicates()
        antigo = antigo.merge(chaves, on=["fonte", "ano"], how="left", indicator=True)
        antigo = antigo[antigo["_merge"] == "left_only"].drop(columns="_merge")
        novo = pd.concat([antigo, novo], ignore_index=True)
    novo.sort_values(["fonte", "estacao_id", "variavel", "ano"]).to_csv(arq, index=False)


def salvar_cadastro(novas: list[dict], raiz: Path) -> None:
    arq = raiz / "estacoes.csv"
    cad = pd.DataFrame(novas)
    base = [dict(fonte="Alerta Rio", estacao_id=v[0], estacao_nome=v[1], latitude=v[2], longitude=v[3], altitude=v[4])
            for v in ALERTARIO.values()]
    cad = pd.concat([pd.DataFrame(base), cad], ignore_index=True)
    if arq.exists():
        cad = pd.concat([cad, pd.read_csv(arq)], ignore_index=True)
    cad = cad.drop_duplicates(["fonte", "estacao_id"], keep="first").sort_values(["fonte", "estacao_id"])
    cad.to_csv(arq, index=False)


# --------------------------------------------------------------------------
# Orquestração
# --------------------------------------------------------------------------
def rodar(anos: list[int], fontes: list[str], raiz: Path, pasta_zip: Path, forcar: bool, apagar_zip: bool) -> int:
    raiz.mkdir(parents=True, exist_ok=True)
    falhas: list[str] = []
    tocados: set[int] = set()
    qa_partes, cadastro = [], []
    sess_ar = None
    for ano in anos:
        if "inmet" in fontes:
            try:
                zp = baixar_inmet(ano, pasta_zip, forcar)
                longo, cad = processar_inmet(ano, zp)
                if longo.empty:
                    log.warning("INMET %d: nenhuma estação do MRJ no arquivo", ano)
                else:
                    longo, fora = aplicar_faixas(longo)
                    gravar_horario(longo, raiz, ano, "INMET")
                    qa_partes.append(resumo_qa(longo, ano, "INMET", fora))
                    cadastro += cad
                    tocados.add(ano)
                    log.info("INMET %d: %d estações, %s linhas", ano, len(cad), f"{len(longo):,}")
                if apagar_zip:
                    zp.unlink(missing_ok=True)
            except Exception as e:  # noqa: BLE001
                log.error("INMET %d falhou: %s", ano, e)
                falhas.append(f"INMET {ano}")
        if "alertario" in fontes:
            try:
                if sess_ar is None:
                    sess_ar = _sessao_alertario()
                s, tok = sess_ar
                partes = []
                for est in ALERTARIO:
                    conteudo = baixar_alertario(ano, est, s, tok)
                    time.sleep(1)
                    if not conteudo:
                        log.info("Alerta Rio %d estação %s: sem dados", ano, ALERTARIO[est][0])
                        continue
                    p = processar_alertario(ano, est, conteudo)
                    if not p.empty:
                        partes.append(p)
                if partes:
                    longo = pd.concat(partes, ignore_index=True)
                    longo, fora = aplicar_faixas(longo)
                    gravar_horario(longo, raiz, ano, "Alerta Rio")
                    qa_partes.append(resumo_qa(longo, ano, "Alerta Rio", fora))
                    tocados.add(ano)
                    log.info("Alerta Rio %d: %d estações, %s linhas", ano, len(partes), f"{len(longo):,}")
                else:
                    log.warning("Alerta Rio %d: nenhuma estação com dados", ano)
            except Exception as e:  # noqa: BLE001
                log.error("Alerta Rio %d falhou: %s", ano, e)
                falhas.append(f"Alerta Rio {ano}")
    if tocados:
        locais = set(tocados) | {a - 1 for a in tocados}
        log.info("Recalculando diário e municipal para %s", sorted(locais))
        recalcular_diario_municipal(raiz, locais)
    if qa_partes:
        salvar_qa(pd.concat(qa_partes, ignore_index=True), raiz.parent / "qa" if raiz.name == "clima" else raiz / "qa")
    salvar_cadastro(cadastro, raiz)
    exportar_csv_municipal(raiz, raiz.parent / "clima_municipal_diario.csv" if raiz.name == "clima" else raiz / "clima_municipal_diario.csv")
    if falhas:
        log.error("Falhas: %s", falhas)
        return 1
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anos", nargs="*", type=int)
    ap.add_argument("--ano-ini", type=int, default=ANO_INI_PADRAO)
    ap.add_argument("--ano-fim", type=int, default=datetime.now().year)
    ap.add_argument("--fontes", nargs="*", choices=["inmet", "alertario"], default=["inmet", "alertario"])
    ap.add_argument("--raiz", type=Path, default=Path("datalake/clima"))
    ap.add_argument("--pasta-zip", type=Path, default=Path("datalake/raw_clima"))
    ap.add_argument("--forcar-download", action="store_true")
    ap.add_argument("--apagar-zip", action="store_true")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    anos = sorted(set(a.anos)) if a.anos else list(range(a.ano_ini, a.ano_fim + 1))
    sys.exit(rodar(anos, a.fontes, a.raiz, a.pasta_zip, a.forcar_download, a.apagar_zip))


if __name__ == "__main__":
    main()
