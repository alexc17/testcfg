# Run KFCP experiments and save results to file.


import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random
import json
import argparse


import generatecfg
import cfgfcp
import testfcp

# Takes one filename as parameter
parser = argparse.ArgumentParser(description=
	"""
		Test K FCP property of a random grammar in CNF.
	""")

parser.add_argument("--grammars", default = 10, help="Number of grammars", type=int)

parser.add_argument("--nonterminals", help="Number of nonterminals including S", type = int, default = 10)
parser.add_argument("--terminals", default = 100, help="Number of terminals", type=int)
parser.add_argument("--seed", default = -1, help="Random seed", type=int)
parser.add_argument("--bproductions", default = 30, help="Total number of binary productions", type=int)
parser.add_argument("--lproductions", default = 50, help="Total number of lexical productions", type=int)
parser.add_argument("filename", help="Filename for result to be stored in")
args = parser.parse_args()


if args.seed > 0:
	random.seed(args.seed)


factory = generatecfg.CnfFactory()
factory.number_nonterminals = args.nonterminals
factory.number_terminals =args.terminals
factory.number_binary_productions = args.bproductions
factory.number_lexical_productions = args.lproductions


#factory.no_lexical_ambiguity = True
number_grammars = args.grammars
max_length = 20
nyields = 10


data = []
for k in [1,2,3,4]:
	x = []
	y = []
	for lprod in [50,100,150,200,250,300]:
	#for lprod in [25, 50, 75,100]:#100,150,200,250,300]:
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
			result = 0
			if answer:
				result =1

			# write result to file.
			data.append((k,lprod, result) )
			print k, lprod, result

data_file = open(args.filename,'w')
json.dump(data , data_file)
data_file.close()
