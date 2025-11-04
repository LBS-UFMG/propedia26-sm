#!/usr/bin/env python3
"""
cluster_fasta_100_per_entry.py

Agrupa sequências 100% idênticas de um FASTA e gera um TSV com
uma linha por entrada do FASTA.

Entrada (ex. peptides.fasta):
>1GMH-E-F | Peptide
CGVPAIQPVL
>1GMH-E-G | Peptide
CGVPAIQPVL

Saída (seq_100_clusters.tsv):
id    cluster_ids
1GMH-E-F    1GMH-E-F,1GMH-E-G
1GMH-E-G    1GMH-E-F,1GMH-E-G

Uso:
    python cluster_fasta_100_per_entry.py peptides.fasta seq_100_clusters.tsv
Se não fornecer argumentos, usa 'peptides.fasta' e 'seq_100_clusters.tsv'.
"""

import sys
from pathlib import Path
from collections import OrderedDict

def parse_fasta_ordered(fasta_path):
    """
    Lê um FASTA e retorna duas estruturas:
    - entries: lista de tuples (seq_id, seq) na ordem de aparecimento
    - seq_to_ids: OrderedDict map seq -> list(ids) (ordem de primeira ocorrência)
    Sequências são normalizadas: concatenadas, sem espaços, uppercase.
    """
    entries = []
    seq_to_ids = OrderedDict()

    header = None
    seq_lines = []
    with open(fasta_path, 'r', encoding='utf-8') as fh:
        for raw in fh:
            line = raw.rstrip('\n')
            if not line:
                continue
            if line.startswith('>'):
                # finalizar record anterior
                if header is not None:
                    seq = ''.join(seq_lines).replace(' ', '').upper()
                    seq_id = extract_id_from_header(header)
                    entries.append((seq_id, seq))
                    if seq in seq_to_ids:
                        seq_to_ids[seq].append(seq_id)
                    else:
                        seq_to_ids[seq] = [seq_id]
                header = line[1:].strip()
                seq_lines = []
            else:
                seq_lines.append(line.strip())
        # último registro
        if header is not None:
            seq = ''.join(seq_lines).replace(' ', '').upper()
            seq_id = extract_id_from_header(header)
            entries.append((seq_id, seq))
            if seq in seq_to_ids:
                seq_to_ids[seq].append(seq_id)
            else:
                seq_to_ids[seq] = [seq_id]

    return entries, seq_to_ids

def extract_id_from_header(header):
    """
    Extrai a porção antes do '|' (se houver) e faz strip.
    Ex: "1GMH-E-F | Peptide" -> "1GMH-E-F"
    """
    if '|' in header:
        left = header.split('|', 1)[0]
    else:
        left = header
    return left.strip()

def write_clusters_per_entry(entries, seq_to_ids, out_path):
    """
    Para cada entrada (na ordem), escreve uma linha:
    id \t cluster_ids (vírgula-separados)
    """
    with open(out_path, 'w', encoding='utf-8') as outfh:
        outfh.write("id\tcluster_ids\n")
        for seq_id, seq in entries:
            cluster_ids = seq_to_ids.get(seq, [])
            cluster_str = ",".join(cluster_ids)
            outfh.write(f"{seq_id}\t{cluster_str}\n")

def main(fasta='peptides.fasta', out_tsv='seq_100_clusters.tsv'):
    fasta_path = Path(fasta)
    out_path = Path(out_tsv)

    if not fasta_path.exists():
        print(f"Erro: arquivo {fasta_path} não encontrado.", file=sys.stderr)
        sys.exit(1)

    print(f"Lendo FASTA: {fasta_path} ...")
    entries, seq_to_ids = parse_fasta_ordered(fasta_path)
    total_entries = len(entries)
    total_clusters = len(seq_to_ids)
    print(f"Entradas lidas: {total_entries}")
    print(f"Clusters únicos (sequências distintas): {total_clusters}")

    print(f"Escrevendo TSV: {out_path} ...")
    write_clusters_per_entry(entries, seq_to_ids, out_path)

    # verificação simples
    # contar linhas escritas (excluindo header) -> deve ser igual ao total_entries
    with open(out_path, 'r', encoding='utf-8') as fh:
        lines = sum(1 for _ in fh) - 1

    print(f"Linhas escritas (excluindo header): {lines}")
    if lines != total_entries:
        print("Aviso: número de linhas escritas difere do número de entradas lidas.", file=sys.stderr)
    else:
        print("Verificação OK: uma linha por entrada do FASTA.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Agrupa sequências 100% idênticas e gera TSV com uma linha por entrada do FASTA.")
    parser.add_argument('fasta', nargs='?', default='peptides.fasta', help='Arquivo FASTA de entrada')
    parser.add_argument('out', nargs='?', default='seq_100_clusters.tsv', help='Arquivo TSV de saída')
    args = parser.parse_args()
    main(args.fasta, args.out)
