# Data lake do município do Rio de Janeiro: mortalidade (SIM) e clima

Este repositório guarda, em um só lugar e versionado com commits, os bancos de dados do município do Rio de Janeiro (código IBGE 330455) usados nas análises de mortalidade e calor. Os dados ficam na pasta `datalake/`. O catálogo, com número de linhas, período e colunas de cada conjunto, está em [`datalake/CATALOGO.md`](datalake/CATALOGO.md) e é gerado a cada atualização.

## Estrutura

```
datalake/
  silver/sim/
    ocorrencia_mrj/ano_arquivo=AAAA/part-0.parquet    óbitos ocorridos no município
    residencia_mrj/ano_arquivo=AAAA/part-0.parquet    óbitos de residentes no município
  clima/
    horario/<variavel>/ano=AAAA/part-0.parquet        por estação, hora em UTC
    diario/<variavel>/ano=AAAA/part-0.parquet         por estação, dia local (UTC-3)
    municipal/<variavel>/ano=AAAA/part-0.parquet      média das estações por dia local
    estacoes.csv                                      cadastro das estações
  clima_municipal_diario.csv                          clima municipal diário, tabela larga
  haat_diario_municipal.csv                           índice de calor e HAAT diários
  obitos_diarios_ocorrencia_mrj.csv                   óbitos por dia, faixa etária e capítulo da CID-10
  qa/                                                 controle de qualidade por ano
  CATALOGO.md, catalogo.csv                           catálogo gerado por catalogar.py
```

## Como ler os dados

Em R, com o pacote `arrow`, a partir de uma cópia do repositório:

```r
library(arrow)
obitos <- open_dataset("datalake/silver/sim/ocorrencia_mrj") |> collect()
temp   <- open_dataset("datalake/clima/municipal/temperatura") |> collect()
haat   <- readr::read_csv("datalake/haat_diario_municipal.csv")
```

Em Python:

```python
import pandas as pd
obitos = pd.read_parquet("datalake/silver/sim/ocorrencia_mrj")
haat = pd.read_csv("datalake/haat_diario_municipal.csv")
```

Para ler um arquivo sem clonar, use o endereço bruto do GitHub, por exemplo
`https://raw.githubusercontent.com/FEHALTENBURG1/<repositório>/main/datalake/haat_diario_municipal.csv`.
Cada arquivo Parquet tem menos de 10 MB, abaixo do limite de 100 MB por arquivo do Git.

## Mortalidade (SIM)

Fonte: arquivos de mortalidade do OpenDATASUS (Ministério da Saúde), de 2006 a 2026. `sim_datalake.py` baixa o arquivo de cada ano, filtra o município do Rio de Janeiro e grava dois recortes em Parquet:

- `ocorrencia_mrj`: óbitos com ocorrência no município, qualquer que seja a residência.
- `residencia_mrj`: óbitos de residentes no município, qualquer que seja o local de ocorrência.

A partição `ano_arquivo` é o ano do arquivo de origem no OpenDATASUS. Um óbito pode estar no arquivo de um ano diferente do ano do óbito (por exemplo, por data de entrada no sistema), então use `DTOBITO` para filtrar por data de óbito.

O banco combinado (residentes e óbitos no território) foi descontinuado. O pipeline ainda sabe gerá-lo, mas ele não é versionado nem publicado.

## Clima

Fontes: INMET e Alerta Rio. `clima_datalake.py` monta a série histórica por tipo de aferição. Variáveis: temperatura (média, máxima e mínima da hora), ponto de orvalho, umidade, precipitação, pressão, vento (velocidade, direção e rajada) e radiação.

Estações: INMET A602 Marambaia, A621 Vila Militar, A636 Jacarepaguá e A652 Forte de Copacabana; Alerta Rio Vidigal, Irajá, Jardim Botânico, Barra/Riocentro, Guaratiba, Santa Cruz, Alto da Boa Vista e São Cristóvão. Nem toda estação mede todas as variáveis (a maior parte do Alerta Rio mede só temperatura, umidade e chuva), e a coluna `n_estacoes` mostra quantas entraram em cada média.

`haat_clima.py` calcula o índice de calor e a métrica HAAT diários a partir do próprio lago, sem baixar nada.

## Atualização

Dois fluxos do GitHub Actions rodam todo mês e gravam o resultado em `datalake/` com um commit:

| Fluxo | Quando | O que faz |
|---|---|---|
| `atualizar_sim.yml` | dia 5, 08:00 UTC | Reprocessa o ano anterior e o corrente do SIM, refaz `obitos_diarios_ocorrencia_mrj.csv` |
| `atualizar_clima.yml` | dia 6, 08:00 UTC | Reprocessa o ano anterior e o corrente do clima e recalcula o HAAT |

Depois de cada commit, `catalogar.py` atualiza o catálogo. Os dois fluxos também continuam publicando as Releases `sim-mrj` e `clima-mrj`, porque o painel Shiny ainda lê os dados delas. Quando o painel passar a ler `datalake/` diretamente, a publicação nas Releases pode ser removida.

Primeira carga ou reprocessamento de anos específicos: Actions, escolher o fluxo, Run workflow, e preencher o campo `anos` (por exemplo, de 2006 a 2026 para a carga completa do SIM; a do clima leva cerca de uma hora).

### Crescimento do repositório

Hoje `datalake/` tem cerca de 200 MB. Como o Parquet é regravado inteiro a cada atualização, cada mês adiciona ao histórico do Git os arquivos dos dois anos reprocessados, até cerca de 18 MB no pior caso, o que dá algo próximo de 200 MB por ano. Se o histórico ficar pesado, ele pode ser comprimido em um novo commit inicial sem perder os dados atuais.

## Outros arquivos

- `agregar_obitos.py`: gera `obitos_diarios_ocorrencia_mrj.csv` a partir do recorte de ocorrência.
- `catalogar.py`: gera `datalake/CATALOGO.md` e `datalake/catalogo.csv`.
- `.github/scripts/commitar_dados.sh`: commita as mudanças de `datalake/` e atualiza o catálogo, tentando de novo se outro fluxo tiver publicado antes.
- `app.R` e `instalar_pacotes.R`: protótipo anterior do painel. O painel atual está no repositório `mortalidade_MRJ`, em `painel_quarto/shiny`.

## Créditos

Clima e métrica HAAT: Morais JHA, Saraceni V, Ferreira CD, Cruz DMO, Aguilar GM, Cruz OG. *Heat exposure and mortality in Rio de Janeiro: sustaining the first Brazilian heat protocol.* https://github.com/joaohmorais/heat_mortality_MRJ_article (uso autorizado).
