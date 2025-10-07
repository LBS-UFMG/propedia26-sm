import os
import pandas as pd

# Caminho da pasta contendo os arquivos CSV
pasta = "./"

# Itera por todos os arquivos CSV da pasta
for arquivo in os.listdir(pasta):
    if arquivo.endswith(".csv"):
        caminho_csv = os.path.join(pasta, arquivo)
        caminho_fasta = os.path.join(pasta, os.path.splitext(arquivo)[0] + ".fasta")
        
        # Lê o CSV (separado por tabulações)
        df = pd.read_csv(caminho_csv, sep=",", header=None)
        
        # Abre o arquivo fasta para escrita
        with open(caminho_fasta, "w") as fasta:
            for _, linha in df.iterrows():
                try:
                    sequencia = str(linha[1]).strip()
                    if sequencia == 'Peptide':
                        continue # ignora a primeira linha
                    classe = str(linha[2]).strip()
                    header = f">{sequencia}_{classe}"
                    fasta.write(f"{header}\n{sequencia}\n")
                except:
                    print('erro:', linha)
                    continue
        
        print(f"Arquivo gerado: {caminho_fasta}")
