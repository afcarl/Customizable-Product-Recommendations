from math import *
from pprint import pprint
from copy import deepcopy
rel=[2,2,3,5,5,3,3,4,5,3]
cg=0
for item in rel:
	cg+=item

pprint("Cumulative Gain = "+str(cg))

dcg=0
# dcg+=rel[0]
for i in range(len(rel)):
	dcg+=(((2**rel[i])-1)/log((rel[i]+1),2))

pprint("Discounted Cumulative Gain = "+str(dcg))

irel=deepcopy(rel)
irel.sort(reverse=True)
idcg=0

# idcg+=irel[0]
for i in range(len(irel)):
	idcg+=(((2**rel[i])-1)/log((irel[i]+1),2))

pprint("Ideal Discounted Cumulative Gain = "+str(idcg))

ndcg=dcg/idcg

pprint("Normalized Discounted Cumulative Gain = "+str(ndcg))