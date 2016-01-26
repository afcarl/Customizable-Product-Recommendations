from __future__ import division
import json
from pprint import pprint
from operator import itemgetter
import itertools
import copy
import csv
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
			if((int(j[u'Price']) > int(i[u'Price']))and(int(j[u'Value']) < int(i[u'Value']))):
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

# User input (Very naive, should have to do for now)
u = [u'0500GB',u'2GB',u'18.5 Inch',u'Windows 7',u'Intel i5',u'04GB']
x = [data[u'Hard Drive'],data[u'Graphics Card'],data[u'Monitor'],data[u'Operating System'],data[u'Processor'],data[u'RAM']]
c = 40000

# Remove those configurations that are less than the specified configuration
start = []
for i in range(len(u)):
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
		t1.append(int(sorted_x[i][j][u'Value'])-int(sorted_x[i][j-1][u'Value']))
		t2.append(int(sorted_x[i][j][u'Price'])-int(sorted_x[i][j-1][u'Price']))
	p.append(t1)
	w.append(t2)

# Initialize costs and profits
c_res = c
p_res = 0

pprint("User requirements:")
pprint(u)
print "\n"
knapsack = []

for i in range(len(sorted_x)):
	knapsack.append(sorted_x[i][0])

for i in range(len(sorted_x)):
	c_res = c_res - int(sorted_x[i][0][u'Price'])
	p_res = p_res + int(sorted_x[i][0][u'Value'])


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

a=[]
b=[]
for i in range(len(e_flat)):
	if e_flat[i]!=0:
		(x,y)=index_2d(e,e_flat[i])
		a.append(x)
		b.append(y)
# for i in range(len(a)):
# 	pprint(a[i])
# 	pprint(sorted_x[a[i]][b[i]])
#Now, of the selected items above, we can replace in the knapsack in various combinations to get the candidate set of solutions.
#This should give us a good amount of possible solutions, giving the user various choices to choose from.

candidate_set=[]
cost=[]
candidate_set.append(knapsack)
temp=0
for item in knapsack:
	temp+=int(item['Price'])
cost.append(temp)

#One at a time from e_flat
for i in range(len(a)):
	temp1=copy.deepcopy(knapsack)
	temp1[a[i]]=sorted_x[a[i]][b[i]]
	temp2=0
	for j in range(len(temp1)):
		temp2+=int(temp1[j]['Price'])
	if(temp2<=c):
		candidate_set.append(temp1)
		cost.append(temp2)
for i in range(len(cost)):
	pprint(cost[i])
	pprint(candidate_set[i])




#Two at a time from sorted_x
# for i in range(len(a)):
# 	temp1=copy.deepcopy(knapsack)
# 	for j in range(i+1,len(a)):
# 		temp1[a[i]]=sorted_x[a[i]][b[i]]
# 		temp1[a[j]]=sorted_x[a[j]][b[j]]
# 		temp2=0
# 		for k in range(len(temp1)):
# 			temp2+=int(temp1[k]['Price'])
# 		if(temp2<=c):
# 			candidate_set.append(temp1)
# 			cost.append(temp2)

# #Three at a time from sorted_x
# for i in range(len(a)):
# 	temp1=copy.deepcopy(knapsack)
# 	for j in range(i+1,len(a)):
# 		for k in range(i+2,len(a)):
# 			temp1[a[i]]=sorted_x[a[i]][b[i]]
# 			temp1[a[j]]=sorted_x[a[j]][b[j]]
# 			temp1[a[k]]=sorted_x[a[k]][b[k]]
# 			temp2=0
# 			for l in range(len(temp1)):
# 				temp2+=int(temp1[l]['Price'])
# 			if(temp2<=c):
# 				candidate_set.append(temp1)
# 				cost.append(temp2)
# #Four at a time from sorted_x
# for i in range(len(a)):
# 	temp1=copy.deepcopy(knapsack)
# 	for j in range(i+1,len(a)):
# 		for k in range(i+2,len(a)):
# 			for l in range(i+3,len(a)):
# 				temp1[a[i]]=sorted_x[a[i]][b[i]]
# 				temp1[a[j]]=sorted_x[a[j]][b[j]]
# 				temp1[a[k]]=sorted_x[a[k]][b[k]]
# 				temp1[a[l]]=sorted_x[a[l]][b[l]]
# 				temp2=0
# 				for m in range(len(temp1)):
# 					temp2+=int(temp1[m]['Price'])
# 				if(temp2<=c):
# 					candidate_set.append(temp1)
# 					cost.append(temp2)
# #Five at a time from sorted_x
# for i in range(len(a)):
# 	temp1=copy.deepcopy(knapsack)
# 	for j in range(i+1,len(a)):
# 		for k in range(i+2,len(a)):
# 			for l in range(i+3,len(a)):
# 				for m in range(i+4,len(a)):
# 					temp1[a[i]]=sorted_x[a[i]][b[i]]
# 					temp1[a[j]]=sorted_x[a[j]][b[j]]
# 					temp1[a[k]]=sorted_x[a[k]][b[k]]
# 					temp1[a[l]]=sorted_x[a[l]][b[l]]
# 					temp1[a[m]]=sorted_x[a[m]][b[m]]
# 					temp2=0
# 					for n in range(len(temp1)):
# 						temp2+=int(temp1[n]['Price'])
# 					if(temp2<=c):
# 						candidate_set.append(temp1)
# 						cost.append(temp2)
# #Six at a time from sorted_x
# for i in range(len(a)):
# 	temp1=copy.deepcopy(knapsack)
# 	for j in range(i+1,len(a)):
# 		for k in range(i+2,len(a)):
# 			for l in range(i+3,len(a)):
# 				for m in range(i+4,len(a)):
# 					for n in range(i+5,len(a)):
# 						temp1[a[i]]=sorted_x[a[i]][b[i]]
# 						temp1[a[j]]=sorted_x[a[j]][b[j]]
# 						temp1[a[k]]=sorted_x[a[k]][b[k]]
# 						temp1[a[l]]=sorted_x[a[l]][b[l]]
# 						temp1[a[m]]=sorted_x[a[m]][b[m]]
# 						temp1[a[n]]=sorted_x[a[n]][b[n]]
# 						temp2=0
# 						for o in range(len(temp1)):
# 							temp2+=int(temp1[o]['Price'])
# 						if(temp2<=c):
# 							candidate_set.append(temp1)
# 							cost.append(temp2)
# pprint(len(candidate_set))
# # for i in range(len(candidate_set)):
# # 	pprint(candidate_set[i])
# # 	pprint(cost[i])
# p=[]
# for i in range(len(candidate_set)):
# 	s=""
# 	for item in candidate_set[i]:
# 		s+=item['Name']+", "
# 	p.append(s[:-1])
# print len(p)
# print len(cost)
# for i in range(len(cost)):
# 	p[i]=p[i]+" Cost : "+str(cost[i])
# print p
# p.reverse()

# with open('models.txt','wb') as f:
# 	for i in range(len(p)):
# 		f.write(p[i]+"\n")
# # with open('models.csv','ab') as f:
# # 	writer=csv.writer(f)
# # 	writer.writerows([p])