## plot from multiple files.
## each is stored in a json format
## as a list of tuples
## coming from multiple threads or processes.

import matplotlib 
import matplotlib.pyplot as plt
import json
import collections

nslices = 40
aggregate = []

for n in range(1,nslices+1):

	handle = open("../data/kfcp." + str(n))
	results = json.load(handle)
	handle.close()
	aggregate.extend(results)

print "total examples ", len(aggregate)


totals = collections.Counter()
positives = collections.Counter()
kvalues = set()
xvalues = set()

for (k,x,result) in aggregate:
	kvalues.add(k)
	xvalues.add(x)

	totals[(k,x)] += 1
	if result == 1:
		positives[(k,x)] += 1

k_range = list(kvalues)
k_range.sort()
x_range = list(xvalues)
x_range.sort()

legend = []
for k in k_range:
	legend.append("$k="+ str(k)+ "$")
	plotx = []
	ploty = []
	for x in x_range:
		n = totals[(k,x)]
		if n > 0:
			# valid data point
			np = positives[(k,x)]
			ratio = float(np)/float(n)
			plotx.append(x)
			ploty.append(ratio)

	plt.plot(plotx,ploty,"o-")

axes = plt.gca()
axes.set_ylim([0,1.1])
plt.legend(legend, loc='upper right')
plt.xlabel('$|P_L|$')
plt.ylabel('k-FCP')

#plt.legend(legend, loc='lower right')
plt.savefig('../figures/figure_cnf_kfcp_1000.pdf')
