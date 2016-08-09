# run experiment on fcp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random

import logging

#logging.basicConfig(level=logging.DEBUG)

import cfg
import earleyparser
import uniformsampler
import generatecfg

import cfgfcp

print "Running experiment on CFGs with the 1 FKP"
# no graph -- just test a single grammar.
 
random.seed(8)
factory = generatecfg.CnfFactory()
factory.number_nonterminals = 10
factory.number_terminals =100
factory.number_binary_productions = 30
factory.number_lexical_productions = 50


#factory.no_lexical_ambiguity = True
number_grammars = 100
max_length = 20
nyields = 10
x = []
y = []


for lprod in xrange(25,301,25):
	#for lprod in [25, 50, 100,150,200,250,300]:
	print "lexical productions", lprod
	x.append(lprod)
	factory.number_lexical_productions  = lprod
	fkpn = 0.0
	for grammar  in xrange(number_grammars):
		
		
		grammar = factory.make_grammar()
		print grammar.language_infinite(), len(grammar.nonterminals)
		#print grammar
		#grammar.dump()
	# 	us = uniformsampler.UniformSampler(grammar,max_length)
	 	## now test if it has the fcp and fkp.
		answer = cfgfcp.test_one_fkp_exact(grammar, 10)
		print "FKP1", answer
		if answer:
			fkpn += 1
	print "ratio = ", fkpn
	ratio = fkpn / number_grammars
	y.append(ratio)

print x
print y

axes = plt.gca()
axes.set_ylim([0,1])

plt.plot(x,y,'o-')

plt.xlabel('$|P_L|$')
plt.ylabel('1-FKP')

#plt.legend(legend, loc='lower right')
plt.savefig('../figures/figure_cnf-1fkp.pdf')