# Generate a random pcfg file.
# Use nonterminals S, NT0, \dots
# and lowercase terminals.

import dictionary
import random
import numpy as np
import sys
import argparse
import cfg

class CfgStore:
	"""
	Class for storing a collection of randomly generated CFGs.

	We generate a large number of CFGs and store them by number of nonterminals.
	"""
	
	def __init__(self, factory, ngrammars, minnt, maxnt):
		self.factory = factory
		self.max = maxnt
		self.min = minnt
		self.cfg_lists = [ [] ] 
		for i in xrange(self.maxnt + 1):
			self.cfg_lists.append([])
		try:
			for i in reversed(xrange(minnt, maxnt + 1)):
				print "Trying to make grammars with", i
				factory.number_nonterminals = i
				for g in xrange(ngrammars):				
					grammar = factory.make_grammar()
					n = len(grammar.nonterminals)
					self.cfg_lists[n].append(grammar)
		except ValueError:
			print "Bailed out"
		factory.number_nonterminals = self.max
		for i in xrange(self.max + 1):
			print i, len(self.cfg_lists[i])

class CnfFactory:
	"""
	Class for generating CFGs in CNF.

	Very naive. No attempt to make them reasonable.
	"""
	def __init__(self):
		self.number_nonterminals = 1
		self.number_terminals = 2
		self.number_binary_productions = 1
		self.number_lexical_productions = 1
		self.nonterminals = []
		self.terminals = []
		# unique lexicon gives each nonterminal a single distinct terminal
		self.unique_lexicon = False



	def make_uprod(self):
		rhs = random.choice(self.terminals)
		lhs = random.choice(self.nonterminals)
		return (lhs,(rhs,))

	def make_bprod(self):
		rhs1 = random.choice(self.nonterminals)
		rhs2 = random.choice(self.nonterminals)
		lhs = random.choice(self.nonterminals)
		return (lhs,(rhs1,rhs2))

	def make_grammar(self):
		"""
		return a new grammar. that is trim.
		"""
		self.terminals = list(dictionary.generateDictionary(self.number_terminals))
		self.nonterminals = [ "S" ]
		for j in xrange(self.number_nonterminals - 1):
			nt = "NT" + str(j)
			self.nonterminals.append(nt)
		bprods = set()
		if self.number_binary_productions > (self.number_nonterminals ** 3) * 0.9:
			raise ValueError()
		if self.number_lexical_productions > (self.number_nonterminals * self.number_terminals) * 0.9:
			raise ValueError()
			
		while len(bprods) < self.number_binary_productions:
			bprods.add(self.make_bprod())
		uprods = set()
		if self.unique_lexicon:
			if len(self.terminals) < len(self.nonterminals):
				raise ValueError()
			i = 0
			for nt in self.nonterminals:
				terminal = self.terminals[i]
				i += 1
				uprods.add((nt,(terminal,)))
		else:
			while len(uprods) < self.number_lexical_productions:
				uprods.add(self.make_uprod())

		## now return the grammar.
		for p in uprods:
			bprods.add(p)
		grammar = cfg.ContextFreeGrammar()
		grammar.terminals = set(self.terminals)
		grammar.nonterminals = set(self.nonterminals)
		grammar.productions = bprods
		grammar.start_set = set(["S"])
		return grammar.trim()


class CfgFactory:
	"""
	Class for generating CFGs.
	"""
	def __init__(self):
		self.number_nonterminals = 1
		self.number_terminals = 2
		self.number_productions = 1
		self.number_preterminal_productions = 0
		self.min_rhs_length = 1
		self.max_rhs_length = 2
		self.start_symbols = 1
		self.no_unary_nt = True
		# minumum number of times a nonterminal can appear on the lhs of a rule

		self.min_nt_lhs = 1
		# minimum number of times a nonterminal can appear on the rhs of a rule
		self.min_nt_rhs = 1
		self.no_lexical_ambiguity = False
		# used for the no lexical ambiguity mode.
		self.terminal_counter = 0
		self.terminalprob = 0.5
		

		self.terminals = []
		self.nonterminals = []
		self.productions = set()
		self.start_set = set()

	def construct_terminals(self):
		if self.no_lexical_ambiguity:
			self.number_terminals = self.number_productions * self.max_rhs_length
			self.terminal_counter = 0
		self.terminals = list(dictionary.generateDictionary(self.number_terminals))
		assert len(self.terminals) == self.number_terminals

	def construct_nonterminals(self):
		if self.start_symbols == 1:
			self.start_set.add("S")
			self.nonterminals.append("S")
		else:
			for i in range(self.start_symbols):
				s = "S_" + str(i)
				self.start_set.add(s)
				self.nonterminals.append(s)	
		for j in range(self.number_nonterminals - self.start_symbols):
			nt = "NT" + str(j)
			self.nonterminals.append(nt)	


	def make_productions_preterminals(self):
		"""
		In the case where we want separate nonterminal and terminal rules.
		"""
		# first we add a bunch of preterminals.
		preterminal_productions = set()
		for i in self.terminals:
			rhs = (i,)
			lhs = random.choice(self.nonterminals)
			preterminal_productions.add((lhs,rhs))
		while len(preterminal_productions) < self.number_preterminal_productions:
			lhs = random.choice(self.nonterminals)
			rhs = (random.choice(self.terminals),)
			preterminal_productions.add((lhs,rhs))
		return preterminal_productions

	def make_productions3(self):
		"""
		In the case where we want separate nonterminal and terminal rules.
		"""
		self.make_productions2()
		for prod in self.make_productions_preterminals():
			self.productions.add(prod)


	def make_productions2(self):
		lhscounter = {}
		rhscounter = {}
		for nt in self.nonterminals:
			lhscounter[nt] = self.min_nt_lhs
			rhscounter[nt] = self.min_nt_rhs
		# if we don't have any 
		if (not self.no_lexical_ambiguity) and self.number_preterminal_productions == 0:
			for term in self.terminals:
				rhscounter[term] = 1
		self.productions = set()
		while len(self.productions) < self.number_productions:
			if len(lhscounter) > 0:
				lhs, n = lhscounter.popitem()
				lhscounter[lhs] = n
				production = self.make_production_lhs(lhs)
			elif len(rhscounter) > 0:
				rhs, n = rhscounter.popitem()
				rhscounter[rhs] = n
				production = self.make_production_rhs(rhs)
			else:
				production = self.make_production()
			self.add_production(production,lhscounter,rhscounter)
		if not (len(lhscounter) == 0 and len(rhscounter) == 0):
			print "lhscounter", lhscounter, "rhscounter", rhscounter
			raise ValueError()

	def add_production(self, production, nonterminalLhsCounter, nonterminalRhsCounter):
		c = 0
		if not production in self.productions:
			lhs,rhs = production
			if lhs in nonterminalLhsCounter:
				c += 1
				n = nonterminalLhsCounter[lhs]
				if n > 1:
					nonterminalLhsCounter[lhs] = n -1
				else:
					del nonterminalLhsCounter[lhs]
			
			for r in rhs:
				if r in nonterminalRhsCounter:
					c += 1
					n = nonterminalRhsCounter[r]
					if n > 1:
						nonterminalRhsCounter[r] = n -1
					else:
						del nonterminalRhsCounter[r]
			self.productions.add(production)
		return c

	def pick_terminal(self):
		if self.no_lexical_ambiguity:
			# we create a new fresh terminal symbol every time we want one.
			answer = self.terminals[self.terminal_counter]
			self.terminal_counter += 1
			return answer
		else:
			return random.choice(self.terminals)

	def make_production(self):
		lhs = random.choice(self.nonterminals)
		return self.make_production_lhs(lhs)



	def make_production_lhs(self,lhs):
		l = self.pick_rhs_length()
		if l == 1 and self.no_unary_nt:
			rhs = [self.pick_terminal()]
		else:
			rhs = []
			for i in xrange(l):
				rhs.append(self.pick_rhs_element())
		return (lhs, tuple(rhs))

	def make_production_rhs(self, r):
		# make a production with this r symbol on the rhs.
		l = self.pick_rhs_length()
		if self.no_unary_nt and r in self.nonterminals:
			while l == 1:
				l = self.pick_rhs_length()
		lhs = random.choice(self.nonterminals)
		position = random.randrange(l)
		rhs = []
		for i in xrange(l):
			if i == position:
				rhs.append(r)
			else:
				rhs.append(self.pick_rhs_element())
		return (lhs, tuple(rhs))

	def pick_rhs_element(self):
		"""
		If we are in preterminal mode then we pick a nonterminal.
		Otherwise pick randomly
		"""
		if self.number_preterminal_productions > 0:
			return random.choice(self.nonterminals)
		if random.random() < self.terminalprob:
			return self.pick_terminal()
		else:
			return random.choice(self.nonterminals)

	def pick_rhs_length(self):
		return random.randrange(self.min_rhs_length,self.max_rhs_length+1)

	def _return_grammar(self):
		grammar = cfg.ContextFreeGrammar()
		grammar.terminals = set(self.terminals)
		grammar.nonterminals = set(self.nonterminals)
		grammar.productions = set(self.productions)
		grammar.start_set = set(self.start_set)
		return grammar.trim()

	def make_grammar(self):
		"""
		This returns a trim grammar with at most these numbers of terminals and nonterminals etc.
		"""
		self.construct_terminals()
		self.construct_nonterminals()
		if self.number_preterminal_productions == 0:
			self.make_productions2()
		else:
			self.make_productions3()
		return self._return_grammar()

def generate_cfg(numStart, numNonterminals, numTerminals, numProductions, min_length, max_length, onlyunaryterminal,terminalprob, minrhs):
	"""
	This will return a new trim CFG, with at most numNonterminals, numTerminals etc.
	It may have less as the trimming process may remove some.
	If numTerminals is -1, then we make sure we have a new one for each occurrence.

	
	"""
	grammar = cfg.ContextFreeGrammar()
	if numTerminals == -1:
		terminals = list(dictionary.generateDictionary(numProductions * max_length))
	else:
		terminals = list(dictionary.generateDictionary(numTerminals))
	nonterminals = [ ]
	terminalCounter = 0
	start = [ ]
	if numStart == 1:
		start.append("S")
	else:
		for i in xrange(numStart):
			start.append("S_" + str(i))
	for s in start:
		nonterminals.append(s)
	vcup = [ ]
	for terminal in terminals:
		vcup.append(terminal)
	for i in range(numNonterminals - numStart):
		nt = "NT" + str(i)
		nonterminals.append(nt)
		vcup.append(nt)
	productionSet = set()
	obligatoryrhs = []
	for x in xrange(minrhs):
		for nt in nonterminals:
			obligatoryrhs.append(nt)
	while len(productionSet) < numProductions:	
		if len(productionSet) < len(obligatoryrhs):
			lhs = obligatoryrhs[len(productionSet)]
		else:
			lhs = random.choice(nonterminals)
		rhs = []
		rhslength = random.randrange(min_length,max_length+1)
		#print rhslength
		if rhslength == 1 and onlyunaryterminal:			
			if numTerminals == -1:
				rhs.append(terminals[terminalCounter])
				terminalCounter += 1
			else:
				rhs.append(random.choice(terminals))
		else:
			for i in range(rhslength):
				if random.random() < terminalprob:
					if numTerminals == -1:
						rhs.append(terminals[terminalCounter])
						terminalCounter += 1
					else:
						rhs.append(random.choice(terminals))
				else:
					rhs.append(random.choice(nonterminals))
		prod = (lhs,tuple(rhs))
		if not prod in productionSet:
			productionSet.add(prod)
			#print prod
	for nt in nonterminals:
		n = 0
		for lhs,rhs in productionSet:
			for sym in rhs:
				if sym == nt:
					break
		else:
			# not on the rhs of any nonterminal.
			while True:
				lhs = random.choice(nonterminals)
				if lhs != nt:
					rhslength = random.randrange(min_length,max_length+1)
					if rhslength == 1 and not onlyunaryterminal:
						productionSet.add((lhs,(nt,)))
						break
					elif rhslength > 1:
						position = random.choice(range(rhslength))
						rhs = []
						for i in range(rhslength):
							if i == position:
								rhs.append(nt)
							else:
								if random.random() < terminalprob:
									if numTerminals == -1:
										rhs.append(terminals[terminalCounter])
										terminalCounter += 1
									else:
										rhs.append(random.choice(terminals))
								else:
									rhs.append(random.choice(nonterminals))
						productionSet.add((lhs,tuple(rhs)))

	# now we have the set of weighted productions.
	grammar.productions = productionSet
	grammar.nonterminals = nonterminals
	grammar.terminals = terminals
	grammar.start_set = start
	return grammar.trim()


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description=
		"""
			Generate a random CFG.

			This will be trim.
			Rhs lengths are  uniformly distributed.
			Option to exclude unary rules between nonterminals.
		""")
	parser.add_argument("--numstart", help="Number of start symbols", type = int, default = 1)
	parser.add_argument("--nonterminals", help="Number of nonterminals including start", type = int, default = 1)
	parser.add_argument("--terminalprob", help="Probability that a symbol on the rhs will be a terminal", type=float,default=0.5)
	parser.add_argument("--terminals", default = 2, help="Number of terminals", type=int)
	parser.add_argument("--productions", default = 2, help="Total number of productions", type=int)
	parser.add_argument("--preterminals", default = 0, help="If this (the number of preterminal productions) is greater than 0, then we introduce all terminals with a preterminal.", type=int)
	
	parser.add_argument("--minrhslength", type=int, default = 1, help = "Minimum length of the rhs of a production.")
	parser.add_argument("--maxrhslength", type=int, default = 2, help = "Maximum length of the rhs of a production.")
	parser.add_argument("--unaryrules", action="store_true", default=False, help="If set then unary rules will have terminals on the right hand side. ")
	parser.add_argument("--no_lexical_ambiguity", action="store_true", default=False, help="If set then all terminals are different.")
	parser.add_argument("--minntrhs", type=int, default = 0, help = "Minimum number of productions that each nonterminal appears on rhs of.")
	parser.add_argument("--minntlhs", type=int, default = 0, help = "Minimum number of productions that each nonterminal appears on lhs of.")
	
	parser.add_argument("filename", help="Filename for result to be stored in")
	args = parser.parse_args()
	factory = CfgFactory()
	factory.number_terminals = args.terminals
	factory.number_nonterminals = args.nonterminals
	factory.start_symbols = args.numstart
	factory.number_preterminal_productions = args.preterminals
	factory.number_productions = args.productions 
	factory.terminalprob = args.terminalprob
	factory.min_rhs_length = args.minrhslength
	factory.max_rhs_length = args.maxrhslength
	factory.no_lexical_ambiguity = args.no_lexical_ambiguity
	grammar = factory.make_grammar()
	grammar.store(args.filename)
	
