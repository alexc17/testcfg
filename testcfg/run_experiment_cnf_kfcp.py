## run experiment on which grammars are infinite
# generate grammar 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random

import generatecfg
import cfgfcp
import testfcp
print " running experiments on what grammars have the k fcp."


random.seed(8)
factory = generatecfg.CnfFactory()
factory.number_nonterminals = 10
factory.number_terminals =100
factory.number_binary_productions = 30
factory.number_lexical_productions = 50


#factory.no_lexical_ambiguity = True
number_grammars = 10
max_length = 20
nyields = 10


legend = []
for k in [1,2,3,4]:
	x = []
	y = []
	legend.append("$k="+ str(k)+ "$")
	print "Doing k-FCP k = ", k
	#for lprod in [50,100,150,200,250,300]:
	for lprod in [25, 50, 75,100]:#100,150,200,250,300]:
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
			answer = cfgfcp.test_strong_fcp_full(grammar, k)
			print "FCPK", answer
			if answer:
				fkpn += 1
		print "ratio = ", fkpn, "/", number_grammars
		ratio = fkpn / number_grammars
		y.append(ratio)

	print x
	print y

	

	plt.plot(x,y,"o-")

axes = plt.gca()
axes.set_ylim([0,1.1])
plt.legend(legend, loc='upper right')
plt.xlabel('$|P_L|$')
plt.ylabel('k-FCP')

#plt.legend(legend, loc='lower right')
plt.savefig('../figures/figure_cnf-kfcp.pdf')
