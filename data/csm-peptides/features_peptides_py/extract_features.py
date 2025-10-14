from Bio import SeqIO
import peptides
import pandas as pd
import numpy as np
import glob 

# === Configurações ===

for arq_fasta in glob.glob('../fasta/*fasta'):

    fasta_file = arq_fasta   # caminho do seu arquivo FASTA

    output_file = arq_fasta.replace('.fasta','')+".tsv"  # saída em formato TSV

    # === Leitura das sequências FASTA ===
    records = list(SeqIO.parse(fasta_file, "fasta"))
    print(f"[INFO] {len(records)} sequências carregadas do arquivo FASTA.")

    # === Extração das features ===
    dados = []
    for rec in records:
        seq = str(rec.seq)
        
        try:
            pep = peptides.Peptide(seq)
            desc = pep.descriptors()  # retorna todas as features disponíveis
            
            # Adiciona informações básicas
            desc["id"] = rec.id
            desc["sequence"] = seq
            
            dados.append(desc)
        except Exception as e:
            print(f"[ERRO] Falha ao processar {rec.id}: {e}")

    # === Criação do DataFrame ===
    df = pd.DataFrame(dados)

    # === Reordena colunas (id, sequence vêm primeiro) ===
    cols = ["id", "sequence"] + [c for c in df.columns if c not in ("id", "sequence")]
    df = df[cols]
    df = df.applymap(lambda x: round(x, 2) if isinstance(x, (int, float, np.floating)) else x)

    # === Exporta para TSV ===
    df.to_csv(output_file, sep="\t", index=False)
    print(f"[OK] Arquivo salvo em: {output_file}")

    # === Mostra primeiras linhas ===
    #print(df.head())
