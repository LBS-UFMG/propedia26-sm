entrada = "../seq_100_clusters.tsv"

base = "SBP.tsv"

dados = {}
tudo = {}
proba = {}

# carrega dados
with open(entrada) as f:
	linhas = f.readlines()

	for linha in linhas:
		l = linha.split('\t')

		if l[0] == 'cluster_ids' or l[0] == 'id':
			continue #ignora primeira linha

		dados[l[0]] = l[1].strip().split(',')

		for i in l[1].strip().split(','):
			if i != 'cluster_ids':
				tudo[i] = -1


with open(base) as f:
	linhas = f.readlines()

	for linha in linhas:
		l = linha.split('\t')

		if l[0] == '#':
			continue #ignora primeira linha

		id = l[0]
		prob = round(float(l[3]),2)

		proba[id]=prob


for i in tudo:

	for j in dados[i]:
		try:
			tudo[i] = proba[j]
			break
		except: 
			ignora = True

with open('_'+base,'w') as f:
	for i in tudo:
		print(i,tudo[i],sep='\t',file=f)

	