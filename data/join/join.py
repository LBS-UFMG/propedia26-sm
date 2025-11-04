#!/usr/bin/env python3
"""
merge_csvs_fixed.py

Versão corrigida do script para unir:
- propedia26_v6.csv (sep=';')
- main_14_10_20.csv (sep=',')

Produz propedia26_v7.csv (sep=';').

Comportamento:
- chave primária: 'id' (string)
- valores numéricos detectados em main_14_10_20.csv serão formatados com exatamente 2 casas decimais na saída
- quando houver conflito (mesmo id e mesma coluna), os valores de main_14_10_20.csv sobrescrevem os de propedia26_v6.csv
- corrige bug de KeyError ao reordenar colunas adicionando colunas faltantes do main ao resultado
- normaliza nomes de colunas com .strip()
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

def detect_numeric_columns(df):
    """Retorna lista de colunas que são numéricas em pelo menos 50% dos valores (exceto 'id')."""
    numeric_cols = []
    for col in df.columns:
        if col.lower() == 'id':
            continue
        converted = pd.to_numeric(df[col], errors='coerce')
        non_na = converted.notna().sum()
        total = len(converted)
        if total > 0 and (non_na / total) >= 0.5:
            numeric_cols.append(col)
    return numeric_cols

def main(propedia_fp='propedia26_v6.csv', main_fp='main_14_10_20.csv', out_fp='propedia26_v7.csv'):
    propedia_fp = Path(propedia_fp)
    main_fp = Path(main_fp)
    out_fp = Path(out_fp)

    if not propedia_fp.exists():
        print(f"Erro: arquivo {propedia_fp} não encontrado.", file=sys.stderr)
        sys.exit(1)
    if not main_fp.exists():
        print(f"Erro: arquivo {main_fp} não encontrado.", file=sys.stderr)
        sys.exit(1)

    # 1) Ler arquivos com os separadores corretos (ler como strings inicialmente)
    print("Lendo propedia26_v6.csv (sep=';') ...")
    propedia = pd.read_csv(propedia_fp, sep=';', dtype=str, keep_default_na=False, na_values=[''])
    print("Lendo main_14_10_20.csv (sep=',') ...")
    main = pd.read_csv(main_fp, sep=',', dtype=str, keep_default_na=False, na_values=[''])

    # 1.1) Normalizar nomes de colunas (strip) para evitar espaços extras
    propedia.columns = propedia.columns.str.strip()
    main.columns = main.columns.str.strip()

    # 2) Garantir a existência da coluna 'id' e normalizá-la como string
    if 'id' not in propedia.columns or 'id' not in main.columns:
        print("Erro: coluna 'id' não encontrada em um dos arquivos.", file=sys.stderr)
        sys.exit(1)

    propedia['id'] = propedia['id'].astype(str).str.strip()
    main['id'] = main['id'].astype(str).str.strip()

    # 3) Detectar colunas numéricas em 'main' e convertê-las para float (quando possível)
    numeric_cols_in_main = detect_numeric_columns(main)
    print("Colunas detectadas como numéricas em main:", numeric_cols_in_main)

    for col in numeric_cols_in_main:
        # converter strings vazias para NaN e depois para float
        main[col] = pd.to_numeric(main[col].replace('', np.nan), errors='coerce')

    # 4) Indexar por 'id'
    propedia = propedia.set_index('id')
    main = main.set_index('id')

    # 5) Tratar duplicatas de id: manter primeiro (pode ajustar conforme desejado)
    if not propedia.index.is_unique:
        print("Aviso: ids duplicados em propedia26_v6.csv - mantendo o primeiro por id.")
        propedia = propedia[~propedia.index.duplicated(keep='first')]
    if not main.index.is_unique:
        print("Aviso: ids duplicados em main_14_10_20.csv - mantendo o primeiro por id.")
        main = main[~main.index.duplicated(keep='first')]

    # 6) Preparar resultado inicial como propedia reindexado com todos os ids
    all_ids = propedia.index.union(main.index)
    result = propedia.reindex(all_ids)

    # 6.1) Adicionar ao result todas as colunas que existem em main mas não em result,
    # para que update possa sobrescrever/colocar valores nestas colunas
    missing_cols = [c for c in main.columns if c not in result.columns]
    if missing_cols:
        print(f"Adicionando colunas faltantes ao resultado: {missing_cols}")
        for c in missing_cols:
            result[c] = np.nan

    # 7) Agora podemos atualizar/sobrescrever com os valores de main (main tem prioridade)
    result.update(main)

    # 8) Formatar as colunas numéricas originadas do main para terem exatamente 2 casas decimais
    for col in numeric_cols_in_main:
        if col in result.columns:
            # converter (novamente) para float para garantir formatação correta
            result[col] = pd.to_numeric(result[col], errors='coerce')
            # formatar: manter vazio se NaN
            result[col] = result[col].map(lambda x: f"{x:.2f}" if pd.notna(x) else "")

    # 9) Reset index para ter coluna 'id' novamente
    result = result.reset_index()

    # 10) Construir ordem final de colunas:
    propedia_cols = list(pd.read_csv(propedia_fp, sep=';', nrows=0).columns.str.strip())
    main_cols = list(pd.read_csv(main_fp, sep=',', nrows=0).columns.str.strip())

    final_cols = []
    for c in propedia_cols:
        if c not in final_cols:
            final_cols.append(c)
    for c in main_cols:
        if c not in final_cols:
            final_cols.append(c)
    # garantir inclusão de quaisquer colunas adicionais presentes no result
    for c in result.columns:
        if c not in final_cols:
            final_cols.append(c)

    # 10.1) Evitar KeyError: selecionar apenas as colunas que realmente existem em result,
    # preservando a ordem proposta em final_cols
    final_cols_existing = [c for c in final_cols if c in result.columns]

    # Reorder result columns
    result = result[final_cols_existing]

    # 11) Salvar arquivo final com sep=';'
    print(f"Gravando resultado em {out_fp} (sep=';') ...")
    result.to_csv(out_fp, sep=';', index=False, na_rep='')

    print("Concluído com sucesso.")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Merge two CSVs into propedia26_v7.csv (fixed)")
    parser.add_argument('propedia', nargs='?', default='propedia26_v6.csv', help='Arquivo propedia (sep=";")')
    parser.add_argument('main', nargs='?', default='main_14_10_25.csv', help='Arquivo main (sep=",")')
    parser.add_argument('out', nargs='?', default='propedia26_v7.csv', help='Arquivo de saída (sep=";")')
    args = parser.parse_args()
    main(args.propedia, args.main, args.out)
