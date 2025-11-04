#!/usr/bin/env python3
"""
remove_g_columns.py

Lê todos os arquivos .tsv em uma pasta, remove as colunas
cujos nomes começam com 'g' (minúsculo) e salva de volta.

Uso:
    python remove_g_columns.py /caminho/para/a/pasta

Dependências:
    pip install pandas
"""

import pandas as pd
from pathlib import Path
import sys

def remove_g_columns_in_folder(folder_path):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Erro: a pasta {folder} não existe.")
        sys.exit(1)

    tsv_files = list(folder.glob("*.tsv"))
    if not tsv_files:
        print(f"⚠️ Nenhum arquivo .tsv encontrado em {folder}.")
        return

    print(f"📂 Encontrados {len(tsv_files)} arquivos TSV em {folder}\n")

    for file in tsv_files:
        print(f"➡️ Processando: {file.name}")
        try:
            df = pd.read_csv(file, sep="\t", dtype=str)  # lê tudo como texto para segurança
            original_cols = list(df.columns)

            # Seleciona colunas que NÃO começam com "g"
            cols_to_keep = [col for col in df.columns if not col.startswith("g")]
            removed_cols = [col for col in df.columns if col.startswith("g")]

            df = df[cols_to_keep]

            # Salvar sobrescrevendo o arquivo original
            df.to_csv(file, sep="\t", index=False)

            print(f"   ✔️ Removidas {len(removed_cols)} colunas começando com 'g'.")
        except Exception as e:
            print(f"   ❌ Erro ao processar {file.name}: {e}")

    print("\n✅ Processamento concluído!")

if __name__ == "__main__":
    # Pega o caminho da pasta por argumento ou usa o diretório atual
    folder_path = sys.argv[1] if len(sys.argv) > 1 else "."
    remove_g_columns_in_folder(folder_path)
