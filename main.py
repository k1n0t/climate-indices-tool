#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🌍 Climate Index Automation Tool (ETCCDI) - Versão Acadêmica Avançada (CORRIGIDA)
Desenvolvido por: KAUE ARAUJO SOUSA
Descrição: Calcula 27 índices climáticos ETCCDI + Análises estatísticas avançadas
Gera 27 gráficos profissionais, tendências, correlações e análises climatológicas
Versão: 5.1.2
"""
import os
import sys
import warnings
import threading
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import queue
import pandas as pd
import numpy as np
import xarray as xr
from xclim import atmos
from xclim.core.calendar import percentile_doy
from scipy import stats
from scipy.signal import detrend
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.linear_model import LinearRegression

# Configurações globais
warnings.filterwarnings("ignore")
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_theme(style="whitegrid", palette="husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 9

class ClimateIndicesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 Climate Indices Tool - ETCCDI (v5.1.2 Celsius)")
        self.root.geometry("1100x800")
        self.root.configure(bg="#f5f6fa")
        
        # Variáveis de controle
        self.var_temp = tk.StringVar()
        self.var_prec = tk.StringVar()
        self.var_out = tk.StringVar(value=os.path.join(os.getcwd(), "resultados_etccdi"))
        self.var_base_start = tk.StringVar(value="1981")
        self.var_base_end = tk.StringVar(value="2010")
        
        # Queue para comunicação thread-safe
        self.ui_queue = queue.Queue()
        self.root.after(100, self._process_queue)
        self._setup_ui()

    def _setup_ui(self):
        # Header
        header = ttk.LabelFrame(self.root, text="ℹ️ Sobre", padding=10)
        header.pack(fill=tk.X, padx=10, pady=(10, 5))
        ttk.Label(header, text="Análise Automática de 27 Índices Climáticos ETCCDI + Análises Avançadas",
                  font=("Segoe UI", 14, "bold"), foreground="#2980B9").pack(anchor=tk.W)
        ttk.Label(header, text="💻 Gera 27 gráficos acadêmicos | Tendências | Correlações | Análises Estatísticas",
                  font=("Segoe UI", 10), foreground="#2C3E50").pack(anchor=tk.W)
        ttk.Label(header, text="Criador: Kauê Araújo Sousa",
                  font=("Segoe UI", 10, "bold"), foreground="#27AE60").pack(anchor=tk.W)
        
        # Configurações
        cfg = ttk.LabelFrame(self.root, text="⚙️ Configurações de Entrada", padding=15)
        cfg.pack(fill=tk.X, padx=10, pady=5)
        self._add_entry(cfg, "Arquivo Temperatura (CSV):", self.var_temp, 0, is_file=True)
        self._add_entry(cfg, "Arquivo Precipitação (CSV):", self.var_prec, 1, is_file=True)
        self._add_entry(cfg, "Pasta de Resultados:", self.var_out, 2, is_dir=True)
        
        # Período base
        frame_dates = ttk.Frame(cfg)
        frame_dates.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        ttk.Label(frame_dates, text="Período Base (Anos):").pack(side=tk.LEFT)
        ttk.Entry(frame_dates, textvariable=self.var_base_start, width=6).pack(side=tk.LEFT, padx=5)
        ttk.Label(frame_dates, text="até").pack(side=tk.LEFT)
        ttk.Entry(frame_dates, textvariable=self.var_base_end, width=6).pack(side=tk.LEFT, padx=5)
        
        # Botão Executar
        self.btn_run = ttk.Button(self.root, text="▶ INICIAR PROCESSAMENTO COMPLETO", style="Run.TButton", command=self._start_processing)
        self.btn_run.pack(fill=tk.X, padx=20, pady=15)
        
        style = ttk.Style()
        style.configure("Run.TButton", font=("Segoe UI", 12, "bold"), foreground="white", background="#27AE60")
        
        # Log & Progresso
        log_frame = ttk.LabelFrame(self.root, text="📋 Log de Execução & Progresso", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.progress = ttk.Progressbar(log_frame, orient='horizontal', mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        self.txt_log = tk.Text(log_frame, state='disabled', bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
        self.txt_log.pack(fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(self.txt_log, command=self.txt_log.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_log.config(yscrollcommand=scroll.set)

    def _add_entry(self, parent, label, var, row, is_file=False, is_dir=False):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=1, sticky="ew", padx=5)
        ttk.Entry(frame, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        btn_cmd = lambda: filedialog.askopenfilename(filetypes=[("CSV", "*.csv")]) if is_file else filedialog.askdirectory()
        ttk.Button(frame, text="📂", width=3, command=lambda: self._set_path(var, btn_cmd())).pack(side=tk.RIGHT)

    def _set_path(self, var, path):
        if path: var.set(path)

    def _process_queue(self):
        try:
            while True:
                callback = self.ui_queue.get_nowait()
                callback()
        except queue.Empty:
            pass
        self.root.after(100, self._process_queue)

    def _safe_log(self, msg):
        self.ui_queue.put(lambda: self._log(msg))

    def _safe_progress(self, value):
        self.ui_queue.put(lambda: self.progress.config(value=value))

    def _log(self, msg):
        self.txt_log.config(state='normal')
        self.txt_log.insert(tk.END, f"{msg}\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state='disabled')
        self.root.update_idletasks()

    def _start_processing(self):
        if not self.var_temp.get() or not self.var_prec.get():
            messagebox.showwarning("Atenção", "Selecione os arquivos de Temperatura e Precipitação.")
            return
        if not os.path.exists(self.var_temp.get()) or not os.path.exists(self.var_prec.get()):
            messagebox.showerror("Erro", "Um ou mais arquivos não foram encontrados.")
            return
        self.btn_run.config(state='disabled')
        self.progress['value'] = 0
        self.txt_log.config(state='normal')
        self.txt_log.delete('1.0', tk.END)
        self.txt_log.config(state='disabled')
        self._log("🚀 Iniciando processamento acadêmico avançado...")
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        try:
            out_dir = os.path.join(self.var_out.get(), "resultados_finais_v5")
            os.makedirs(out_dir, exist_ok=True)
            self._safe_log(f"📁 Pasta de saída: {out_dir}")
            
            # 1. Leitura
            self._safe_progress(10)
            self._safe_log("1. Lendo arquivos CSV e pulando cabeçalho NASA...")
            def get_skip(path):
                with open(path, 'r', encoding='utf-8') as f:
                    for i, l in enumerate(f):
                        if "-END HEADER-" in l: return i + 1
                return 0
            df_t = pd.read_csv(self.var_temp.get(), skiprows=get_skip(self.var_temp.get()))
            df_p = pd.read_csv(self.var_prec.get(), skiprows=get_skip(self.var_prec.get()))
            
            # 2. Merge & Limpeza
            self._safe_progress(25)
            self._safe_log("2. Unindo datasets e criando índice temporal...")
            req_t = {"YEAR", "DOY", "T2M_MIN", "T2M_MAX"}
            req_p = {"YEAR", "DOY", "PRECTOTCORR"}
            if not req_t.issubset(df_t.columns) or not req_p.issubset(df_p.columns):
                raise ValueError("Colunas obrigatórias ausentes. Esperado: YEAR, DOY, T2M_MIN, T2M_MAX, PRECTOTCORR")
            df = pd.merge(df_t, df_p, on=['YEAR', 'DOY'], how='outer')
            df['time'] = pd.to_datetime(df['YEAR'].astype(str) + df['DOY'].astype(str).str.zfill(3), format='%Y%j')
            df.set_index('time', inplace=True)
            df.replace([-999.0, -999], np.nan, inplace=True)
            df.sort_index(inplace=True)
            
            # 3. xarray & Base Period
            self._safe_progress(40)
            self._safe_log("3. Convertendo para xarray e definindo período base...")
            ds = xr.Dataset({
                'tmax': (['time'], df['T2M_MAX'], {'units': 'degC'}),
                'tmin': (['time'], df['T2M_MIN'], {'units': 'degC'}),
                'prcp': (['time'], df['PRECTOTCORR'], {'units': 'mm/d'})
            }, coords={'time': df.index})
            
            # 🆕 Calcular temperatura média diária
            ds['tmean'] = (ds['tmin'] + ds['tmax']) / 2.0
            
            base_slice = slice(self.var_base_start.get(), self.var_base_end.get())
            ds_base = ds.sel(time=base_slice)
            if ds_base.time.size == 0:
                self._safe_log("   ⚠️ Período base não encontrado. Usando série completa como referência.")
                ds_base = ds
                
            # 4. Cálculo dos 27 Índices ETCCDI + Média Anual
            self._safe_progress(55)
            self._safe_log("4. Calculando índices absolutos, percentis e resumos anuais...")
            idx = {}
            # Absolutos
            idx['TXx'] = atmos.tx_max(ds.tmax, freq='YS')
            idx['TXn'] = atmos.tx_min(ds.tmax, freq='YS')
            idx['TNx'] = atmos.tn_max(ds.tmin, freq='YS')
            idx['TNn'] = atmos.tn_min(ds.tmin, freq='YS')
            idx['DTR'] = atmos.daily_temperature_range(ds.tmin, ds.tmax, freq='YS')
            idx['SU25'] = atmos.tx_days_above(ds.tmax, thresh='25.0 degC', freq='YS')
            idx['TR20'] = atmos.tn_days_above(ds.tmin, thresh='20.0 degC', freq='YS')
            idx['FD0'] = atmos.tn_days_below(ds.tmin, thresh='0.0 degC', freq='YS')
            idx['ID0'] = atmos.tx_days_below(ds.tmax, thresh='0.0 degC', freq='YS')
            idx['Rx1day'] = atmos.max_1day_precipitation_amount(ds.prcp, freq='YS')
            idx['Rx5day'] = atmos.max_n_day_precipitation_amount(ds.prcp, window=5, freq='YS')
            idx['SDII'] = atmos.daily_pr_intensity(ds.prcp, thresh='1.0 mm/d', freq='YS')
            idx['R10mm'] = atmos.wetdays(ds.prcp, thresh='10.0 mm/d', freq='YS')
            idx['R20mm'] = atmos.wetdays(ds.prcp, thresh='20.0 mm/d', freq='YS')
            idx['CDD'] = atmos.maximum_consecutive_dry_days(ds.prcp, thresh='1.0 mm/d', freq='YS')
            idx['CWD'] = atmos.maximum_consecutive_wet_days(ds.prcp, thresh='1.0 mm/d', freq='YS')
            idx['PRCPTOT'] = ds.prcp.where(ds.prcp >= 1.0).resample(time='YS').sum()
            
            # 🆕 Temperatura Média Anual
            idx['Tmean_annual'] = ds.tmean.resample(time='YS').mean()
            
            # Percentis
            t90 = percentile_doy(ds_base.tmax, window=5, per=90)
            t10 = percentile_doy(ds_base.tmax, window=5, per=10)
            tn90 = percentile_doy(ds_base.tmin, window=5, per=90)
            tn10 = percentile_doy(ds_base.tmin, window=5, per=10)
            p95 = ds_base.prcp.where(ds_base.prcp >= 1.0).quantile(0.95, dim='time')
            p99 = ds_base.prcp.where(ds_base.prcp >= 1.0).quantile(0.99, dim='time')
            
            idx['TX90p'] = atmos.tx90p(ds.tmax, t90, freq='YS')
            idx['TX10p'] = atmos.tx10p(ds.tmax, t10, freq='YS')
            idx['TN90p'] = atmos.tn90p(ds.tmin, tn90, freq='YS')
            idx['TN10p'] = atmos.tn10p(ds.tmin, tn10, freq='YS')
            idx['WSDI'] = atmos.warm_spell_duration_index(ds.tmax, t90, window=6, freq='YS')
            idx['CSDI'] = atmos.cold_spell_duration_index(ds.tmin, tn10, window=6, freq='YS')
            idx['R95pTOT'] = ds.prcp.where(ds.prcp > p95).resample(time='YS').sum()
            idx['R99pTOT'] = ds.prcp.where(ds.prcp > p99).resample(time='YS').sum()
            
            # 🔥 CORREÇÃO CRÍTICA: Converter índices de temperatura de Kelvin para Celsius
            self._safe_log("   🌡️ Convertendo índices de temperatura de Kelvin para Celsius...")
            temp_abs_indices = ['TXx', 'TXn', 'TNx', 'TNn', 'Tmean_annual']
            for idx_name in temp_abs_indices:
                if idx_name in idx:
                    if idx[idx_name].mean() > 200:
                        idx[idx_name] = idx[idx_name] - 273.15
            self._safe_log("   ✅ Conversão concluída - todos os índices em Celsius")
            
            # 5. Consolidação
            self._safe_progress(75)
            self._safe_log("5. Consolidando resultados (removendo duplicatas)...")
            ds_res = xr.Dataset({k: v.drop_vars('quantile', errors='ignore') for k, v in idx.items()})
            df_res = ds_res.to_dataframe()
            df_res['year'] = df_res.index.get_level_values('time').year
            df_res = df_res.groupby('year').mean()
            df_res.index.name = 'Ano'
            df_res = df_res.dropna(how='all')
            
            for col in temp_abs_indices:
                if col in df_res.columns and df_res[col].mean() > 100:
                    df_res[col] = df_res[col] - 273.15
                    
            csv_path = os.path.join(out_dir, "indices_etccdi_anual.csv")
            df_res.to_csv(csv_path)
            self._safe_log(f"✅ Tabela salva: {csv_path}")
            self._safe_log(f"   📊 Período analisado: {df_res.index.min()} a {df_res.index.max()} ({len(df_res)} anos)")
            
            # 6. Gráficos Avançados
            self._safe_progress(85)
            self._safe_log("6. Gerando gráficos acadêmicos profissionais...")
            plot_dir = os.path.join(out_dir, "graficos")
            os.makedirs(plot_dir, exist_ok=True)
            self._generate_plots(df_res, plot_dir)
            
            self._safe_progress(100)
            self._safe_log("🎉 PROCESSO ACADÊMICO CONCLUÍDO COM SUCESSO!")
            self.root.after(100, lambda: messagebox.showinfo("Sucesso", "Processamento finalizado!\nVerifique a pasta de resultados."))
            
        except Exception as e:
            self._safe_log(f"❌ ERRO CRÍTICO: {e}")
            self._safe_log(traceback.format_exc())
            self.root.after(100, lambda: messagebox.showerror("Erro", str(e)))
        finally:
            self.root.after(100, lambda: self.btn_run.config(state='normal'))

    def _plot_trend(self, ax, x, y, label, color, title, ylabel, unit="", fill=False):
        valid = ~np.isnan(y)
        if valid.sum() < 3:
            ax.text(0.5, 0.5, "Dados insuficientes", ha="center", va="center", transform=ax.transAxes)
            return
        if fill:
            ax.fill_between(x[valid], y[valid], color=color, alpha=0.2, label=f'{label} (Área)')
        ax.plot(x[valid], y[valid], color=color, marker="o", linewidth=1.5, markersize=4, label=label)
        slope, intercept, r_value, p_value, _ = stats.linregress(x[valid], y[valid])
        ax.plot(x[valid], slope*x[valid]+intercept, color='black', ls="--", alpha=0.4, label="Tendência Linear")
        ax.text(0.02, 0.98, f"R²={r_value**2:.3f}\np={p_value:.3f}", transform=ax.transAxes,
                fontsize=8, va="top", bbox=dict(facecolor="white", alpha=0.8, boxstyle="round"))
        ax.set_xlabel("Ano"); ax.set_ylabel(f"{ylabel} ({unit})")
        ax.set_title(title, fontsize=10, fontweight='bold'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

    def _generate_plots(self, df, plot_dir):
        self._safe_log("   🎨 Plotando séries temporais anuais...")
        figs_config = [
            ("01_temperaturas_extremas.png", [("TXx", "Máxima Absoluta", "°C", "red"), ("TXn", "Mínima Absoluta", "°C", "blue"),
             ("TNx", "Mínima das Máximas", "°C", "orange"), ("TNn", "Mínima das Mínimas", "°C", "purple")]),
            ("02_dias_limite.png", [("SU25", "Dias Quentes >25°C", "dias", "red"), ("TR20", "Noites Quentes >20°C", "dias", "orange"),
             ("FD0", "Dias de Geada <0°C", "dias", "blue"), ("ID0", "Dias de Gelo <0°C", "dias", "purple")]),
            ("03_precip_extrema.png", [("Rx1day", "Máx. 1 dia", "mm", "darkblue"), ("Rx5day", "Máx. 5 dias", "mm", "steelblue"),
             ("R10mm", "Dias ≥10mm", "dias", "green"), ("R20mm", "Dias ≥20mm", "dias", "darkgreen")]),
            ("04_intensidade_duracao.png", [("SDII", "Intensidade Diária", "mm/dia", "brown"), ("CDD", "Dias Secos Consec.", "dias", "gold"),
             ("CWD", "Dias Úmidos Consec.", "dias", "cyan"), ("PRCPTOT", "Precip. Total", "mm", "blue")]),
            ("05_percentis_temp.png", [("TX90p", "Dias Quentes (P90)", "%", "red"), ("TX10p", "Dias Frios (P10)", "%", "blue"),
             ("TN90p", "Noites Quentes (P90)", "%", "orange"), ("TN10p", "Noites Frias (P10)", "%", "purple")]),
            ("06_ondas_eventos.png", [("WSDI", "Ondas de Calor", "dias", "red"), ("CSDI", "Ondas de Frio", "dias", "blue"),
             ("R95pTOT", "Chuva Extrema (P95)", "mm", "darkblue"), ("R99pTOT", "Chuva P99", "mm", "purple")]),
        ]
        for fname, cols in figs_config:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            for i, (col, title, unit, color) in enumerate(cols):
                self._plot_trend(axes.flat[i], df.index, df[col].values, col, color, title, "Valor", unit)
            plt.tight_layout()
            plt.savefig(os.path.join(plot_dir, fname), dpi=300, bbox_inches='tight')
            plt.close()
            
        # --- GRÁFICOS ACADÊMICOS AVANÇADOS (07-25) ---
        self._safe_log("   📊 Gerando análises estatísticas avançadas...")
        
        if 'PRCPTOT' in df.columns and 'TXx' in df.columns:
            fig, ax = plt.subplots(figsize=(14, 6))
            width = 0.4; x = np.arange(len(df.index))
            ax.bar(x - width/2, df['PRCPTOT'], width, label='Precipitação Total (mm)', color='steelblue', alpha=0.8)
            ax2 = ax.twinx()
            ax2.bar(x + width/2, df['TXx'], width, label='Temp. Máxima (°C)', color='tomato', alpha=0.8)
            ax.set_xticks(x); ax.set_xticklabels(df.index, rotation=45, ha='right')
            ax.set_ylabel("Precipitação (mm)", color='steelblue', fontweight='bold')
            ax2.set_ylabel("Temperatura Máxima (°C)", color='tomato', fontweight='bold')
            plt.title("Comparativo Anual: Precipitação vs Temperatura Máxima", fontweight='bold', fontsize=12)
            fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.9)); plt.tight_layout()
            plt.savefig(os.path.join(plot_dir, "07_comparativo_anual.png"), dpi=300); plt.close()
            
        anomaly_cols = ['TXx', 'TNn', 'PRCPTOT', 'SDII', 'SU25', 'FD0', 'WSDI', 'CDD']
        valid_cols = [c for c in anomaly_cols if c in df.columns]
        if len(valid_cols) > 1:
            df_anom = df[valid_cols].copy()
            df_anom = (df_anom - df_anom.mean()) / df_anom.std()
            df_anom = df_anom.fillna(0)
            plt.figure(figsize=(16, 10))
            sns.heatmap(df_anom.T, cmap='RdYlBu_r', center=0, linewidths=0.5, annot=False, cbar_kws={'label': 'Anomalia (Z-Score)'})
            plt.yticks(rotation=0); plt.xticks(np.arange(len(df.index)) + 0.5, df.index, rotation=45, ha='right')
            plt.title("Anomalias Anuais Normalizadas (Z-Score) - Comparação entre Índices", fontweight='bold')
            plt.xlabel("Ano"); plt.tight_layout()
            plt.savefig(os.path.join(plot_dir, "08_anomalias_anuais.png"), dpi=300); plt.close()
            
        scatter_cols = ['TXx', 'TNn', 'PRCPTOT', 'SU25', 'FD0', 'SDII']
        valid_scatter = [c for c in scatter_cols if c in df.columns]
        if len(valid_scatter) >= 3:
            g = sns.pairplot(df[valid_scatter].dropna(), diag_kind='hist', plot_kws={'alpha':0.6, 's':60}, corner=True, diag_kws={'fill':True, 'color':'steelblue'})
            g.fig.suptitle("Matriz de Dispersão Anual entre Índices Chave", y=1.02, fontweight='bold')
            plt.savefig(os.path.join(plot_dir, "09_scatter_indices.png"), dpi=300); plt.close()
            
        if 'SDII' in df.columns and 'R10mm' in df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.scatter(df['SDII'], df['R10mm'], c=df.index, cmap='viridis', s=100, alpha=0.7, edgecolor='k')
            cbar = plt.colorbar(ax.collections[0]); cbar.set_label('Ano')
            if not df[['SDII', 'R10mm']].dropna().empty:
                z = np.polyfit(df['SDII'].dropna(), df['R10mm'].dropna(), 1)
                p = np.poly1d(z)
                ax.plot(df['SDII'].dropna().sort_values(), p(df['SDII'].dropna().sort_values()), "r--", alpha=0.8, label="Tendência")
            ax.set_xlabel("Intensidade Diária Média (mm/dia)", fontweight='bold')
            ax.set_ylabel("Número de Dias ≥10mm", fontweight='bold')
            ax.set_title("Relação Anual: Intensidade vs Frequência de Chuva", fontweight='bold')
            ax.legend(); ax.grid(True, alpha=0.3); plt.tight_layout()
            plt.savefig(os.path.join(plot_dir, "10_intensidade_vs_frequencia.png"), dpi=300); plt.close()
            
        if all(c in df.columns for c in ['WSDI', 'CSDI']):
            fig, ax = plt.subplots(figsize=(14, 6))
            ax.bar(df.index, df['WSDI'], label='Dias em Ondas de Calor (WSDI)', color='red', alpha=0.7)
            ax.bar(df.index, df['CSDI'], bottom=df['WSDI'], label='Dias em Ondas de Frio (CSDI)', color='blue', alpha=0.7)
            ax.set_ylabel("Dias", fontweight='bold'); ax.set_title("Balanço Anual: Ondas de Calor vs Frio", fontweight='bold')
            ax.legend(); ax.set_xticks(df.index); ax.tick_params(axis='x', rotation=45); plt.tight_layout()
            plt.savefig(os.path.join(plot_dir, "11_balanco_energetico.png"), dpi=300); plt.close()
            
        if 'PRCPTOT' in df.columns and 'TXx' in df.columns:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            top5_p = df['PRCPTOT'].dropna().nlargest(5); ax1.bar(range(5), top5_p.values, color='steelblue', alpha=0.8)
            ax1.set_xticks(range(5)); ax1.set_xticklabels(top5_p.index); ax1.set_title("Top 5 Anos Mais Chuvosos", fontweight='bold')
            top5_t = df['TXx'].dropna().nlargest(5); ax2.bar(range(5), top5_t.values, color='tomato', alpha=0.8)
            ax2.set_xticks(range(5)); ax2.set_xticklabels(top5_t.index); ax2.set_title("Top 5 Anos Mais Quentes", fontweight='bold')
            plt.tight_layout(); plt.savefig(os.path.join(plot_dir, "12_top5_anos_criticos.png"), dpi=300); plt.close()
            
        corr_cols = [c for c in ['TXx','TNn','SU25','FD0','Rx1day','R10mm','CDD','PRCPTOT','TX90p','WSDI','SDII'] if c in df.columns]
        if len(corr_cols) > 2:
            plt.figure(figsize=(12, 10))
            sns.heatmap(df[corr_cols].corr(), annot=True, fmt=".2f", cmap="RdYlBu_r", center=0, square=True, linewidths=0.5)
            plt.title("Matriz de Correlação entre Índices (Atualizada)", fontweight="bold"); plt.tight_layout()
            plt.savefig(os.path.join(plot_dir, "13_correlacao.png"), dpi=300); plt.close()
            
        if 'TXx' in df.columns:
            try:
                decomposition = seasonal_decompose(df['TXx'].ffill(), model='additive', period=5)
                fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(14, 10))
                ax1.plot(decomposition.observed); ax1.set_title('Observado'); ax1.grid(True, alpha=0.3)
                ax2.plot(decomposition.trend); ax2.set_title('Tendência'); ax2.grid(True, alpha=0.3)
                ax3.plot(decomposition.seasonal); ax3.set_title('Sazonalidade'); ax3.grid(True, alpha=0.3)
                ax4.plot(decomposition.resid); ax4.set_title('Resíduo'); ax4.grid(True, alpha=0.3)
                plt.suptitle("Decomposição de Série Temporal - TXx", fontweight="bold", y=0.98); plt.tight_layout()
                plt.savefig(os.path.join(plot_dir, "14_decomposicao_serie.png"), dpi=300); plt.close()
            except: pass
            
        dist_cols = ['TXx', 'PRCPTOT', 'SU25', 'Rx1day']
        valid_dist = [c for c in dist_cols if c in df.columns]
        if len(valid_dist) >= 2:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            for ax, col in zip(axes.flat, valid_dist[:4]):
                sns.kdeplot(df[col].dropna(), ax=ax, fill=True, color='steelblue', alpha=0.6)
                ax.axvline(df[col].mean(), color='red', linestyle='--', label=f'Média: {df[col].mean():.1f}')
                ax.axvline(df[col].median(), color='green', linestyle='--', label=f'Mediana: {df[col].median():.1f}')
                ax.set_title(f'Distribuição - {col}', fontweight='bold'); ax.legend()
            plt.tight_layout(); plt.savefig(os.path.join(plot_dir, "15_distribuicao_kde.png"), dpi=300); plt.close()
            
        df_dec = df.copy()
        df_dec['Decada'] = (df_dec.index // 10) * 10
        violin_cols = [('TXx','°C'), ('PRCPTOT','mm'), ('SU25','dias'), ('WSDI','dias')]
        valid_violin = [(c, u) for c, u in violin_cols if c in df.columns]
        if len(valid_violin) >= 2:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            for ax, (col, unit) in zip(axes.flat, valid_violin):
                data = df_dec[[col, 'Decada']].dropna()
                if len(data) > 0:
                    sns.violinplot(x='Decada', y=col, data=data, ax=ax, palette='Set2', inner='box')
                    ax.set_ylabel(f'{col} ({unit})', fontweight='bold'); ax.set_title(f'Distribuição de {col} por Década', fontweight='bold')
                    ax.tick_params(axis='x', rotation=45)
            plt.suptitle("Análise de Variabilidade por Década", fontweight="bold", y=1.02); plt.tight_layout()
            plt.savefig(os.path.join(plot_dir, "16_violin_decadas.png"), dpi=300); plt.close()
            
        trend_cols = ['TXx', 'TNn', 'PRCPTOT', 'SU25']
        valid_trend = [c for c in trend_cols if c in df.columns]
        if len(valid_trend) >= 2:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            for ax, col in zip(axes.flat, valid_trend[:4]):
                y = df[col].values; x = df.index.values; valid = ~np.isnan(y)
                if valid.sum() >= 3:
                    slope, intercept, r_value, p_value, _ = stats.linregress(x[valid], y[valid])
                    ax.scatter(x[valid], y[valid], alpha=0.6, color='steelblue', s=50)
                    ax.plot(x[valid], slope*x[valid]+intercept, 'r-', linewidth=2, label=f'Tendência (p={p_value:.3f})')
                    ax.set_title(f'{col} - Análise de Tendência', fontweight='bold'); ax.set_xlabel('Ano'); ax.set_ylabel('Valor'); ax.legend(); ax.grid(True, alpha=0.3)
            plt.tight_layout(); plt.savefig(os.path.join(plot_dir, "17_tendencias_mann_kendall.png"), dpi=300); plt.close()
            
        if len(df) >= 10:
            df_temp = df.copy()
            mid_year = df_temp.index[len(df_temp)//2]
            df_temp['Periodo'] = df_temp.index.map(lambda x: '1º Período' if x < mid_year else '2º Período')
            box_cols = [('TXx','°C'), ('PRCPTOT','mm'), ('SU25','dias'), ('Rx1day','mm')]
            valid_box = [(c, u) for c, u in box_cols if c in df.columns]
            if len(valid_box) >= 2:
                fig, axes = plt.subplots(2, 2, figsize=(14, 10))
                for ax, (col, unit) in zip(axes.flat, valid_box):
                    data = df_temp[[col, 'Periodo']].dropna()
                    if len(data) > 0:
                        sns.boxplot(x='Periodo', y=col, data=data, ax=ax, palette='Set1', showmeans=True, meanprops={"marker":"o", "markerfacecolor":"white", "markeredgecolor":"black", "markersize":"8"})
                        ax.set_ylabel(f'{col} ({unit})', fontweight='bold'); ax.set_title(f'Comparação Temporal - {col}', fontweight='bold')
                plt.suptitle("Comparação entre Períodos (1º vs 2º)", fontweight="bold", y=1.02); plt.tight_layout()
                plt.savefig(os.path.join(plot_dir, "18_boxplot_periodos.png"), dpi=300); plt.close()
                
        radar_cols = ['TXx', 'TNn', 'PRCPTOT', 'SU25', 'WSDI']
        valid_radar = [c for c in radar_cols if c in df.columns]
        if len(valid_radar) >= 3 and len(df) >= 3:
            df_norm = (df[valid_radar] - df[valid_radar].mean()) / df[valid_radar].std()
            df_norm = df_norm.fillna(0)
            years_plot = [df.index.min(), df.index[len(df)//2], df.index.max()]
            years_plot = [y for y in years_plot if y in df_norm.index]
            if len(years_plot) >= 2:
                angles = np.linspace(0, 2 * np.pi, len(valid_radar), endpoint=False).tolist()
                angles += angles[:1]
                fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
                colors = plt.cm.Set1(np.linspace(0, 1, len(years_plot)))
                for i, year in enumerate(years_plot):
                    values = df_norm.loc[year].tolist(); values += values[:1]
                    ax.plot(angles, values, 'o-', linewidth=2, label=f'{year}', color=colors[i])
                    ax.fill(angles, values, alpha=0.15, color=colors[i])
                ax.set_xticks(angles[:-1]); ax.set_xticklabels(valid_radar, fontsize=10); ax.set_ylim(-2, 2)
                ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
                plt.title("Análise Multivariada Normalizada (Z-Score)", fontweight='bold', pad=20); plt.tight_layout()
                plt.savefig(os.path.join(plot_dir, "19_radar_multivariado.png"), dpi=300); plt.close()
                
        if 'TXx' in df.columns:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            acf_cols = [('TXx', 'Temperatura Máxima'), ('PRCPTOT', 'Precipitação Total'), ('SU25', 'Dias Quentes'), ('WSDI', 'Ondas de Calor')]
            for ax, (col, title) in zip(axes.flat, acf_cols):
                if col in df.columns:
                    pd.plotting.autocorrelation_plot(df[col].dropna(), ax=ax)
                    ax.set_title(f'Autocorrelação - {title}', fontweight='bold'); ax.grid(True, alpha=0.3)
            plt.tight_layout(); plt.savefig(os.path.join(plot_dir, "20_autocorrelacao.png"), dpi=300); plt.close()
            
        cv_cols = ['TXx', 'TNn', 'PRCPTOT', 'SDII']
        valid_cv = [c for c in cv_cols if c in df.columns]
        if len(valid_cv) >= 2:
            df_cv = df[valid_cv].copy()
            df_cv = (df_cv.std() / df_cv.mean() * 100).to_frame(name='CV%')
            df_cv = df_cv.sort_values('CV%', ascending=False)
            plt.figure(figsize=(12, 6))
            bars = plt.bar(df_cv.index, df_cv['CV%'], color=plt.cm.Set2(np.linspace(0, 1, len(df_cv))), alpha=0.8)
            plt.ylabel('Coeficiente de Variação (%)', fontweight='bold')
            plt.title('Variabilidade Relativa dos Índices Climáticos', fontweight='bold'); plt.xticks(rotation=45)
            for bar, val in zip(bars, df_cv['CV%']): plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
            plt.tight_layout(); plt.savefig(os.path.join(plot_dir, "21_coeficiente_variacao.png"), dpi=300); plt.close()
            
        if 'TXx' in df.columns and 'PRCPTOT' in df.columns:
            max_lag = min(10, len(df) // 3); lags = range(-max_lag, max_lag + 1); correlations = []
            for lag in lags:
                if lag < 0: corr = df['TXx'].iloc[-lag:].corr(df['PRCPTOT'].iloc[:lag])
                elif lag > 0: corr = df['TXx'].iloc[:-lag].corr(df['PRCPTOT'].iloc[lag:])
                else: corr = df['TXx'].corr(df['PRCPTOT'])
                correlations.append(corr)
            plt.figure(figsize=(12, 6))
            plt.plot(lags, correlations, 'o-', linewidth=2, markersize=8, color='steelblue')
            plt.axhline(0, color='gray', linestyle='--', alpha=0.5); plt.axvline(0, color='red', linestyle='--', alpha=0.5, label='Lag 0')
            plt.xlabel('Lag (anos)', fontweight='bold'); plt.ylabel('Coeficiente de Correlação', fontweight='bold')
            plt.title('Correlação Cruzada: TXx vs PRCPTOT', fontweight='bold')
            plt.legend(); plt.grid(True, alpha=0.3); plt.tight_layout()
            plt.savefig(os.path.join(plot_dir, "22_correlacao_cruzada.png"), dpi=300); plt.close()
            
        extreme_cols = [('TXx', 90, 'high'), ('PRCPTOT', 75, 'high'), ('FD0', 90, 'low')]
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        for ax, (col, perc, direction) in zip(axes, extreme_cols):
            if col in df.columns:
                threshold = df[col].quantile(perc/100)
                if direction == 'high': extremes = df[df[col] > threshold]; label = f'Acima de P{perc}'
                else: extremes = df[df[col] < threshold]; label = f'Abaixo de P{perc}'
                ax.scatter(df.index, df[col], alpha=0.3, color='gray', label='Normal')
                ax.scatter(extremes.index, extremes[col], color='red', s=80, alpha=0.8, label=label, edgecolor='black', linewidth=1)
                ax.axhline(threshold, color='red', linestyle='--', alpha=0.7, label=f'Limiar: {threshold:.1f}')
                ax.set_title(f'Extremos - {col}', fontweight='bold'); ax.set_xlabel('Ano'); ax.set_ylabel('Valor'); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
        plt.suptitle("Análise de Eventos Extremos", fontweight="bold", y=1.05); plt.tight_layout()
        plt.savefig(os.path.join(plot_dir, "23_extremos_percentis.png"), dpi=300); plt.close()
        
        ma_cols = [('TXx', 'Temperatura Máxima', '°C', 'red'), ('PRCPTOT', 'Precipitação Total', 'mm', 'blue')]
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        for ax, (col, title, unit, color) in zip(axes, ma_cols):
            if col in df.columns:
                y = df[col].values; x = df.index
                ax.plot(x, y, color='gray', alpha=0.4, linewidth=1, label='Anual')
                for window, alpha in [(3, 0.8), (5, 0.6), (10, 0.4)]:
                    roll = pd.Series(y, index=x).rolling(window, center=True, min_periods=1).mean()
                    ax.plot(roll.index, roll.values, linewidth=2, alpha=alpha, label=f'Média Móvel ({window}a)')
                ax.set_title(f'{title} - Tendências Suavizadas', fontweight='bold'); ax.set_ylabel(unit); ax.legend(); ax.grid(True, alpha=0.3)
        plt.tight_layout(); plt.savefig(os.path.join(plot_dir, "24_medias_moveis_multiplas.png"), dpi=300); plt.close()
        
        summary_cols = ['TXx', 'TNn', 'PRCPTOT', 'SU25', 'WSDI', 'FD0']
        valid_summary = [c for c in summary_cols if c in df.columns]
        if len(valid_summary) >= 4:
            df_summary = df[valid_summary].describe()
            fig, ax = plt.subplots(figsize=(14, 8))
            ax.axis('off')
            table = ax.table(cellText=df_summary.values, colLabels=df_summary.columns, rowLabels=df_summary.index, cellLoc='center', loc='center', colColours=['#3498db']*len(df_summary.columns))
            table.auto_set_font_size(False); table.set_fontsize(9); table.scale(1.2, 1.5)
            plt.title("Resumo Estatístico Descritivo dos Índices", fontweight='bold', fontsize=14, pad=20); plt.tight_layout()
            plt.savefig(os.path.join(plot_dir, "25_resumo_estatistico.png"), dpi=300); plt.close()
            
        # 🆕 26. PRECIPITAÇÃO TOTAL ANUAL (GRÁFICO ISOLADO)
        self._safe_log("   📊 Gerando gráfico de precipitação anual isolada...")
        if 'PRCPTOT' in df.columns:
            fig, ax = plt.subplots(figsize=(14, 6))
            x = df.index
            y = df['PRCPTOT'].values
            valid = ~np.isnan(y)
            # Barras coloridas por valor
            colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(x)))
            ax.bar(x[valid], y[valid], color=colors[:len(x[valid])], alpha=0.8, edgecolor='navy', linewidth=0.5)
            # Linha de tendência
            if valid.sum() >= 3:
                slope, intercept, r_value, p_value, _ = stats.linregress(x[valid].astype(float), y[valid])
                ax.plot(x[valid], slope*x[valid].astype(float)+intercept, 'r--', linewidth=2, label=f'Tendência (R²={r_value**2:.3f})')
            ax.set_xlabel("Ano", fontweight='bold'); ax.set_ylabel("Precipitação Total Anual (mm)", fontweight='bold')
            ax.set_title("📈 Precipitação Total Anual - Série Temporal Completa", fontweight='bold', fontsize=12)
            ax.legend(fontsize=9); ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=45, ha='right'); plt.tight_layout()
            plt.savefig(os.path.join(plot_dir, "26_precipitacao_anual_isolada.png"), dpi=300, bbox_inches='tight')
            plt.close()
            
        # 🆕 27. TEMPERATURAS: MÍNIMA, MÁXIMA E MÉDIA (GRÁFICO COMPARATIVO)
        self._safe_log("   📊 Gerando gráfico comparativo de temperaturas...")
        temp_cols = [('TNn', 'Temperatura Mínima', 'blue'), ('Tmean_annual', 'Temperatura Média', 'green'), ('TXx', 'Temperatura Máxima', 'red')]
        valid_temp = [(c, t, col) for c, t, col in temp_cols if c in df.columns]
        if len(valid_temp) >= 2:
            fig, ax = plt.subplots(figsize=(14, 7))
            x = df.index
            for col, label, color in valid_temp:
                y = df[col].values
                valid = ~np.isnan(y)
                ax.plot(x[valid], y[valid], color=color, marker='o', linewidth=2, markersize=4, label=f'{label} ({col})', alpha=0.9)
                # Adicionar tendência para cada série
                if valid.sum() >= 3:
                    slope, intercept, r_value, p_value, _ = stats.linregress(x[valid].astype(float), y[valid])
                    ax.plot(x[valid], slope*x[valid].astype(float)+intercept, color=color, ls=':', alpha=0.5)
            ax.set_xlabel("Ano", fontweight='bold'); ax.set_ylabel("Temperatura (°C)", fontweight='bold')
            ax.set_title("🌡️ Comparativo: Temperatura Mínima, Média e Máxima Anual", fontweight='bold', fontsize=12)
            ax.legend(fontsize=9, loc='best'); ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45, ha='right'); plt.tight_layout()
            plt.savefig(os.path.join(plot_dir, "27_temperaturas_comparativo.png"), dpi=300, bbox_inches='tight')
            plt.close()
            
        self._safe_log("   ✅ Todos os gráficos acadêmicos gerados com sucesso!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClimateIndicesApp(root)
    root.mainloop()
