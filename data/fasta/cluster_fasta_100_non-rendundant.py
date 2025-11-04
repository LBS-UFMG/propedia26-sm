#!/usr/bin/env python3
"""
cluster_fasta_100.py

Agrupa sequências 100% idênticas de um FASTA (peptides.fasta) e grava seq_100_clusters.tsv.

Entrada esperada (FASTA):
>1GMH-E-F | Peptide
CGVPAIQPVL
>1GMH-E-G | Peptide
CGVPAIQPVL

Saída (TSV, tab-separated):
id    cluster_ids
1GMH-E-F    1GMH-E-F,1GMH-E-G

Uso:
    python cluster_fasta_100.py peptides.fasta seq_100_clusters.tsv
Se nenhum argumento for passado, usa 'peptides.fasta' e 'seq_100_clusters.tsv'.
"""

import sys
from pathlib import Path
from collections import OrderedDict

def parse_fasta(fasta_path):
    """
    Generator que itera sobre (header, sequence) de um FASTA,
    juntando linhas de sequência e ignorando linhas vazias.
    """
    header = None
    seq_lines = []
    with open(fasta_path, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.rstrip('\n')
            if not line:
                continue
            if line.startswith('>'):
                # yield previous
                if header is not None:
                    seq = ''.join(seq_lines).replace(' ', '').upper()
                    yield header, seq
                header = line[1:].strip()  # remove '>' e espaços
                seq_lines = []
            else:
                seq_lines.append(line.strip())
        # last record
        if header is not None:
            seq = ''.join(seq_lines).replace(' ', '').upper()
            yield header, seq

def extract_id_from_header(header):
    """
    Extrai o identificador que vem antes do '|' no header.
    Ex: "1GMH-E-F | Peptide" -> "1GMH-E-F"
    Se não houver '|', retorna a linha inteira do header (após strip).
    """
    if '|' in header:
        left = header.split(' | ', 1)[0]
    else:
        left = header
    return left.strip()

def cluster_fasta(fasta_path, out_tsv_path):
    fasta_path = Path(fasta_path)
    out_tsv_path = Path(out_tsv_path)

    if not fasta_path.exists():
        print(f"Erro: arquivo {fasta_path} não encontrado.", file=sys.stderr)
        sys.exit(1)

    # manter ordem de primeira ocorrência -> OrderedDict map sequence -> list(ids)
    seq_to_ids = OrderedDict()

    total = 0
    for header, seq in parse_fasta(fasta_path):
        total += 1
        seq_id = extract_id_from_header(header)
        # use sequence as key (already uppercased, no spaces)
        if seq in seq_to_ids:
            seq_to_ids[seq].append(seq_id)
        else:
            seq_to_ids[seq] = [seq_id]

    # gravar TSV: primeira coluna = id (primeiro id do grupo), segunda = lista de ids separadas por vírgula
    with open(out_tsv_path, 'w', encoding='utf-8') as outfh:
        outfh.write("id\tcluster_ids\n")
        for seq, ids in seq_to_ids.items():
            representative = ids[0]
            cluster_str = ",".join(ids)
            outfh.write(f"{representative}\t{cluster_str}\n")

    print(f"Concluído. {total} sequências lidas -> {len(seq_to_ids)} clusters únicos.")
    print(f"Arquivo salvo em: {out_tsv_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Agrupa sequências 100% idênticas de um FASTA e grava TSV.")
    parser.add_argument('fasta', nargs='?', default='peptides.fasta', help='Arquivo FASTA de entrada (default: peptides.fasta)')
    parser.add_argument('out', nargs='?', default='seq_100_clusters.tsv', help='Arquivo TSV de saída (default: seq_100_clusters.tsv)')
    args = parser.parse_args()
    cluster_fasta(args.fasta, args.out)
