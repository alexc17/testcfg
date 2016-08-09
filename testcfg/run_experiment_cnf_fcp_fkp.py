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

print "Running experiment on CFGs with the FCP"
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

fcp_x = []
fcp_y = []

fkp_x = []
fkp_y = []

for sigma in [100,200]:
	fcp_x.append(sigma)
	fkp_x.append(sigma)

	for grammar  in xrange(number_grammars):
		fkpn = 0
		fcpn = 0
		factory.number_terminals = sigma
		grammar = factory.make_grammar()
		print grammar.language_infinite(), len(grammar.nonterminals)
		#print grammar
		#grammar.dump()
	# 	us = uniformsampler.UniformSampler(grammar,max_length)
	 	## now test if it has the fcp and fkp.
		answer = cfgfcp.test_one_fkp_exact(grammar, 10)
		print "FKP1", answer
		answer2 = cfgfcp.test_one_fcp_exact(grammar,20)
		print "FCP1", answer2
	