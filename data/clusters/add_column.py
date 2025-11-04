#!/usr/bin/env python3
"""
add_clusters_to_propedia.py

Lê propedia26_v7.csv (sep=';') e adiciona colunas a partir de arquivos TSV em 'clusters/'.
Processa apenas arquivos cujo nome começa com '_' e termina com '.tsv'.
Cada arquivo de cluster não tem cabeçalho e tem formato:
    <id>\t<value>\n

Para cada arquivo '_NAME.tsv' cria coluna 'NAME' em propedia26_v8.csv com os valores mapeados por 'id'.

Uso:
    python add_clusters_to_propedia.py

Ou:
    python add_clusters_to_propedia.py /caminho/para/propedia26_v7.csv /caminho/para/clusters /caminho/para/propedia26_v8.csv
"""
from pathlib import Path
import pandas as pd
import sys

def load_kv_tsv(path):
    """
    Lê um tsv sem cabeçalho contendo pelo menos duas colunas (key, value).
    Retorna um dict key -> value. Remove espaços em torno das chaves.
    Se houver chaves duplicadas, o último valor prevalece.
    """
    # ler apenas as duas primeiras colunas, sem header
    df = pd.read_csv(path, sep='\t', header=None, usecols=[0,1], dtype=str, keep_default_na=False, na_values=[''])
    # nomear colunas
    df.columns = ['key', 'value']
    # strip em keys e values
    df['key'] = df['key'].astype(str).str.strip()
    # manter último em caso de duplicatas
    df = df.drop_duplicates(subset='key', keep='last')
    return dict(zip(df['key'], df['value']))

def main(propedia_fp='propedia26_v7.csv', clusters_dir='clusters', out_fp='propedia26_v8.csv'):
    propedia_path = Path(propedia_fp)
    clusters_path = Path(clusters_dir)
    out_path = Path(out_fp)

    if not propedia_path.exists():
        print(f"Erro: {propedia_path} não encontrado.", file=sys.stderr)
        sys.exit(1)
    if not clusters_path.exists() or not clusters_path.is_dir():
        print(f"Erro: pasta de clusters {clusters_path} não encontrada.", file=sys.stderr)
        sys.exit(1)

    # 1) Ler propedia como strings para preservar conteúdo original
    print("Lendo", propedia_path)
    propedia = pd.read_csv(propedia_path, sep=';', dtype=str, keep_default_na=False, na_values=[''])
    propedia.columns = propedia.columns.str.strip()

    if 'id' not in propedia.columns:
        print("Erro: coluna 'id' não encontrada em propedia26_v7.csv", file=sys.stderr)
        sys.exit(1)

    # garantir ids padronizados (strings sem espaços extras)
    propedia['id'] = propedia['id'].astype(str).str.strip()

    # 2) Encontrar arquivos que começam com '_' e terminam com '.tsv'
    cluster_files = sorted(p for p in clusters_path.glob('_*.tsv') if p.is_file())
    if not cluster_files:
        print(f"Aviso: nenhum arquivo _*.tsv encontrado em {clusters_path}. Saindo.", file=sys.stderr)
        sys.exit(0)

    print(f"Arquivos de cluster encontrados: {len(cluster_files)}")
    processed = []
    for fp in cluster_files:
        name_stem = fp.stem  # ex: '_AAP'
        # remover prefixo '_' se existir para nome da coluna
        col_name = name_stem.lstrip('_')
        print(f"Processando {fp.name} -> coluna '{col_name}'")

        try:
            kv = load_kv_tsv(fp)
        except Exception as e:
            print(f"  Erro ao ler {fp.name}: {e}", file=sys.stderr)
            continue

        # Mapear propedia['id'] para valores; se não encontrado, colocar empty string
        propedia[col_name] = propedia['id'].map(kv).fillna('')

        processed.append(fp.name)
        mapped = (propedia[col_name] != '').sum()
        print(f"  Mapeados: {mapped} / {len(propedia)}")

    # 3) Salvar resultado
    print("Salvando resultado em", out_path)
    propedia.to_csv(out_path, sep=';', index=False, na_rep='')

    print("Concluído. Arquivos processados:", processed)
    print(f"Arquivo salvo: {out_path}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Adicionar colunas de arquivos _*.tsv em clusters/ ao propedia26_v7.csv")
    parser.add_argument('propedia', nargs='?', default='propedia26_v7.csv', help='arquivo propedia26_v7.csv (sep=";")')
    parser.add_argument('clusters_dir', nargs='?', default='clusters', help='pasta contendo arquivos _*.tsv')
    parser.add_argument('out', nargs='?', default='propedia26_v8.csv', help='arquivo de saída (sep=";")')
    args = parser.parse_args()
    main(args.propedia, args.clusters_dir, args.out)
