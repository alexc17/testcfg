# run experiment on fcp

import matplotlib.pyplot as plt
import random


import cfg
import earleyparser
import uniformsampler
import generatecfg
print "Running experiment on density of CFGs."
 
#random.seed(7)
factory = generatecfg.CnfFactory()
factory.number_nonterminals = 10
factory.number_terminals = 100
factory.number_binary_productions = 30
factory.number_lexical_productions = 10
#factory.unique_lexicon = True

number_grammars = 10
max_length = 50
#samples_per_length = 10
for g in xrange(number_grammars):
	print "Grammar ", g
	x = []
	y = []
	grammar = factory.make_grammar()
	if len(grammar.terminals) > 0:
	 	us = uniformsampler.UniformSampler(grammar,max_length)
	 	for l in xrange(1,max_length +1):
	 		density = us.density(l)
	 		x.append(l)
	 		y.append(density)
	 	plt.plot(x,y)

plt.xlabel('Length')
plt.ylabel('Density')
plt.yscale('log')
plt.title('Derivation Density')
plt.savefig('../figures/cnf_density_1.pdf')
