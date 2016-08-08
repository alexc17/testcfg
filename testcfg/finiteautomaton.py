import pcfg
import cfg
import partitionfunction

class FiniteAutomaton:
	"""
	A finite automaton that we use to intersect with a PCFG or CFG for various purposes.
	"""

	def __init__(self):
		# a set of tuples that are (start, end, string)
		# states are integers?
		self.start = set()
		self.end = set()
		self.states = set()
		self.arcs = set()	
		self.initial = False
		self.final = False

	def addArc(self, i,j, string):
		self.arcs.add((i,j,string))
		self.states.add(i)
		self.states.add(j)

	def dump(self):
		print "start states ", self.start
		print "end states ", self.end
		for a in self.arcs:
			print a[0], "->", a[1], ": ", a[2]

	def getNonTerminal(self,i,j,s,map):
		"""
		i and j are states, and s is a terminal or nonterminal symbol in the grammar.

		 """
		x = (i,j,s)
		if x in map:
			return map[x]
		else:
			newnt = "NT" + str(len(map))
			map[x] = newnt
			return newnt

	def getNonTerminal2(self,i,j,s,map):
		"""
		i and j are states, and s is a terminal or nonterminal symbol in the grammar.

		 """
		x = (i,j,s)
		if x in map:
			return map[x]
		else:
			newnt = "N" + s + "_" + str(i) + "->" + str(j)
			while newnt in map:
				newnt = newnt + str(len(map))
			map[x] = newnt
			return newnt

	def createRhsList(self, rhs):
		"""
		Return a list of all possible ways of taking a sequence of states 
		through the rhs. This will be a list of lists of tuples.

		recursive method.
		"""
		answer = []
		if len(rhs) == 0:
			return []
		if len(rhs) == 1:
			# there are exactly n^2 ways
			for a in self.states:
				for b in self.states:
					answer.append([(a,b,rhs[0])])
		else:
			cdrlist = self.createRhsList(rhs[1:])
			first = rhs[0]
			for s in self.states:
				for cdr in cdrlist:
					s2 = cdr[0][0]
					newrhs = [ (s,s2,rhs[0])]
					newrhs.extend(cdr)
					answer.append(newrhs) 
		return answer


	def intersect_cfg_remove(self, grammar, nonterminal):
		"""
		Return a cfg and remove the states that will generate
		(nonterminal, self.initial, self.final)
		"""
		ntmap = dict()
		cfg = self.intersect_cfg(grammar,ntmap)
		special_nonterminal = self.getNonTerminal2(self.initial,self.final, nonterminal,ntmap)
		# now remove it from cfg.
		assert special_nonterminal in cfg.nonterminals
		cfg.nonterminals.remove(special_nonterminal)
		if special_nonterminal in cfg.start_set:
			cfg.start_set.remove(special_nonterminal)
		stripped_productions = set()
		for prod in cfg.productions:
			if not (prod[0] == special_nonterminal or special_nonterminal in prod[1]):
				stripped_productions.add(prod)
		cfg.productions = stripped_productions
		return cfg



	def intersect_cfg(self, grammar, ntmap=False):
		"""
		Return a new cfg.
		"""
		newgrammar = cfg.ContextFreeGrammar()
		productions = set()
		if not ntmap:
			ntmap = dict()
		for start_nt in grammar.start_set:
			newgrammar.nonterminals.add(start_nt)
		# unary rules from start symbol to start_state,end_state, start_symbol
		for start_state in self.start:
			for end_state in self.end:
				for start_nt in grammar.start_set:
					nt = self.getNonTerminal2(start_state,end_state,start_nt,ntmap)
					production = (start_nt,(nt,))
					productions.add(production)
		# lexical rules
		for arc in self.arcs:
			lhs = self.getNonTerminal2(arc[0],arc[1],arc[2],ntmap)
			production = (lhs, (arc[2],))
			productions.add(production)
		# regular productions
		for production in grammar.productions:
			lhs = production[0]
			rhs = production[1]
			l = len(rhs)
			if l == 0:
				# epsilon rule
				for i in self.states:
					nonterminal = self.getNonTerminal2(i,i,lhs,ntmap)
					newproduction = (nonterminal,())
					productions.add(newproduction)
			else:
				rhslist = self.createRhsList(rhs)
				#print "RHSLIST" , rhslist
				for newrhs in rhslist:
					firstState = newrhs[0][0]
					lastState = newrhs[-1][1]
					newlhs = self.getNonTerminal2(firstState,lastState,lhs,ntmap)
					#print "LHS", newlhs
					newrhs = tuple([ self.getNonTerminal2(tup[0],tup[1],tup[2],ntmap) for tup in newrhs ])
					newproduction = (newlhs,newrhs)
					productions.add(newproduction)
		newgrammar.productions = productions
		#print productions
		#print "Terminals are ", grammar.terminals
		newgrammar.terminals = set(grammar.terminals)

		for k in ntmap:
			#print k,ntmap[k]
			newgrammar.nonterminals.add(ntmap[k])
		newgrammar.start_set = set(grammar.start_set)
		return newgrammar

	def intersect_pcfg(self,grammar):
		"""
		return a new PCFG which is intersected with this regular language.
		
		Doesnt need to be binarised but long rhs will cause an exponential blow up in the size of the grammar.
		"""
		newgrammar = pcfg.Pcfg()
		ntmap = dict()
		# map from tuples (start,end,nt)
		# Now we need to compute the transitive closure of the 
		# epsilon transitions and a few other things.
		newproductions = []

		# unary rules from start symbol to start_state,end_state, start_symbol
		for start_state in self.start:
			for end_state in self.end:
				nt = self.getNonTerminal(start_state,end_state,grammar.start,ntmap)
				prod = pcfg.Production(grammar.start, [nt])
				prod.probability = 1.0
				newproductions.append(prod)

		# lexical rules
		for arc in self.arcs:
			lhs = self.getNonTerminal(arc[0],arc[1],arc[2],ntmap)
			production = pcfg.Production(lhs, [arc[2]])
			production.probability = 1.0
			newproductions.append(production)

		for production in grammar.productions:
			l = len(production.rhs)
			if l == 0:
				# epsilon rule
				for i in self.states:
					nonterminal = self.getNonTerminal(i,i,production.lhs,ntmap)
					newproduction = pcfg.Production(nonterminal,[])
					newproduction.probability = production.probability
					newproductions.append(newproduction)
			else:
				rhslist = self.createRhsList(production.rhs)
				#print rhslist
				for newrhs in rhslist:
					firstState = newrhs[0][0]
					lastState = newrhs[-1][1]
					lhs = self.getNonTerminal(firstState,lastState,production.lhs,ntmap)
					rhs = [ self.getNonTerminal(tup[0],tup[1],tup[2],ntmap) for tup in newrhs ]
					newproduction = pcfg.Production(lhs,rhs)
					newproduction.probability = production.probability
					newproductions.append(newproduction)
		# now we have a set of productions we create a new PCFG object.
		newgrammar.productions = newproductions
		newgrammar.terminals = set(grammar.terminals)
		for k in ntmap:
			#print k,ntmap[k]
			newgrammar.nonterminals.add(ntmap[k])
		newgrammar.start = grammar.start
		# construct but don't normalise.
		newgrammar.constructIndices(False)
		return newgrammar

#
# Factory methods
# to produce FAs that are useful for prefix, suffix etc,
#
#

def make_context(context, alphabet):
	"""
	Construct an automaton that recognizes u \Sigma^* v
	"""
	left = context[0]
	right = context[1]
	fa = FiniteAutomaton()
	current = 0
	fa.start.add(current)
	for s in left:
		fa.addArc(current, current+1,s)
		current += 1
	for s in alphabet:
		fa.addArc(current,current,s)
	for s in right:
		fa.addArc(current, current+1,s)
		current += 1
	fa.end.add(current)
	return fa


def make_context_long(context, alphabet):
	"""
	Construct an automaton that recognizes u \Sigma^+ v,
	and has special states for start and finish.
	For uv need a separet check.
	"""
	left = context[0]
	right = context[1]
	fa = FiniteAutomaton()
	current = 0
	fa.start.add(current)
	for s in left:
		fa.addArc(current, current+1,s)
		current += 1
	fa.initial = current
	middle = current+1
	fa.final = current+2
	current = current+2
	for s in right:
		fa.addArc(current, current+1,s)
		current += 1
	fa.end.add(current)

	for s in alphabet:
		fa.addArc(fa.initial,middle,s)
		fa.addArc(middle,middle,s)
		fa.addArc(middle,fa.final,s)
		fa.addArc(fa.initial,fa.final,s)

	return fa


def make_infix(stringlist,alphabet):
	"""
	Construct an automaton that recognizes \Sigma^* w \Sigma^*
	"""
	fa = FiniteAutomaton()
	current = 0
	fa.start.add(current)
	for s in stringlist:
		fa.addArc(current,current+1,s)
		current += 1
	fa.end.add(current)
	for s in alphabet:
		fa.addArc(0,0,s)
		fa.addArc(current,current,s)
	return fa

def make_infix_long(stringlist,alphabet):
	"""
	Construct an automaton that recognizes \Sigma^* w \Sigma^*
	and has a specific start and end state for begining and end of w.
	Returns the fa, and stores the specific start and end state in 
	self.initial and self.final.
	"""
	fa = FiniteAutomaton()
	

	current = 0
	fa.start.add(0)
	fa.start.add(1)
	current = 1
	for s in stringlist:
		fa.addArc(current,current+1,s)
		current += 1
	final = current+1
	fa.end.add(current)
	fa.end.add(final)
	for s in alphabet:
		fa.addArc(0,1,s)
		fa.addArc(0,0,s)
		fa.addArc(current,final,s)
		fa.addArc(final,final,s)
	fa.initial = 1
	fa.final = current
	return fa


# maybe add optional argument n to recognize
# \Sigma^n w \Sigma^*
def make_prefix(stringlist, alphabet):
	"""
	Construct an automaton that recognizes w \Sigma^*
	"""
	fa = FiniteAutomaton()
	current = 0
	fa.start.add(current)
	for s in stringlist:
		fa.addArc(current,current+1,s)
		current += 1
	fa.end.add(current)
	for s in alphabet:
		fa.addArc(current,current,s)
	return fa


def make_string(stringlist):
	"""
	Construct an automaton that recognizes w alone.
	"""
	fa = FiniteAutomaton()
	current = 0
	fa.start.add(current)
	for s in enumerate(stringlist):
		fa.addArc(current,current+1,s)
		current += 1
	fa.end.add(current)
	return fa


if __name__ == '__main__':
	print "Testing the intersection code crudely"
	grammar = pcfg.loadfromfile("crazy.pcfg")
	print "Loaded initial grammar"
	s = [ "jku" , "lan"]
	fa = make_infix(s, grammar.terminals)
	print "Constructed fa"
	#fa.dump()
	intersected_grammar = fa.intersect(grammar)
	print "intersected fa"
	#intersected_grammar.dump()
	print "trimming..."
	trimmed = intersected_grammar.trim()
	#trimmed.dump()
	print "trimmed"
	print "computing partition function..."
	x =	partitionfunction.computePartitionFunction(trimmed,100)
	print "Prefix probability is ", x
				







