# Rodar como root no servidor (biblioteca do sistema):
#   sudo R -f instalar_pacotes.R
pk <- c("shiny", "bslib", "dplyr", "tidyr", "readr", "lubridate", "plotly")
falta <- setdiff(pk, rownames(installed.packages()))
if (length(falta)) install.packages(falta, repos = "https://cloud.r-project.org")
cat("Pacotes OK:", paste(pk, collapse = ", "), "\n")
