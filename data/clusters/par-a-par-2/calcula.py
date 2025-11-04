entrada = "seq100_clusters-NR.tsv"
ref = "reference.tsv"
dados = {}
tudo = {}
proba = {}

for i in open(ref).readlines():
	l = i.split('\t')
	tudo[l[0]]='-'

# carrega dados
with open(entrada) as f:
	linhas = f.readlines()

	for linha in linhas:
		l = linha.split('\t')

		id = l[0]
		equipe = l[1].strip().split(',')

		for i in equipe:
			if i in tudo:
				tudo[i] = id


with open('_'+entrada,'w') as f:
	for i in tudo:
		print(i,tudo[i],sep='\t',file=f)

	