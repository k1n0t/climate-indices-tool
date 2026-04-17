# 🌍 Climate Indices Automation Tool (ETCCDI) - v5.0.1
> *Ferramenta Acadêmica Avançada para Cálculo, Análise e Visualização de 27 Índices Climáticos*

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![ETCCDI](https://img.shields.io/badge/Standard-ETCCDI%2FWMO-green.svg)](https://etccdi.pacificclimate.org/)
[![GUI](https://img.shields.io/badge/Interface-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)



 📑 Índice
- [Qual o Intuito?](#-qual-o-intuito)
- [Principais Funcionalidades](#-principais-funcionalidades)
- [Metodologia Aplicada](#-metodologia-aplicada)
- [Instalação e Requisitos](#-instalação-e-requisitos)
- [Como Usar](#-como-usar)
- [Como Contribuir](#-como-contribuir)
- [Citação e Referências](#-citação-e-referências)



 🎯 Qual o Intuito?

Esta aplicação foi desenvolvida para automatizar, padronizar e democratizar a análise climatológica baseada nos índices recomendados pelo ETCCDI (*Expert Team on Climate Change Detection and Indices*). Seus objetivos principais são:

- ✅ Eliminar a repetição manual de cálculos estatísticos e geração de gráficos em estudos climáticos.  
- ✅ Garantir conformidade internacional com os padrões da WMO/ETCCDI para detecção de mudanças climáticas.  
- ✅ Entregar resultados prontos para publicação científica, com 25+ gráficos em alta resolução (300 DPI), tabelas consolidadas e métricas de tendência.  
- ✅ Facilitar o acesso a pesquisadores e estudantes por meio de uma interface gráfica (GUI) intuitiva, sem necessidade de conhecimento prévio em programação.  
- ✅ Corrigir automaticamente inconsistências de unidades, convertendo índices termodinâmicos de Kelvin para Celsius, alinhando-se às convenções climatológicas padrão.



 ✨ Principais Funcionalidades

Além do cálculo rigoroso dos índices, a ferramenta atua como um laboratório completo de análise de dados climáticos:
* Geração Automática de Visualizações Científicas: Mais de 25 gráficos prontos para artigos (Séries temporais, Heatmaps de anomalias, Violin plots por década, Boxplots comparativos, Gráficos de radar, Scatter plots, KDE).
* Consolidação Estatística: Tendências lineares (R² e valor-p), normalização Z-score, decomposição sazonal e análise de extremos por percentis.
* Exportação Otimizada: Relatórios estatísticos exportados diretamente em formatos tabulares (`.csv`/`.xlsx`), facilitando a inclusão em teses e dissertações.



 📐 Metodologia Aplicada

O pipeline de processamento segue rigorosamente a literatura climatológica, estruturado em 6 etapas principais:

# 1. Ingestão e Pré-processamento
- Leitura de arquivos `.csv` (compatível nativamente com dados NASA POWER).
- Identificação e pulo automático de cabeçalhos (ex: `-END HEADER-`).
- Mesclagem por `YEAR` e `DOY` (Day of Year) e conversão para índice temporal `datetime`.
- Tratamento automatizado de dados faltantes/inválidos (`-999` → `NaN`).

# 2. Estruturação Multidimensional
- Conversão para `xarray.Dataset`, otimizando operações massivas.
- Resampling anual (`freq='YS'`) aplicado a todos os índices.

# 3. Definição da Climatologia de Referência (Período Base)
- Janela padrão: 1981–2010 (ajustável diretamente via GUI).
- Cálculo de percentis diários (`percentile_doy`) com janela móvel de 5 dias para suavização sazonal.
- Percentis utilizados: P10, P90 (temperatura), P95, P99 (precipitação).

# 4. Cálculo dos 27 Índices ETCCDI
Utilização do motor numérico `xclim` para garantir reprodutibilidade e conformidade CF/SI:

| Absolutos | `TXx`, `TNn`, `SU25`, `FD0`, `Rx1day`, `CDD`, `CWD`, `PRCPTOT` |
| Percentílicos/Relativos | `TX90p`, `TN10p`, `WSDI`, `CSDI`, `R95pTOT`, `R99pTOT` |

> 🔥 Nota sobre Correção de Unidade: A ferramenta realiza conversão explícita de índices termodinâmicos de Kelvin para Celsius (`- 273.15`), acompanhada de validação pós-processamento.

# 5. Análise Estatística Avançada
- Agregação anual robusta (remoção de duplicatas).
- Cálculo de tendências por Mínimos Quadrados.
- Decomposição sazonal via `statsmodels`.
- Autocorrelação e coeficiente de variação.

# 6. Pipeline de Visualização
Arquitetura construída sobre `matplotlib` e `seaborn`, parametrizada para estética acadêmica (incluindo médias móveis de 3, 5 e 10 anos).



 📦 Instalação e Requisitos

# Pré-requisitos
Certifique-se de ter o Python 3.8+ instalado em sua máquina. 

# Passo a Passo

1. Clone o repositório:
```bash
git clone [https://github.com/k1n0t/climate-indices-tool.git]
cd climate-indices-tool
