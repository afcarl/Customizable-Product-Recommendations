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
u = [u'2000GB',u'3GB',u'24 Inch',u'Linux/DOS',u'Intel i7',u'16GB']
x = [data[u'Hard Drive'],data[u'Graphics Card'],data[u'Monitor'],data[u'Operating System'],data[u'Processor'],data[u'RAM']]
q = [0,1,2,5,6]
c = 75000

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
# pprint("RECOMMENDATION 1")
# pprint(pk/ck)
# pprint(knapsack)
candidate_set.append(copy.deepcopy(knapsack))
profit_by_cost.append(copy.deepcopy(p_k))
initial = copy.deepcopy(knapsack)

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

#Two at a time replacement
a=[]
b=[]
for i in range(len(e_flat)):
	if e_flat[i]!=0:
		(x,y)=index_2d(e,e_flat[i])
		a.append(x)
		b.append(y)
for i in range(len(a)):
	temp1=copy.deepcopy(knapsack)
	temp1[a[i]]=sorted_x[a[i]][b[i]]
	ck=0
	pk=0
	temp=""
	for j in range(len(temp1)):
		ck+=int(temp1[j][u'Price'])
		pk+=int(temp1[j][u'Value'])
	p_k=pk/ck
	if(ck<=c):
		for x in temp1:
			temp+=str(x[u'Key'])+"_"
		temp=temp[:-1]
		if temp not in keys:
			keys.append(copy.deepcopy(temp))
			candidate_set.append(temp1)
			profit_by_cost.append(copy.deepcopy(p_k))

for i in range(len(a)):
	temp1=copy.deepcopy(knapsack)
	for j in range(i+1,len(a)):
		temp1[a[i]]=sorted_x[a[i]][b[i]]
		temp1[a[j]]=sorted_x[a[j]][b[j]]
		ck=0
		pk=0
		temp=""
		for j in range(len(temp1)):
			ck+=int(temp1[j][u'Price'])
			pk+=int(temp1[j][u'Value'])
		p_k=pk/ck
		if(ck<=c):
			for x in temp1:
				temp+=str(x[u'Key'])+"_"
			temp=temp[:-1]
			if temp not in keys:
				keys.append(copy.deepcopy(temp))
				candidate_set.append(temp1)
				profit_by_cost.append(copy.deepcopy(p_k))


# pprint(len(keys))
# pprint(len(candidate_set))
# pprint(keys)
for i in range(len(profit_by_cost)):
	pprint("RECOMMENDATION "+str(i+1))
	pprint(profit_by_cost[i])
	pprint(candidate_set[i])

sum_of_profit=0
for item in profit_by_cost:
	sum_of_profit+=item
pprint ("Max of profit by cost is "+str(max(profit_by_cost)))
pprint("Avg pk/ck is "+str(sum_of_profit/len(profit_by_cost)))

end=timeit.default_timer()
pprint ("Time elapsed is "+str(end-begin))