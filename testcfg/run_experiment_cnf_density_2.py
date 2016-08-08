# run experiment on fcp

import matplotlib.pyplot as plt
import random


import cfg
import earleyparser
import uniformsampler
import generatecfg
print "Running experiment on CFGs with the FCP"
 
random.seed(7)
factory = generatecfg.CnfFactory()
factory.number_nonterminals = 10
factory.number_terminals = 100
factory.number_binary_productions = 30
factory.number_lexical_productions = 100

number_grammars = 5
max_length = 20
samples_per_length = 10
for g in xrange(number_grammars):
	print "Grammar ", g
	x = []
	y = []
	grammar = factory.make_grammar()
	
 	us = uniformsampler.UniformSampler(grammar,max_length)
 	for l in xrange(1,max_length +1):
 		density = us.density(l)
 		x.append(l)
 		y.append(density)
 	plt.plot(x,y,"bx-")
 	x = []
 	y = []
 	for l in xrange(1,max_length +1):
 		density = us.string_density(l, samples_per_length)
 		x.append(l)
 		y.append(density)
 	plt.plot(x,y,"ro-")

plt.xlabel('Length')
plt.ylabel('Density')
plt.yscale('log')
plt.title('Density')
#legend = ["Derivation density", "String density"]
#plt.legend(legend, loc='upper left')
plt.savefig('../figures/cnf_density_3.pdf')
