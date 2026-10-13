# Painel: mortalidade por ocorrência (SIM) x clima — Município do Rio de Janeiro
#
# Dados lidos direto do GitHub:
#   - óbitos diários : Release "sim-mrj" do SEU repositório (gerada pelo workflow)
#   - clima diário   : data/temp_df.csv do repositório do artigo (Morais et al.)
#
# Para rodar: shiny::runApp("painel")

library(shiny)
library(bslib)
library(dplyr)
library(tidyr)
library(readr)
library(lubridate)
library(plotly)

# ---- Configuração -----------------------------------------------------------
REPO_DADOS <- Sys.getenv("REPO_DADOS", "FEHALTENBURG1/mortalidade_MRJ")  # <- repositório com a Release sim-mrj
URL_OBITOS <- sprintf(
  "https://github.com/%s/releases/download/sim-mrj/obitos_diarios_ocorrencia_mrj.csv",
  REPO_DADOS
)
URL_CLIMA <- paste0(
  "https://raw.githubusercontent.com/joaohmorais/heat_mortality_MRJ_article/",
  "master/data/temp_df.csv"
)

VARS_CLIMA <- c(
  "Temperatura média (°C)"          = "t_med",
  "Temperatura máxima (°C)"         = "t_max",
  "Índice de calor médio (°C)"      = "hi_med",
  "Índice de calor máximo (°C)"     = "hi_max",
  "HAAT acima de 36 °C (°C·h)"      = "auc36",
  "HAAT acima de 32 °C (°C·h)"      = "auc32"
)

# ---- Leitura (cache de 6 h + cópia local como reserva) ----------------------
TTL_HORAS <- 6
DIR_CACHE <- file.path(tempdir(), "cache_painel")
dir.create(DIR_CACHE, showWarnings = FALSE, recursive = TRUE)

ler_url <- function(url, local) {
  arq <- file.path(DIR_CACHE, basename(url))
  fresco <- file.exists(arq) &&
    difftime(Sys.time(), file.mtime(arq), units = "hours") < TTL_HORAS
  if (!fresco) {
    ok <- tryCatch({
      utils::download.file(url, arq, mode = "wb", quiet = TRUE)
      TRUE
    }, error = function(e) FALSE, warning = function(w) FALSE)
    if (!ok) unlink(arq)
  }
  fonte <- if (file.exists(arq)) arq else local
  if (!file.exists(fonte))
    stop("Não consegui baixar ", url, " e não há cópia local em ", local, call. = FALSE)
  read_csv(fonte, show_col_types = FALSE, progress = FALSE)
}

obitos <- ler_url(URL_OBITOS, "dados/obitos_diarios_ocorrencia_mrj.csv") |>
  mutate(dia = as.Date(dia))
clima <- ler_url(URL_CLIMA, "dados/temp_df.csv") |>
  mutate(dia = as.Date(dia)) |>
  select(dia, all_of(unname(VARS_CLIMA)))

# só o período em que há óbitos E clima
dia_min <- max(min(obitos$dia), min(clima$dia))
dia_max <- min(max(obitos$dia), max(clima$dia))

capitulos <- obitos |>
  distinct(cid_capitulo, cid_capitulo_desc) |>
  arrange(cid_capitulo)
opcoes_cap <- c("Todas as causas" = "TODAS",
                setNames(capitulos$cid_capitulo,
                         paste0(capitulos$cid_capitulo, " – ", capitulos$cid_capitulo_desc)))

# ---- Interface --------------------------------------------------------------
ui <- page_sidebar(
  title = "Mortalidade por ocorrência e clima — Município do Rio de Janeiro",
  theme = bs_theme(version = 5, bootswatch = "flatly"),
  sidebar = sidebar(
    width = 320,
    dateRangeInput("periodo", "Período",
                   start = max(dia_min, dia_max - years(3)), end = dia_max,
                   min = dia_min, max = dia_max, format = "dd/mm/yyyy",
                   language = "pt-BR", separator = " a "),
    selectInput("faixa", "Faixa etária",
                c("Todas" = "TODAS", "65+ anos" = "65+ anos", "0-64 anos" = "0-64 anos")),
    selectInput("causa", "Causa (capítulo CID-10)", opcoes_cap),
    selectInput("var_clima", "Variável climática", VARS_CLIMA, selected = "hi_med"),
    sliderInput("suav", "Média móvel (dias)", min = 1, max = 30, value = 7, step = 1),
    hr(),
    helpText("Óbitos: SIM/OpenDATASUS, por município de ocorrência (CODMUNOCOR = 330455). ",
             "Clima: dados do estudo de Morais et al., cobrindo ", format(min(clima$dia), "%m/%Y"),
             " a ", format(max(clima$dia), "%m/%Y"), ".")
  ),
  navset_card_tab(
    nav_panel("Série diária",
              plotlyOutput("g_serie", height = "520px")),
    nav_panel("Óbitos × clima",
              plotlyOutput("g_resposta", height = "520px"),
              helpText("Média de óbitos por dia em cada faixa (decil) da variável climática.",
                       " Descritivo: não ajusta tendência, sazonalidade nem dia da semana.")),
    nav_panel("Dias de calor",
              layout_columns(
                sliderInput("pctl", "Dia de calor = acima do percentil", min = 80, max = 99,
                            value = 95, step = 1),
                col_widths = 12),
              tableOutput("t_calor"),
              helpText("Compara a média diária de óbitos nos dias acima do percentil escolhido",
                       " com os demais dias do período. Razão bruta, sem controle de confundidores",
                       " (sazonalidade e tendência); para efeito ajustado, ver o modelo DLNM do artigo.")),
    nav_panel("Dados",
              downloadButton("baixar", "Baixar CSV filtrado"),
              br(), br(),
              tableOutput("t_dados")),
    nav_panel("Sobre",
              markdown(paste0(
                "**Fonte dos óbitos:** Sistema de Informações sobre Mortalidade (SIM), ",
                "Ministério da Saúde, via OpenDATASUS. Recorte: óbitos ocorridos no município ",
                "do Rio de Janeiro (IBGE 330455).\n\n",
                "**Fonte do clima:** dados e código do estudo *Heat exposure and mortality in Rio de ",
                "Janeiro: sustaining the first Brazilian heat protocol* (Morais JHA, Saraceni V, ",
                "Ferreira CD, Cruz DMO, Aguilar GM, Cruz OG). Repositório: ",
                "<https://github.com/joaohmorais/heat_mortality_MRJ_article>. Usado com autorização.\n\n",
                "**HAAT:** área acumulada acima de um limiar de índice de calor (°C·h) no dia.\n\n",
                "**Limites:** painel descritivo. Os dados de clima do estudo terminam em jun/2024; ",
                "óbitos mais recentes ficam fora das análises até o clima ser atualizado."
              )))
  )
)

# ---- Servidor ---------------------------------------------------------------
server <- function(input, output, session) {

  base_dia <- reactive({
    req(input$periodo)
    d <- obitos |> filter(dia >= input$periodo[1], dia <= input$periodo[2])
    if (input$faixa != "TODAS")  d <- d |> filter(faixa_etaria == input$faixa)
    if (input$causa != "TODAS")  d <- d |> filter(cid_capitulo == input$causa)
    dias <- tibble(dia = seq(input$periodo[1], input$periodo[2], by = "day"))
    dias |>
      left_join(d |> group_by(dia) |> summarise(n = sum(n), .groups = "drop"), by = "dia") |>
      mutate(n = replace_na(n, 0L)) |>
      inner_join(clima, by = "dia") |>
      arrange(dia) |>
      mutate(clima = .data[[input$var_clima]])
  })

  media_movel <- function(x, k) {
    if (k <= 1) return(x)
    as.numeric(stats::filter(x, rep(1 / k, k), sides = 2))
  }

  nome_var <- reactive(names(VARS_CLIMA)[VARS_CLIMA == input$var_clima])

  output$g_serie <- renderPlotly({
    d <- base_dia()
    validate(need(nrow(d) > 0, "Sem dados para o período escolhido."))
    d <- d |> mutate(n_s = media_movel(n, input$suav), clima_s = media_movel(clima, input$suav))
    plot_ly(d, x = ~dia) |>
      add_lines(y = ~n_s, name = "Óbitos/dia", line = list(color = "#2c3e50"),
                hovertemplate = "%{x|%d/%m/%Y}<br>%{y:.1f} óbitos<extra></extra>") |>
      add_lines(y = ~clima_s, name = nome_var(), yaxis = "y2", line = list(color = "#e67e22"),
                hovertemplate = "%{x|%d/%m/%Y}<br>%{y:.1f}<extra></extra>") |>
      layout(
        xaxis = list(title = ""),
        yaxis = list(title = paste0("Óbitos por dia (média móvel de ", input$suav, " d)")),
        yaxis2 = list(title = nome_var(), overlaying = "y", side = "right", showgrid = FALSE),
        legend = list(orientation = "h", y = -0.15),
        hovermode = "x unified"
      )
  })

  output$g_resposta <- renderPlotly({
    d <- base_dia()
    validate(need(nrow(d) > 30, "Poucos dias para o período escolhido."))
    q <- unique(stats::quantile(d$clima, probs = seq(0, 1, 0.1), na.rm = TRUE))
    validate(need(length(q) > 2, "Variável com pouca variação no período."))
    d <- d |>
      mutate(faixa = cut(clima, breaks = q, include.lowest = TRUE, dig.lab = 4)) |>
      group_by(faixa) |>
      summarise(media = mean(n), dp = sd(n), dias = n(), .groups = "drop") |>
      mutate(ep = dp / sqrt(dias))
    plot_ly(d, x = ~faixa, y = ~media, type = "bar", marker = list(color = "#2c3e50"),
            error_y = list(array = ~1.96 * ep, color = "#7f8c8d"),
            hovertemplate = "%{x}<br>%{y:.1f} óbitos/dia<br>%{customdata} dias<extra></extra>",
            customdata = ~dias) |>
      layout(xaxis = list(title = paste0(nome_var(), " (decis)")),
             yaxis = list(title = "Média de óbitos por dia"))
  })

  calor <- reactive({
    d <- base_dia()
    req(nrow(d) > 30)
    lim <- stats::quantile(d$clima, input$pctl / 100, na.rm = TRUE)
    d |>
      mutate(grupo = ifelse(clima > lim, "Dias de calor", "Demais dias")) |>
      group_by(grupo) |>
      summarise(dias = n(), obitos = sum(n), media_dia = mean(n), .groups = "drop") |>
      mutate(limiar = lim)
  })

  output$t_calor <- renderTable({
    r <- calor()
    validate(need(nrow(r) == 2, "Sem dias nos dois grupos."))
    m_c <- r$media_dia[r$grupo == "Dias de calor"]
    m_d <- r$media_dia[r$grupo == "Demais dias"]
    r |>
      transmute(Grupo = grupo, Dias = dias, `Óbitos` = obitos,
                `Média/dia` = round(media_dia, 1)) |>
      bind_rows(tibble(Grupo = sprintf("Razão calor/demais (limiar %.1f)", r$limiar[1]),
                       Dias = NA_integer_, `Óbitos` = NA_integer_,
                       `Média/dia` = round(m_c / m_d, 2)))
  }, na = "")

  output$t_dados <- renderTable({
    base_dia() |> select(dia, n, clima) |> mutate(dia = format(dia, "%d/%m/%Y")) |>
      rename(Dia = dia, Óbitos = n, !!nome_var() := clima) |> head(200)
  })

  output$baixar <- downloadHandler(
    filename = function() sprintf("obitos_clima_mrj_%s_a_%s.csv", input$periodo[1], input$periodo[2]),
    content = function(file) write_csv(base_dia() |> select(dia, n, all_of(unname(VARS_CLIMA))), file)
  )
}

shinyApp(ui, server)
