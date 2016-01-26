from __future__ import division
import re
import json
from pprint import pprint
from operator import itemgetter
import itertools
import copy
import timeit

begin=timeit.default_timer()
# Function to remove duplicates from a list
def remdup(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

# Function for pairwise iteration within a list
def pairwise(iterable):
	a, b = itertools.tee(iterable)
	next(b, None)
	return itertools.izip(a, b)

# Function to remove LP-Dominated items
def remove_lp(sorted_x):
	should_restart = True
	while should_restart == True:
		should_restart = False	
		for i,j in pairwise(sorted_x):
			if((float(j[u'Price']) > float(i[u'Price']))and(float(j[u'Value']) < float(i[u'Value']))):
				sorted_x.remove(j)
				should_restart = True
				break
	return sorted_x

def index_2d(myList, v):
    for i, x in enumerate(myList):
        if v in x:
            return (i, x.index(v))

# Load the features file
json_data=open('Feature_set.json')
data = json.load(json_data)
json_data.close()

# User input (Very naive, should have to do for now)
x = [data[u'TV'],data[u'Blu-Ray Players'],data[u'Receivers'],data[u'Universal Remote'],data[u'Speakers']]
q = [0,2]
u = [u'32 Inch', u'Blu-Ray with Wi-Fi',u'7 Channel',None,u'Floor Standing Speakers (2 pair)']
c = 3000

# Remove those configurations that are less than the specified configuration
start = []
for i in range(len(u)):
	if u[i] == None:
		start.append(0)
	else:
		start.append(map(itemgetter(u'Capacity'),x[i]).index(u[i]))
for i in range(len(start)):
	for j in range(start[i]):
		del(x[i][0])

# Assign profits
y=[]
for i in range(len(x)):
	y.append(remdup(map(itemgetter(u'Capacity'),x[i])))

for i in range(len(x)):
	for j in range(len(x[i])):
		if i in q:
			if u == None:
				a = float(re.findall(r'\d+.\d+|\d+',x[i][0])[0])
			else:
				a = float(re.findall(r'\d+.\d+|\d+',u[i])[0])
			b = float(re.findall(r'\d+.\d+|\d+',x[i][j][u'Capacity'])[0])
			bar = b/a
			x[i][j][u'Value'] = (1 - bar/float(x[i][j][u'Price'])) * bar
		else:	
			a = y[i].index(x[i][j][u'Capacity'])
			x[i][j][u'Value'] = a + 1

# Sort by price
sorted_x=[]
for i in range(len(x)):
	sorted_x.append(sorted(x[i], key=itemgetter(u'Price')))

# Remove LP-Dominated Items
for i in range((len(sorted_x))):
	sorted_x[i]=remove_lp(sorted_x[i])


# Calculate p, w
p = []
w = []

for i in range(len(sorted_x)):
	t1=[]
	t2=[]
	for j in range(1,len(sorted_x[i])):
		t1.append(float(sorted_x[i][j][u'Value'])-float(sorted_x[i][j-1][u'Value']))
		t2.append(float(sorted_x[i][j][u'Price'])-float(sorted_x[i][j-1][u'Price']))
	p.append(t1)
	w.append(t2)
r=1
for i in range(len(sorted_x)):
	for j in range(len(sorted_x[i])):
		sorted_x[i][j][u'Key']=r
		r+=1

# Initialize costs and profits
ck = 0
pk = 0

pprint("User Requirements: ")
pprint(c)
pprint(u)

knapsack = []

key=""
keys=[]

for i in range(len(sorted_x)):
	knapsack.append(sorted_x[i][0])
	key+=str(sorted_x[i][0][u'Key'])+'_'

key=key[:-1]
keys.append(copy.deepcopy(key))

for i in range(len(sorted_x)):
	ck = ck + float(sorted_x[i][0][u'Price'])
	pk = pk + float(sorted_x[i][0][u'Value'])

p_k=pk/ck
candidate_set=[]
profit_by_cost=[]
cost=[]
pprint("RECOMMENDATION 1")
pprint(pk/ck)
# pprint(knapsack)
candidate_set.append(copy.deepcopy(knapsack))
profit_by_cost.append(copy.deepcopy(p_k))
initial = copy.deepcopy(knapsack)
cost.append(copy.deepcopy(ck))
# Find the incremental efficiencies

m = max(max(w))

for i in range(len(w)):
	for j in range(len(w[i])):
		w[i][j] = w[i][j]/m

e = []

for i in range(len(p)):
	temp = [0.0]
	for j in range(len(p[i])):
		if (w[i][j]) == 0:
			temp.append(0.0)
		else:
			temp.append(p[i][j]/w[i][j])
	e.append(temp)

e_flat = sum(e,[])
e_flat.sort(reverse = True)
el=e_flat
# Greedy Algorithm Candidate Solutions
r = 1
i = 0
while i < (len(el)):
	(a,b) = index_2d(e,el[i])
	knapsack[a] = sorted_x[a][b]
	temp=""
	ck = 0
	pk = 0
	for j in knapsack:
		(m,n) = index_2d(sorted_x,j)
		ck = ck + float(sorted_x[m][n][u'Price'])
		pk = pk + float(sorted_x[m][n][u'Value'])
	p_k=pk/ck
	i = i + 1
	if (ck <= c):
		if r<20:
			for x in knapsack:
				temp+=str(x[u'Key'])+"_"
			temp=temp[:-1]
			if temp not in keys:
				keys.append(copy.deepcopy(temp))
				r = r + 1
				pprint("RECOMMENDATION "+str(r))
				pprint(pk/ck)
				# pprint(knapsack)
				candidate_set.append(copy.deepcopy(knapsack))
				profit_by_cost.append(copy.deepcopy(p_k))
				cost.append(copy.deepcopy(ck))
		else:
			break
	else:
		knapsack = copy.deepcopy(initial)
		el.pop(0)
		i = 0
pprint(profit_by_cost)
# pprint(candidate_set)
# top_10_index=zip(*sorted(enumerate(profit_by_cost), key=itemgetter(1)))[0][-10:]
# top_10_options=[]
# for i in top_10_index:
# 	top_10_options.append(candidate_set[i])
top_10_options=[]
pprint(top_10_options)
for i in range(10):
	top_10_options.append(candidate_set[i])
f=open('top10_unsorted.txt','wb')
for i in range(len(top_10_options)):
	for j in range(len(top_10_options[i])):
		f.write(top_10_options[i][j][u'Name']+",")
	f.write("\n")
f.close()

# f=open('candidate_set.txt','wb')
# for i in range(len(candidate_set)):
# 	for j in range(len(candidate_set[i])):
# 		f.write(candidate_set[i][j][u'Name']+",")
# 	f.write("\n")
# f.close()

# f=open('cost.txt','wb')
# for i in range(len(cost)):
# 	f.write(str(cost[i])+"\n")
# f.close()



# sum_of_profit=0
# for item in profit_by_cost:
# 	sum_of_profit+=item
# pprint ("Max of profit by cost is "+str((max(profit_by_cost))*1))
# pprint("Avg pk/ck is "+str((sum_of_profit/len(profit_by_cost))*1))

# end=timeit.default_timer()
# pprint ("Time elapsed is "+str(end-begin))