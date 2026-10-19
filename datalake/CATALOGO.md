# Catálogo do data lake do município do Rio de Janeiro

Gerado por `catalogar.py` a cada atualização. Não edite à mão.


## Mortalidade (SIM)

| Conjunto | Formato | Partição | Arquivos | Linhas | Período | Tamanho (MB) |
|---|---|---|---:|---:|---|---:|
| `silver/sim/ocorrencia_mrj` | parquet | ano_arquivo | 21 | 1.303.625 | 2006 a 2026 | 66,8 |
| `silver/sim/residencia_mrj` | parquet | ano_arquivo | 21 | 1.151.359 | 2006 a 2026 | 58,7 |

## Clima

| Conjunto | Formato | Partição | Arquivos | Linhas | Período | Tamanho (MB) |
|---|---|---|---:|---:|---|---:|
| `clima/horario/ponto_orvalho` | parquet | ano | 21 | 602.496 | 2006 a 2026 | 2,7 |
| `clima/horario/precipitacao` | parquet | ano | 21 | 1.561.877 | 2006 a 2026 | 4,0 |
| `clima/horario/pressao` | parquet | ano | 21 | 1.561.877 | 2006 a 2026 | 5,1 |
| `clima/horario/radiacao` | parquet | ano | 21 | 602.496 | 2006 a 2026 | 3,7 |
| `clima/horario/temperatura` | parquet | ano | 21 | 1.561.877 | 2006 a 2026 | 5,8 |
| `clima/horario/temperatura_max` | parquet | ano | 21 | 1.561.877 | 2006 a 2026 | 5,3 |
| `clima/horario/temperatura_min` | parquet | ano | 21 | 1.561.877 | 2006 a 2026 | 5,2 |
| `clima/horario/umidade` | parquet | ano | 21 | 1.561.877 | 2006 a 2026 | 5,3 |
| `clima/horario/vento_direcao` | parquet | ano | 21 | 1.561.877 | 2006 a 2026 | 7,2 |
| `clima/horario/vento_rajada` | parquet | ano | 21 | 602.496 | 2006 a 2026 | 2,7 |
| `clima/horario/vento_velocidade` | parquet | ano | 21 | 1.561.877 | 2006 a 2026 | 5,0 |
| `clima/diario/ponto_orvalho` | parquet | ano | 21 | 23.263 | 2006 a 2026 | 0,2 |
| `clima/diario/precipitacao` | parquet | ano | 21 | 64.541 | 2006 a 2026 | 0,2 |
| `clima/diario/pressao` | parquet | ano | 21 | 38.413 | 2006 a 2026 | 0,4 |
| `clima/diario/radiacao` | parquet | ano | 21 | 24.246 | 2006 a 2026 | 0,3 |
| `clima/diario/temperatura` | parquet | ano | 21 | 59.132 | 2006 a 2026 | 0,7 |
| `clima/diario/temperatura_max` | parquet | ano | 21 | 59.127 | 2006 a 2026 | 0,2 |
| `clima/diario/temperatura_min` | parquet | ano | 21 | 59.127 | 2006 a 2026 | 0,2 |
| `clima/diario/umidade` | parquet | ano | 21 | 56.757 | 2006 a 2026 | 0,6 |
| `clima/diario/vento_direcao` | parquet | ano | 21 | 39.745 | 2006 a 2026 | 0,5 |
| `clima/diario/vento_rajada` | parquet | ano | 21 | 24.070 | 2006 a 2026 | 0,2 |
| `clima/diario/vento_velocidade` | parquet | ano | 21 | 40.255 | 2006 a 2026 | 0,5 |
| `clima/municipal/ponto_orvalho` | parquet | ano | 21 | 7.334 | 2006 a 2026 | 0,1 |
| `clima/municipal/precipitacao` | parquet | ano | 21 | 7.596 | 2006 a 2026 | 0,1 |
| `clima/municipal/pressao` | parquet | ano | 21 | 7.570 | 2006 a 2026 | 0,2 |
| `clima/municipal/radiacao` | parquet | ano | 21 | 7.429 | 2006 a 2026 | 0,1 |
| `clima/municipal/temperatura` | parquet | ano | 21 | 7.586 | 2006 a 2026 | 0,3 |
| `clima/municipal/temperatura_max` | parquet | ano | 21 | 7.586 | 2006 a 2026 | 0,1 |
| `clima/municipal/temperatura_min` | parquet | ano | 21 | 7.586 | 2006 a 2026 | 0,1 |
| `clima/municipal/umidade` | parquet | ano | 21 | 7.581 | 2006 a 2026 | 0,2 |
| `clima/municipal/vento_direcao` | parquet | ano | 21 | 7.561 | 2006 a 2026 | 0,2 |
| `clima/municipal/vento_rajada` | parquet | ano | 21 | 7.377 | 2006 a 2026 | 0,1 |
| `clima/municipal/vento_velocidade` | parquet | ano | 21 | 7.579 | 2006 a 2026 | 0,2 |

## Tabelas derivadas e controle de qualidade

| Conjunto | Formato | Partição | Arquivos | Linhas | Período | Tamanho (MB) |
|---|---|---|---:|---:|---|---:|
| `clima_municipal_diario.csv` | csv | sem partição | 1 | 7.596 | 2006-01-01 a 2026-10-18 | 1,2 |
| `haat_diario_municipal.csv` | csv | sem partição | 1 | 7.117 | 2007-01-01 a 2026-10-19 | 0,7 |
| `obitos_diarios_ocorrencia_mrj.csv` | csv | sem partição | 1 | 186.346 | 2006-01-01 a 2026-08-26 | 12,5 |
| `clima/estacoes.csv` | csv | sem partição | 1 | 12 |  | 0,0 |
| `qa/resumo_ocorrencia.csv` | csv | sem partição | 1 | 21 |  | 0,0 |
| `qa/resumo_residencia.csv` | csv | sem partição | 1 | 21 |  | 0,0 |
| `qa/resumo_clima.csv` | csv | sem partição | 1 | 1.701 |  | 0,1 |

## Descrição e colunas

<details><summary><code>silver/sim/ocorrencia_mrj</code></summary>

Declarações de óbito do SIM com ocorrência no município do Rio de Janeiro (código IBGE 330455).

Fonte: OpenDATASUS, Sistema de Informações sobre Mortalidade (SIM), Ministério da Saúde.

Colunas (133): `CONTADOR`, `ORIGEM`, `TIPOBITO`, `DTOBITO`, `HORAOBITO`, `NATURAL`, `CODMUNNATU`, `DTNASC`, `IDADE`, `SEXO`, `RACACOR`, `ESTCIV`, `ESC`, `ESC2010`, `SERIESCFAL`, `OCUP`, `CODMUNRES`, `LOCOCOR`, `CODESTAB`, `CODMUNOCOR`, `IDADEMAE`, `ESCMAE`, `ESCMAE2010`, `SERIESCMAE`, `OCUPMAE`, `QTDFILVIVO`, `QTDFILMORT`, `GRAVIDEZ`, `SEMAGESTAC`, `GESTACAO`, `PARTO`, `OBITOPARTO`, `PESO`, `TPMORTEOCO`, `OBITOGRAV`, `OBITOPUERP`, `ASSISTMED`, `EXAME`, `CIRURGIA`, `NECROPSIA`, `LINHAA`, `LINHAB`, `LINHAC`, `LINHAD`, `LINHAII`, `CAUSABAS`, `CB_PRE`, `COMUNSVOIM`, `DTATESTADO`, `CIRCOBITO`, `ACIDTRAB`, `FONTE`, `NUMEROLOTE`, `DTINVESTIG`, `DTCADASTRO`, `ATESTANTE`, `STCODIFICA`, `CODIFICADO`, `VERSAOSIST`, `VERSAOSCB`, `FONTEINV`, `DTRECEBIM`, `ATESTADO`, `DTRECORIGA`, `OPOR_DO`, `CAUSAMAT`, `ESCMAEAGR1`, `ESCFALAGR1`, `STDOEPIDEM`, `STDONOVA`, `DIFDATA`, `NUDIASOBCO`, `DTCADINV`, `TPOBITOCOR`, `DTCONINV`, `FONTES`, `TPRESGINFO`, `TPNIVELINV`, `DTCADINF`, `MORTEPARTO`, `DTCONCASO`, `ALTCAUSA`, `CAUSABAS_O`, `TPPOS`, `TP_ALTERA`, `CB_ALT`, `cod_mun_res6`, `cod_mun_ocor6`, `residente_mrj`, `ocorrencia_mrj`, `categoria_territorial`, `idade_unidade`, `idade_unidade_desc`, `idade_valor`, `idade_anos`, `ano_obito`, `mes_obito`, `TIPOBITO_DESC`, `RACACOR_DESC`, `ESTCIV_DESC`, `ESC2010_DESC`, `ESCMAE2010_DESC`, `ESC_DESC`, `ESCMAE_DESC`, `ESCMAEAGR1_DESC`, `ESCFALAGR1_DESC`, `LOCOCOR_DESC`, `GRAVIDEZ_DESC`, `PARTO_DESC`, `OBITOPARTO_DESC`, `MORTEPARTO_DESC`, `TPMORTEOCO_DESC`, `OBITOGRAV_DESC`, `OBITOPUERP_DESC`, `ASSISTMED_DESC`, `NECROPSIA_DESC`, `EXAME_DESC`, `CIRURGIA_DESC`, `ACIDTRAB_DESC`, `ATESTANTE_DESC`, `CIRCOBITO_DESC`, `FONTE_DESC`, `GESTACAO_DESC`, `FONTEINV_DESC`, `STDOEPIDEM_DESC`, `STDONOVA_DESC`, `TPRESGINFO_DESC`, `TPNIVELINV_DESC`, `ALTCAUSA_DESC`, `TPPOS_DESC`, `sexo_desc`, `cid_capitulo`, `cid_capitulo_desc`

</details>

<details><summary><code>silver/sim/residencia_mrj</code></summary>

Declarações de óbito do SIM de residentes no município do Rio de Janeiro, qualquer que seja o local de ocorrência.

Fonte: OpenDATASUS, Sistema de Informações sobre Mortalidade (SIM), Ministério da Saúde.

Colunas (133): `CONTADOR`, `ORIGEM`, `TIPOBITO`, `DTOBITO`, `HORAOBITO`, `NATURAL`, `CODMUNNATU`, `DTNASC`, `IDADE`, `SEXO`, `RACACOR`, `ESTCIV`, `ESC`, `ESC2010`, `SERIESCFAL`, `OCUP`, `CODMUNRES`, `LOCOCOR`, `CODESTAB`, `CODMUNOCOR`, `IDADEMAE`, `ESCMAE`, `ESCMAE2010`, `SERIESCMAE`, `OCUPMAE`, `QTDFILVIVO`, `QTDFILMORT`, `GRAVIDEZ`, `SEMAGESTAC`, `GESTACAO`, `PARTO`, `OBITOPARTO`, `PESO`, `TPMORTEOCO`, `OBITOGRAV`, `OBITOPUERP`, `ASSISTMED`, `EXAME`, `CIRURGIA`, `NECROPSIA`, `LINHAA`, `LINHAB`, `LINHAC`, `LINHAD`, `LINHAII`, `CAUSABAS`, `CB_PRE`, `COMUNSVOIM`, `DTATESTADO`, `CIRCOBITO`, `ACIDTRAB`, `FONTE`, `NUMEROLOTE`, `DTINVESTIG`, `DTCADASTRO`, `ATESTANTE`, `STCODIFICA`, `CODIFICADO`, `VERSAOSIST`, `VERSAOSCB`, `FONTEINV`, `DTRECEBIM`, `ATESTADO`, `DTRECORIGA`, `OPOR_DO`, `CAUSAMAT`, `ESCMAEAGR1`, `ESCFALAGR1`, `STDOEPIDEM`, `STDONOVA`, `DIFDATA`, `NUDIASOBCO`, `DTCADINV`, `TPOBITOCOR`, `DTCONINV`, `FONTES`, `TPRESGINFO`, `TPNIVELINV`, `DTCADINF`, `MORTEPARTO`, `DTCONCASO`, `ALTCAUSA`, `CAUSABAS_O`, `TPPOS`, `TP_ALTERA`, `CB_ALT`, `cod_mun_res6`, `cod_mun_ocor6`, `residente_mrj`, `ocorrencia_mrj`, `categoria_territorial`, `idade_unidade`, `idade_unidade_desc`, `idade_valor`, `idade_anos`, `ano_obito`, `mes_obito`, `TIPOBITO_DESC`, `RACACOR_DESC`, `ESTCIV_DESC`, `ESC2010_DESC`, `ESCMAE2010_DESC`, `ESC_DESC`, `ESCMAE_DESC`, `ESCMAEAGR1_DESC`, `ESCFALAGR1_DESC`, `LOCOCOR_DESC`, `GRAVIDEZ_DESC`, `PARTO_DESC`, `OBITOPARTO_DESC`, `MORTEPARTO_DESC`, `TPMORTEOCO_DESC`, `OBITOGRAV_DESC`, `OBITOPUERP_DESC`, `ASSISTMED_DESC`, `NECROPSIA_DESC`, `EXAME_DESC`, `CIRURGIA_DESC`, `ACIDTRAB_DESC`, `ATESTANTE_DESC`, `CIRCOBITO_DESC`, `FONTE_DESC`, `GESTACAO_DESC`, `FONTEINV_DESC`, `STDOEPIDEM_DESC`, `STDONOVA_DESC`, `TPRESGINFO_DESC`, `TPNIVELINV_DESC`, `ALTCAUSA_DESC`, `TPPOS_DESC`, `sexo_desc`, `cid_capitulo`, `cid_capitulo_desc`

</details>

<details><summary><code>clima/horario/ponto_orvalho</code></summary>

Valor horário por estação, hora em UTC. Variável: ponto_orvalho.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `estacao_nome`, `dt_utc`, `valor`, `n_obs`

</details>

<details><summary><code>clima/horario/precipitacao</code></summary>

Valor horário por estação, hora em UTC. Variável: precipitacao.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `estacao_nome`, `dt_utc`, `valor`, `n_obs`

</details>

<details><summary><code>clima/horario/pressao</code></summary>

Valor horário por estação, hora em UTC. Variável: pressao.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `estacao_nome`, `dt_utc`, `valor`, `n_obs`

</details>

<details><summary><code>clima/horario/radiacao</code></summary>

Valor horário por estação, hora em UTC. Variável: radiacao.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `estacao_nome`, `dt_utc`, `valor`, `n_obs`

</details>

<details><summary><code>clima/horario/temperatura</code></summary>

Valor horário por estação, hora em UTC. Variável: temperatura.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `estacao_nome`, `dt_utc`, `valor`, `n_obs`

</details>

<details><summary><code>clima/horario/temperatura_max</code></summary>

Valor horário por estação, hora em UTC. Variável: temperatura_max.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `estacao_nome`, `dt_utc`, `valor`, `n_obs`

</details>

<details><summary><code>clima/horario/temperatura_min</code></summary>

Valor horário por estação, hora em UTC. Variável: temperatura_min.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `estacao_nome`, `dt_utc`, `valor`, `n_obs`

</details>

<details><summary><code>clima/horario/umidade</code></summary>

Valor horário por estação, hora em UTC. Variável: umidade.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `estacao_nome`, `dt_utc`, `valor`, `n_obs`

</details>

<details><summary><code>clima/horario/vento_direcao</code></summary>

Valor horário por estação, hora em UTC. Variável: vento_direcao.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `estacao_nome`, `dt_utc`, `valor`, `n_obs`

</details>

<details><summary><code>clima/horario/vento_rajada</code></summary>

Valor horário por estação, hora em UTC. Variável: vento_rajada.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `estacao_nome`, `dt_utc`, `valor`, `n_obs`

</details>

<details><summary><code>clima/horario/vento_velocidade</code></summary>

Valor horário por estação, hora em UTC. Variável: vento_velocidade.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `estacao_nome`, `dt_utc`, `valor`, `n_obs`

</details>

<details><summary><code>clima/diario/ponto_orvalho</code></summary>

Resumo diário por estação, dia local (UTC-3). Variável: ponto_orvalho.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (5): `fonte`, `estacao_id`, `dia`, `n_horas`, `media`

</details>

<details><summary><code>clima/diario/precipitacao</code></summary>

Resumo diário por estação, dia local (UTC-3). Variável: precipitacao.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (5): `fonte`, `estacao_id`, `dia`, `n_horas`, `soma`

</details>

<details><summary><code>clima/diario/pressao</code></summary>

Resumo diário por estação, dia local (UTC-3). Variável: pressao.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (5): `fonte`, `estacao_id`, `dia`, `n_horas`, `media`

</details>

<details><summary><code>clima/diario/radiacao</code></summary>

Resumo diário por estação, dia local (UTC-3). Variável: radiacao.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (5): `fonte`, `estacao_id`, `dia`, `n_horas`, `soma`

</details>

<details><summary><code>clima/diario/temperatura</code></summary>

Resumo diário por estação, dia local (UTC-3). Variável: temperatura.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (7): `fonte`, `estacao_id`, `dia`, `n_horas`, `media`, `min`, `max`

</details>

<details><summary><code>clima/diario/temperatura_max</code></summary>

Resumo diário por estação, dia local (UTC-3). Variável: temperatura_max.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (5): `fonte`, `estacao_id`, `dia`, `n_horas`, `max`

</details>

<details><summary><code>clima/diario/temperatura_min</code></summary>

Resumo diário por estação, dia local (UTC-3). Variável: temperatura_min.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (5): `fonte`, `estacao_id`, `dia`, `n_horas`, `min`

</details>

<details><summary><code>clima/diario/umidade</code></summary>

Resumo diário por estação, dia local (UTC-3). Variável: umidade.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (7): `fonte`, `estacao_id`, `dia`, `n_horas`, `media`, `min`, `max`

</details>

<details><summary><code>clima/diario/vento_direcao</code></summary>

Resumo diário por estação, dia local (UTC-3). Variável: vento_direcao.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (5): `fonte`, `estacao_id`, `dia`, `n_horas`, `media`

</details>

<details><summary><code>clima/diario/vento_rajada</code></summary>

Resumo diário por estação, dia local (UTC-3). Variável: vento_rajada.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (5): `fonte`, `estacao_id`, `dia`, `n_horas`, `max`

</details>

<details><summary><code>clima/diario/vento_velocidade</code></summary>

Resumo diário por estação, dia local (UTC-3). Variável: vento_velocidade.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `dia`, `n_horas`, `media`, `max`

</details>

<details><summary><code>clima/municipal/ponto_orvalho</code></summary>

Média das estações do município por dia local. Variável: ponto_orvalho.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (3): `dia`, `media`, `n_estacoes`

</details>

<details><summary><code>clima/municipal/precipitacao</code></summary>

Média das estações do município por dia local. Variável: precipitacao.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (3): `dia`, `soma`, `n_estacoes`

</details>

<details><summary><code>clima/municipal/pressao</code></summary>

Média das estações do município por dia local. Variável: pressao.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (3): `dia`, `media`, `n_estacoes`

</details>

<details><summary><code>clima/municipal/radiacao</code></summary>

Média das estações do município por dia local. Variável: radiacao.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (3): `dia`, `soma`, `n_estacoes`

</details>

<details><summary><code>clima/municipal/temperatura</code></summary>

Média das estações do município por dia local. Variável: temperatura.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (5): `dia`, `media`, `min`, `max`, `n_estacoes`

</details>

<details><summary><code>clima/municipal/temperatura_max</code></summary>

Média das estações do município por dia local. Variável: temperatura_max.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (3): `dia`, `max`, `n_estacoes`

</details>

<details><summary><code>clima/municipal/temperatura_min</code></summary>

Média das estações do município por dia local. Variável: temperatura_min.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (3): `dia`, `min`, `n_estacoes`

</details>

<details><summary><code>clima/municipal/umidade</code></summary>

Média das estações do município por dia local. Variável: umidade.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (5): `dia`, `media`, `min`, `max`, `n_estacoes`

</details>

<details><summary><code>clima/municipal/vento_direcao</code></summary>

Média das estações do município por dia local. Variável: vento_direcao.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (3): `dia`, `media`, `n_estacoes`

</details>

<details><summary><code>clima/municipal/vento_rajada</code></summary>

Média das estações do município por dia local. Variável: vento_rajada.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (3): `dia`, `max`, `n_estacoes`

</details>

<details><summary><code>clima/municipal/vento_velocidade</code></summary>

Média das estações do município por dia local. Variável: vento_velocidade.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (4): `dia`, `media`, `max`, `n_estacoes`

</details>

<details><summary><code>clima_municipal_diario.csv</code></summary>

Tabela larga com o clima municipal diário (todas as variáveis).

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (28): `dia`, `temperatura_media`, `temperatura_min`, `temperatura_max`, `temperatura_n_estacoes`, `temperatura_max_max`, `temperatura_max_n_estacoes`, `temperatura_min_min`, `temperatura_min_n_estacoes`, `ponto_orvalho_media`, `ponto_orvalho_n_estacoes`, `umidade_media`, `umidade_min`, `umidade_max`, `umidade_n_estacoes`, `precipitacao_soma`, `precipitacao_n_estacoes`, `pressao_media`, `pressao_n_estacoes`, `vento_velocidade_media`, `vento_velocidade_max`, `vento_velocidade_n_estacoes`, `vento_direcao_media`, `vento_direcao_n_estacoes`, `vento_rajada_max`, `vento_rajada_n_estacoes`, `radiacao_soma`, `radiacao_n_estacoes`

</details>

<details><summary><code>haat_diario_municipal.csv</code></summary>

Índice de calor e métrica HAAT diários do município, calculados a partir do clima municipal.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (22): `dia`, `n_horas`, `n_estacoes_medio`, `t_med`, `t_max`, `hi_med`, `hi_max`, `num_hr_32`, `num_hr_33`, `num_hr_34`, `num_hr_35`, `num_hr_36`, `num_hr_37`, `num_hr_38`, `num_hr_39`, `num_hr_40`, `num_hr_41`, `num_hr_42`, `num_hr_43`, `num_hr_44`, `auc32`, `auc36`

</details>

<details><summary><code>obitos_diarios_ocorrencia_mrj.csv</code></summary>

Contagem diária de óbitos por ocorrência, por faixa etária e capítulo da CID-10.

Fonte: OpenDATASUS, Sistema de Informações sobre Mortalidade (SIM), Ministério da Saúde.

Colunas (5): `dia`, `faixa_etaria`, `cid_capitulo`, `cid_capitulo_desc`, `n`

</details>

<details><summary><code>clima/estacoes.csv</code></summary>

Cadastro das estações meteorológicas usadas.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (6): `fonte`, `estacao_id`, `estacao_nome`, `latitude`, `longitude`, `altitude`

</details>

<details><summary><code>qa/resumo_ocorrencia.csv</code></summary>

Controle de qualidade por ano: óbitos no Brasil e no recorte de ocorrência.

Fonte: OpenDATASUS, Sistema de Informações sobre Mortalidade (SIM), Ministério da Saúde.

Colunas (5): `ano_arquivo`, `n_brasil`, `n_recorte`, `Residente e óbito no MRJ`, `Não residente, óbito no MRJ`

</details>

<details><summary><code>qa/resumo_residencia.csv</code></summary>

Controle de qualidade por ano: óbitos no Brasil e no recorte de residência.

Fonte: OpenDATASUS, Sistema de Informações sobre Mortalidade (SIM), Ministério da Saúde.

Colunas (5): `ano_arquivo`, `n_brasil`, `n_recorte`, `Residente e óbito no MRJ`, `Residente no MRJ, óbito fora do MRJ`

</details>

<details><summary><code>qa/resumo_clima.csv</code></summary>

Controle de qualidade do clima por estação, ano e variável.

Fonte: INMET e Alerta Rio (Prefeitura do Rio de Janeiro).

Colunas (11): `fonte`, `estacao_id`, `ano`, `variavel`, `n_horas_com_valor`, `cobertura_pct`, `minimo`, `maximo`, `fora_de_faixa`, `primeiro`, `ultimo`

</details>
