# Mortalidade (SIM) no município do Rio de Janeiro: data lake e painel clima × óbitos

## O que tem aqui
- `sim_datalake.py`: baixa os CSVs do SIM (OpenDATASUS), filtra o MRJ (330455) e grava Parquet (silver) por ocorrência e por residência.
- `.github/workflows/atualizar_sim.yml`: atualização mensal automática; publica na Release `sim-mrj` o silver (`silver_sim_mrj.tar.gz`) e `obitos_diarios_ocorrencia_mrj.csv`.
- `painel/`: painel Shiny que lê esses dados e o clima do estudo de Morais et al.

- `clima_datalake.py`: série histórica de clima do MRJ (INMET e Alerta Rio), um conjunto de dados por tipo de aferição.
- `.github/workflows/atualizar_clima.yml`: atualização mensal do clima; publica na Release `clima-mrj`.

## Primeira carga
Actions > "Atualizar SIM (MRJ)" > Run workflow, com os anos de 2006 a 2026 no campo `anos`.

## Painel
1. No servidor: `sudo R -f painel/instalar_pacotes.R`
2. Copiar `painel/` para `/srv/shiny-server/painel`
3. Definir `REPO_DADOS` só se o repositório mudar (padrão: FEHALTENBURG1/mortalidade_MRJ).

## Créditos
Clima e métrica HAAT: Morais JHA, Saraceni V, Ferreira CD, Cruz DMO, Aguilar GM, Cruz OG.
*Heat exposure and mortality in Rio de Janeiro: sustaining the first Brazilian heat protocol.*
https://github.com/joaohmorais/heat_mortality_MRJ_article (uso autorizado).

## Clima (data lake)
Variáveis: temperatura (média, máxima e mínima da hora), ponto de orvalho, umidade, precipitação, pressão,
vento (velocidade, direção, rajada) e radiação. Para cada uma:

| Camada | Caminho | Conteúdo |
|---|---|---|
| Horário | `clima/horario/<variavel>/ano=AAAA` | por estação, hora em UTC |
| Diário | `clima/diario/<variavel>/ano=AAAA` | por estação e dia local (UTC-3) |
| Municipal | `clima/municipal/<variavel>/ano=AAAA` | média das estações do município por dia local |

Também saem `clima/estacoes.csv`, `qa/resumo_clima.csv` e `clima_municipal_diario.csv` (tabela larga).

Estações: INMET A602 Marambaia, A621 Vila Militar, A636 Jacarepaguá, A652 Forte de Copacabana; Alerta Rio
Vidigal, Irajá, Jardim Botânico, Barra/Riocentro, Guaratiba, Santa Cruz, Alto da Boa Vista, São Cristóvão.
Nem toda estação mede todas as variáveis (a maior parte do Alerta Rio mede só temperatura, umidade e chuva);
`n_estacoes` mostra quantas entraram em cada média.

Primeira carga: Actions > "Atualizar clima (MRJ)" > Run workflow com os anos de 2006 a 2026.
