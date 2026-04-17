Perfeito — aqui está o README inteiro em **formato raw (bloco único pronto pra copiar)**:

````markdown
# 🌍 Climate Indices Automation Tool (ETCCDI) — v5.1.2  
> Ferramenta avançada para cálculo, homogeneização e visualização de **27 índices climáticos (ETCCDI/WMO)**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)  
[![ETCCDI](https://img.shields.io/badge/Standard-ETCCDI%2FWMO-green.svg)](https://etccdi.pacificclimate.org/)  
[![GUI](https://img.shields.io/badge/Interface-Tkinter-orange.svg)](https://docs.python.org/3/library/tkinter.html)

---

## 🎯 Propósito

Esta ferramenta foi desenvolvida para **automatizar, padronizar e tornar acessível** a análise climatológica baseada nos índices do **ETCCDI (WMO)**.

Ela resolve problemas comuns em pesquisas climáticas ao:

- ✅ Eliminar tarefas repetitivas de cálculo e visualização  
- ✅ Garantir conformidade com padrões internacionais (ETCCDI/WMO)  
- ✅ Gerar resultados prontos para publicação científica (300 DPI)  
- ✅ Corrigir inhomogeneidades estatísticas em índices percentílicos  
- ✅ Disponibilizar uma **GUI intuitiva** (sem necessidade de programação)  
- ✅ Padronizar automaticamente unidades (Kelvin → Celsius)  

---

## ⚙️ Pipeline Metodológico

O processamento segue rigorosamente a literatura climatológica, estruturado em **6 etapas principais**:

### 1. 📥 Ingestão & Pré-processamento
- Leitura de arquivos `.csv` (compatíveis com NASA POWER)  
- Remoção automática de cabeçalhos (`-END HEADER-`)  
- Conversão para `datetime` via `YEAR + DOY`  
- Tratamento de valores inválidos (`-999 → NaN`)  

---

### 2. 📊 Estruturação com `xarray`
- Conversão para `xarray.Dataset` (alto desempenho)  
- Definição do período base (default: **1981–2010**)  
- Cálculo de percentis diários com janela móvel **5CD (5-day centered)**  

---

### 3. 🔬 Correção de Inhomogeneidade (Bootstrap)

Métodos tradicionais introduzem **descontinuidades artificiais** nos índices percentílicos.

Esta ferramenta implementa o método de:

📄 *Zhang et al. (2005) — Bootstrap leave-one-out*

**Como funciona:**
1. Remove temporariamente o ano avaliado  
2. Reconstrói a amostra mantendo o tamanho original  
3. Recalcula limiares percentílicos  
4. Repete o processo para múltiplas amostras  
5. Calcula a média das estimativas  

✔ Resultado: séries **homogêneas, robustas e sem “jumps” artificiais**

---

### 4. 📈 Cálculo dos Índices ETCCDI

Implementação baseada em `xclim` (compatível com padrões CF/SI)

#### 🔹 Índices Absolutos
`TXx`, `TXn`, `TNx`, `TNn`, `DTR`, `SU25`, `TR20`, `FD0`, `ID0`,  
`Rx1day`, `Rx5day`, `SDII`, `R10mm`, `R20mm`, `CDD`, `CWD`, `PRCPTOT`

#### 🔹 Índices Percentílicos
`TX90p`, `TX10p`, `TN90p`, `TN10p`,  
`WSDI`, `CSDI`, `R95pTOT`, `R99pTOT`

🔥 **Correção automática:** conversão de Kelvin → Celsius (`-273.15`)

---

### 5. 📉 Análise Estatística
- Tendência linear (OLS) + `R²` + valor-p  
- Normalização (Z-score)  
- Decomposição sazonal (`statsmodels`)  
- Autocorrelação e variabilidade  
- Análise de extremos climáticos  

---

### 6. 📊 Visualização Científica

Geração automática de **25+ gráficos** prontos para publicação:

- Séries temporais com tendência  
- Heatmaps (anomalias e correlação)  
- Boxplots e violin plots por década  
- Radar charts multivariados  
- Médias móveis (3, 5, 10 anos)  
- KDE e análise de distribuição  
- Análise de extremos por percentis  

📌 Destaques:
- Precipitação anual completa  
- Comparação de temperatura (mín/méd/máx)  

---

## 📦 Instalação

```bash
pip install pandas numpy xarray xclim scipy matplotlib seaborn statsmodels scikit-learn
````

---

## 🚀 Diferenciais

* ✔ Implementação do método de **Zhang et al. (2005)**
* ✔ Total conformidade com **ETCCDI/WMO**
* ✔ Pipeline completo (dados → análise → visualização)
* ✔ Interface gráfica amigável
* ✔ Resultados prontos para publicação

---

## 📚 Referência

Zhang, X., et al. (2005).
*"Avoiding inhomogeneity in percentile-based indices of temperature extremes."*
Journal of Climate.

```

---

Se quiser, posso te mandar uma versão ainda mais forte (nível projeto destaque no GitHub) com:
- badges de DOI / licença / downloads  
- GIF da interface  
- seção “How to Use” com exemplo real  

Só falar 👍
```
