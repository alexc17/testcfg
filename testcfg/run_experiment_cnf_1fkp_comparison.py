# run experiment on fcp

import matplotlib.pyplot as plt
import random

import logging

#logging.basicConfig(level=logging.DEBUG)

import cfg
import earleyparser
import uniformsampler
import generatecfg

import cfgfcp

print "Running experiment on CFGs with the K FKP"
# no graph -- just test a single grammar.
 
random.seed(7)
factory = generatecfg.CnfFactory()
factory.number_nonterminals = 10
factory.number_terminals =100
factory.number_binary_productions = 30
factory.number_lexical_productions = 50


#factory.no_lexical_ambiguity = True
number_grammars = 100
max_length = 20
nyields = 10


legend = []
for k in [1]:
	x = []
	y = []
	xe = []
	ye = []
	
	print "Doing k-FKP k = ", k
	for lprod in [50,100,150,200,250,300]:
		#for lprod in [25, 50, 100,150,200,250,300]:
		print "lexical productions", lprod
		x.append(lprod)
		xe.append(lprod)
		factory.number_lexical_productions  = lprod
		fkpn = 0.0
		f1p = 0.0
		for grammar  in xrange(number_grammars):
			
			
			grammar = factory.make_grammar()
			print grammar.language_infinite(), len(grammar.nonterminals)
			#print grammar
			#grammar.dump()
		# 	us = uniformsampler.UniformSampler(grammar,max_length)
		 	## now test if it has the fcp and fkp.
			eanswer = cfgfcp.test_one_fkp_exact(grammar, 10)
			if eanswer:
				f1p += 1
			answer = cfgfcp.test_strong_fkp_full(grammar, k)
			print "FKPK", answer
			if answer:
				fkpn += 1
			if eanswer and not answer:
				grammar.dump()
				#raise ValueError()
		print "count k = ", fkpn
		print "count exact = ", f1p
		ratio = fkpn / number_grammars

		y.append(ratio)
		ye.append( f1p/ number_grammars)

	print x
	print y

	

	plt.plot(x,y, 'x-')
	legend.append("Inexact")
	plt.plot(xe,ye, 'o-')
	legend.append("Exact")
axes = plt.gca()
axes.set_ylim([0,1.1])
plt.legend(legend, loc='upper right')
plt.xlabel('$|P_L|$')
plt.ylabel('1-FKP')

#plt.legend(legend, loc='lower right')
plt.savefig('../figures/figure_cnf-1fkp_comparison.pdf')