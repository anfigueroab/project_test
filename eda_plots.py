import argparse
from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os


def ensure_dir(d: Path):
    d.mkdir(parents=True, exist_ok=True)


def save_fig(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main(input_path: Path, out_dir: Path):
    ensure_dir(out_dir)
    print(f"Cargando datos desde: {input_path}")
    df = pd.read_excel(input_path)
    print(f"Filas: {len(df)}, Columnas: {len(df.columns)}")

    # Detectar columnas numéricas relevantes
    num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    print('Columnas numéricas detectadas:', num_cols)

    # 1) Histogramas para variables numéricas
    if num_cols:
        for c in num_cols:
            fig = plt.figure(figsize=(6,4))
            sns.histplot(df[c].dropna(), kde=True, bins=25)
            plt.title(f'Histograma - {c}')
            save_fig(fig, out_dir / f'hist_{c.replace(" ","_")}.png')

    # 2) Boxplots de estadísticas por 'Type 1' si existe
    if 'Type 1' in df.columns and num_cols:
        for c in num_cols:
            fig = plt.figure(figsize=(12,6))
            order = df.groupby('Type 1')[c].median().sort_values(ascending=False).index
            sns.boxplot(data=df, x='Type 1', y=c, order=order)
            plt.xticks(rotation=45)
            plt.title(f'Boxplot {c} por Type 1')
            save_fig(fig, out_dir / f'box_Type1_{c.replace(" ","_")}.png')

    # 3) Conteo de pokémon por 'Type 1'
    if 'Type 1' in df.columns:
        fig = plt.figure(figsize=(10,6))
        sns.countplot(data=df, y='Type 1', order=df['Type 1'].value_counts().index)
        plt.title('Conteo por Type 1')
        save_fig(fig, out_dir / 'count_type1.png')

    # 4) Top 10 por 'Total' si existe
    if 'Total' in df.columns:
        top = df.sort_values('Total', ascending=False).head(10)
        fig = plt.figure(figsize=(10,6))
        sns.barplot(data=top, x='Total', y='Name')
        plt.title('Top 10 Pokémon por Total')
        save_fig(fig, out_dir / 'top10_total.png')

    # 5) Mapa de correlación
    if len(num_cols) > 1:
        corr = df[num_cols].corr()
        fig = plt.figure(figsize=(10,8))
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm')
        plt.title('Mapa de correlación (numéricas)')
        save_fig(fig, out_dir / 'corr_heatmap.png')

    # 6) Pairplot de las principales variables (muestreo si es muy grande)
    try:
        sample = df[num_cols].dropna()
        if len(sample) > 500:
            sample = sample.sample(500, random_state=0)
        if len(sample.columns) >= 2 and len(sample) > 10:
            pp = sns.pairplot(sample)
            pp.fig.suptitle('Pairplot (muestra)', y=1.02)
            pp.savefig(out_dir / 'pairplot_sample.png')
            plt.close(pp.fig)
    except Exception as e:
        print('Pairplot skipped:', e)

    print(f'Gráficos guardados en: {out_dir.resolve()}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Genera gráficos descriptivos desde Pokemon.xlsx')
    parser.add_argument('--input', '-i', type=Path, default=Path('datasets') / 'Pokemon.xlsx')
    parser.add_argument('--out', '-o', type=Path, default=Path('plots'))
    args = parser.parse_args()
    main(args.input, args.out)
