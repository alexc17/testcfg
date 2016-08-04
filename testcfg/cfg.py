# class for cfgs
# here we make no assumptions at all about the cfg
# 

# productions will be coded as a tuple (lhs,rhs) where rhs is a tuple
# nonterminals and terminals are strings.

import collections
import tarjan
import finiteautomaton


class ContextFreeGrammar:
	"""
	This class represents an arbitrary context-free grammar. 
	We assume that the set of nonterminals
	is disjoint from the set of nonterminals. 
	We allow multiple start symbols.

	"""
	def __init__(self):
		self.start_set = set()
		self.terminals = set()
		self.nonterminals = set()
		self.productions = set()


	def copy(self):
		"""
		returns a shallow copy. (which is the same as a deep copy because all of the elements are immutable.)
		"""
		mycopy = ContextFreeGrammar()
		mycopy.start_set = set(self.start_set)
		mycopy.terminals = set(self.terminals)
		mycopy.nonterminals = set(self.nonterminals)
		mycopy.productions = set(self.productions)
		return mycopy

	def all_terminals(rhs):
		for x in rhs:
			if not x in self.terminals:
				return False
		return True


	def is_empty(self):
		"""
		return true if this grammar is empty.
		"""
		return len(self.nonterminals) == 0

	def number_terminal_slots(self):
		n = 0
		for prod in self.productions:
			for sym in prod[1]:
				if sym in self.terminals:
					n += 1
		return n

	def compute_coreachable(self):
		"""
		return a set of all nonterminals that can generate a string.
		"""
		coreachable = set()
		iteration = 0
		done_this_loop = 0
		prodmap = collections.defaultdict(list)
		for prod in self.productions:
			prodmap[prod[0]].append(prod)
		remaining = set(self.nonterminals)
		while iteration == 0 or done_this_loop > 0:
			iteration += 1
			done_this_loop = 0
			for nt in remaining:
				## try some rules with this on the ljs
				ok = True
				
   				for prod in prodmap[nt]:
						# Is the rhs of this rule all coreachable \cup terminals
						for symbol in prod[1]:
							if (not symbol in self.terminals) and (not symbol in coreachable):
								# we can't use this rule
								break
						else:
							# This production is good so we break from the outer loop
							break
   				else:
   					ok = False
   				if ok:
   					done_this_loop += 1
   					coreachable.add(nt)
   			# now remove the ones we just did.
   			remaining2 = set()
   			for nt in remaining:
   				if not nt in coreachable:
   					remaining2.add(nt)
   			remaining = remaining2
	   	return coreachable
	
	def compute_nonnulling(self):
		"""
		return a set of all nonterminals that can generate a nonempty string.
		"""
		coreachable = self.compute_coreachable()
		# collect the  productions that all generate something.
		good_productions = set()
   		for prod in self.productions:
   			for symbol in prod[1]:
   				if not symbol in coreachable and not symbol in self.terminals:
   					break
   			else:
   				good_productions.add(prod)
		nonnulling = set()
		iteration = 0
		done_this_loop = 0
		while iteration == 0 or done_this_loop > 0:
			iteration += 1
			done_this_loop = 0
			for nt in coreachable:
				if not nt in nonnulling:
					## try some rules with this on the lhs
					ok = True
					
	   				for prod in good_productions:
	   					if prod[0] == nt:
	   						# Is the rhs of this rule all coreachable \cup terminals
	   						# with at least one nonnulling
	   						nonnulling_prod = False
	   						for symbol in prod[1]:
	   							if symbol in nonnulling or symbol in self.terminals:
	   								nonnulling_prod = True
	   								break
	   						if nonnulling_prod:
	   							# it doesn't only generate the empty string
	   							nonnulling.add(nt)
	   							done_this_loop += 1
	   							break
	   	return nonnulling	

	def _check_tuple(self,tup, symbol_set):
		for i in tup:
			if not i in symbol_set:
				return False
		return True

	def compute_nulling(self):
		"""
		return the set of all nonterminals that ONLY generate the emptystring.
		"""
		nn = self.compute_nonnulling()
		nulling = set()
		for x in self.compute_nullable():
			if not x in nn:
				nulling.add(x)
		return nulling

	def compute_nullable(self):
		"""
		return a set of all nonterminals that can generate the empty string.
		Not particularly smart algorithm.
		"""

		nullable = set()
		for prod in self.productions:
			if len(prod[1]) == 0:
				nullable.add(prod[0])
		if len(nullable) == 0:
			return nullable
		# otherwise we now need to do some work.
		newones = 1
		while newones > 0:
			newones = 0
			for prod in self.productions:
				if not prod[0] in nullable:
					# this might be nullable
					if self._check_tuple(prod[1],nullable):
						# then this is also nullable.
						nullable.add(prod[0])
						newones += 1
		return nullable


	def compute_trim_set(self):
		"""
		return the set of all nonterminals A that can both generate a string 
		and have a context.
		"""
		#print "computing coreachable"
		coreachable = self.compute_coreachable()
		#print "coreachable", coreachable
		trim = set()
		# good productions are those where the rhs are all generable.
		# this saves some time checking duff productions many times.
   		good_productions = set()
   		for prod in self.productions:
   			for symbol in prod[1]:
   				if not symbol in coreachable and not symbol in self.terminals:
   					break
   			else:
   				good_productions.add(prod)
   		#print "good_productions", len(good_productions)
   		for s in self.start_set:
			if s in coreachable:
				trim.add(s)
		done = len(trim)
		#print "start ", done
   		while done > 0:
   			done = 0
   			for prod in good_productions:
   				if prod[0] in trim:
   					for symbol in prod[1]:
   						if symbol in self.nonterminals and not symbol in trim:
   							done += 1
   							trim.add(symbol)
   		#print "Trim set", trim
   		return trim

   	def trim(self):
   		"""
   		Return a trimmed version of this grammar.
   		"""
   		#print "computing trim set, size ", len(self.nonterminals)
   		trim_set = self.compute_trim_set()
   		#print trim_set
   		result = ContextFreeGrammar()
   		for s in self.start_set:
   			if s in trim_set:
   				result.start_set.add(s)
   		result.nonterminals = trim_set
   		for prod in self.productions:
   			if prod[0] in trim_set:
   				for s in prod[1]:
   					if s in self.nonterminals and not s in trim_set:
   						break
   				else:
   					# this is ok
   					result.productions.add(prod)
   		for prod in result.productions:
   			for sym in prod[1]:
   				if not sym in self.nonterminals:
   					result.terminals.add(sym)
   		return result

	def is_trim(self):
		"""
		return true if this grammar is trim.
		"""
		trim = self.compute_trim_set()
		return len(trim) == len(self.nonterminals)

	def has_unary_loops(self):
		"""
		return true if this grammar has unary loops (also considering nullary rules.)
		This will lead to infinite ambiguity. 
		"""
		return _test_cyclic(self.compute_unary_rules())


	def all_nonterminals_depth1(self):
		"""
		return true if all nonterminals A have a production A -> w.
		"""
		for s in self.nonterminals:
			if not self.nonterminal_depth1(s):
				return False
		return True

	def nonterminal_depth1(self, nt):
		"""
		return true if we have a production A -> w.
		"""	
		for prod in self.productions:
			if prod[0] == nt:
				for r in prod[1]:
					if not r in self.terminals:
						break
				else:
					return prod[1]
		return False
	
	def is_terminal_production(self, production):
		for r in production[1]:
			if not r in self.terminals:
				return False
		return True

	def compute_unary_rules(self):
		"""
		return a set of pairs (A,B) where A =>^* B
		"""
		unary_rules = set()
		nullable = self.compute_nullable()
		for prod in self.productions:
			l = prod[0]
			for r in self._possible_unary(prod, nullable):
				unary_rules.add((l,r))
		return unary_rules


	def _possible_unary(self, production, nullary_nts):
		"""
		Return a list of all nonterminals on the right hand side 
		which could be unary productions. (i.e. such that all the other nonterminals are nullary).
		Fiddly.
		"""
		rhs = production[1]
		if len(rhs) == 0:
			return []
		for s in rhs:
			if s in self.terminals:
				return []
		# ok so no 
		if len(rhs) == 1:
			return list(rhs)
		## so at least two
		non_nullary = False
		for s in rhs:
			if not s in nullary_nts:
				if non_nullary:
					# we have two non nulling.
					return []
				else:
					non_nullary = s
		if non_nullary:
			# we have exactly one non-null
			return [ non_nullary ]
		else:
			# all non nullary
			return list(set(rhs))

	def language_infinite(self):
		"""
		return true if this grammars defines an infinite language.
		
		This is a little more complicated that one would think.
		We normalise it first, by trimming, removing nulling nonterminals and any unary cycles.
		Then it is quite easy.
		"""
		grammar = self.normalise()
		edges = set()
		for prod in grammar.productions:
			a = prod[0]
			for b in prod[1]:
				if a == b:
					return True
				edges.add((a,b))
		#print(edges)
		components = _tarjan(edges)
		for scc in components:
			if len(scc) > 1:
				return True
		return False

	def normalise(self):
		"""
		This trims, removes all nulling nonterminals,
		merges all unary cycles, and returns the resulting grammar.
		"""
		return self.trim().remove_nulling().merge_unary()


	def generate_string(self):
		"""
		If the grammar is not empty then generate some reasonably short string.
		Grammar must be trim first.
		"""
		if len(self.nonterminals) == 0:
			return False
		ntmap = {}
		for p in self.productions:
			if self.is_terminal_production(p):
				ntmap[p[0]] = p[1]
		start = list(self.start_set)[0]
		while not start in ntmap:
			for lhs,rhs in self.productions:
				if not lhs in ntmap:
					result = []
					for rhss in rhs:
						if rhss in ntmap:
							result.extend(ntmap[rhss])
						elif rhss in self.terminals:
							result.append(rhss)
						else:
							break
					else:
						ntmap[lhs] = result
		return ntmap[start]



	def remove_nulling(self):
		"""
		removes nonterminals that only generate the empty string.

		Remove them from the rhs of every rule.
		And remove them from the grammar 
		(unless they are start symbols.)
		"""
		nulling = self.compute_nulling()
		if len(nulling) == 0:
			return self
		grammar = ContextFreeGrammar()
		grammar.terminals = set(self.terminals)
		for prod in productions:
			rhs = []
			for s in prod[1]:
				if not s in nulling:
					rhs.append(s)
			grammar.productions.add((prod[0], tuple(rhs)))
		for s in self.nonterminals:
			if s in self.start_set or not s in nulling:
				grammar.nonterminals.add(s)
		grammar.start_set = set(self.start_set)
		return grammar

	def topological_sort(self):
		"""
		return the nonterminals in order so that if there is a derivation A =>* B
		then A occurs after B. 
		Returns a list of the strongly connected components.

		If there is a loop then we get a component that has more than one element.
		"""
		components =  _tarjan(self.compute_unary_rules())
		done = set()
		for scc in components:
			for s in scc:
				done.add(s)
		for x in self.nonterminals:
			if not x in done:
				components.append((x,))
		return components

	def merge_unary(self):
		"""
		Merge all nonterminals such that A =>* B and B =>* A.
		Take account of nullary rules. Use Tarjan's algorithm.
		Return the smaller grammar.
		"""
		ur = self.compute_unary_rules()
		components = _tarjan(ur)
		merge_map = {}
		for x in components:
			for y in x:
				merge_map[y] = x[0]
		for x in self.nonterminals:
			if not x in merge_map:
				merge_map[x] = x
		for x in self.terminals:
			merge_map[x] = x		
		## now apply merge.
		grammar = ContextFreeGrammar()
		for prod in self.productions:
			newrhs = tuple([ merge_map[x] for x in prod[1] ])
			newlhs = merge_map[prod[0]]
			# now check that this is not just A -> A
			if newrhs != (newlhs,):
				grammar.nonterminals.add(newlhs)
				grammar.productions.add((newlhs,newrhs))
		for s in self.start_set:
			grammar.start_set.add(merge_map[s])
		grammar.terminals = set(self.terminals)
		return grammar



	def count_productions_lhs(self, nonterminal):
		"""
		How many productions does this nonterminal appear on the left hand side of?
		"""
		n = 0
		for prod in self.productions:
			if prod[0] == nonterminal:
				n += 1
		return n

	def count_productions_rhs(self, nonterminal):
		"""
		How many productions does this nonterminal appear on the right hand side of?
		"""
		n = 0
		for prod in self.productions:
			for nt in prod[1]:
				if nt == nonterminal:
					n += 1
		return n

	




	## Methods for intersectin grammar with regular language.

	def prefix_grammar(self, prefix):
		"""
		return a grammar that generates L(G) \cap w\Sigma^*.
		"""
		fa = finiteautomaton.make_prefix(prefix, self.terminals)
		intersected_grammar = fa.intersect_cfg(self)
		grammar = intersected_grammar.trim()
		return grammar

	def infix_grammar(self, infix):
		"""
		return a grammar that generates L(G) \cap \Sigma^* w \Sigma^*.
		"""
		fa = finiteautomaton.make_infix(infix, self.terminals)
		intersected_grammar = fa.intersect_cfg(self)
		#print "Trimming"
		grammar = intersected_grammar.trim()
		return grammar

	def infix_grammar_without_nt(self, infix, nonterminal):
		"""
		return a grammar that generates L(G) \cap \Sigma^* w \Sigma^*,
		except those where nonterminal =>^* w.

		The grammar may of course be empty.
		More precisely, it generates all derivations that have at least one w that is not generated by
		N. This is useful for testing the FKP, where we want to sample from contexts that are not contexts
		of the given nonterminal.
		"""
		fa = finiteautomaton.make_infix_long(infix, self.terminals)
		intersected_grammar = fa.intersect_cfg_remove(self, nonterminal)
		#print "Trimming"
		grammar = intersected_grammar.trim()
		return grammar

	def single_occurrence_grammar(self, symbol):
		"""
		return a grammar that generatse L(G) \cap (\Sigma-a)^* a (\Sigma-a)^*.
		"""
		vocab = set(self.terminals)
		vocab.remove(symbol)
		#print "Symbol is" , symbol
		fa = finiteautomaton.make_infix((symbol,), vocab)
		#fa.dump()
		intersected_grammar = fa.intersect_cfg(self)
		#intersected_grammar.dump()
		grammar = intersected_grammar.trim()
		return grammar

	def context_grammar(self, context):
		"""
		return a grammar that generates L(G) \cap l\Sigma^* r.
		"""
		fa = finiteautomaton.make_context(context, self.terminals)
		intersected_grammar = fa.intersect_cfg(self)
		grammar = intersected_grammar.trim()
		return grammar

	def context_grammar_without_nt(self, context, nonterminal):
		"""
		return a grammar that generates L(G) \cap l\Sigma^* r,
		but where the string l cannot be generated by the given nonterminal.
		"""
		fa = finiteautomaton.make_context_long(context, self.terminals)
		intersected_grammar = fa.intersect_cfg_remove(self, nonterminal)
		grammar = intersected_grammar.trim()
		return grammar


	def store(self,filename):
		fhandle = open(filename,'w')
		fhandle.write("# CFG \n")
		prods = list(self.productions)
		prods.sort()
		for prod in prods:
			fhandle.write(prod[0] + " -> " + " ".join(prod[1]) + "\n")
		fhandle.close()

	def binarised_productions(self):
		result = []
		for prod in productions:
			for bprod in binarise_production(prod):
				result.append(bprod)
		return result

	def dump(self):
		print "CFG dump"
		print "nonterminals", self.nonterminals
		print "terminals", self.terminals
		prods = list(self.productions)
		prods.sort()
		for prod in prods:
			print(prod[0] + " -> " + " ".join(prod[1]))


def binarise_production(prod):
	"""
	return a list of productions of length 1 if the rhs is less than 3.
	If the right hand side has length L > 2 then there will be L - 2 productions. 
	This will be in reverse order.
	"""
	rhs = prod[1]
	lhs = prod[0]
	l = len(rhs)
	if l < 3:
		return [prod]
	## at least 3
	result = []
	currentSymbol = (prod, l-3)
	finalprod = (currentSymbol, rhs[-2:])
	result.append(finalprod)
	for i in range(l-3):
		# number of steps.
		next = (prod, i + l-2 )
		newprod = (next, (rhs[-(3+i)]  , currentSymbol))
		result.append(newprod)
		currentSymbol = next
	firstproduction = (lhs, (rhs[0], currentSymbol))
	result.append(firstproduction)
	return result


	

def load_from_file(filename):
	"""
	factory method that returns a cfg object from a filename.
	this method assumes that the start symbols are S
	or S_something. 
	and that the nonterminals are those symbols that occur on the lhs of a rule.

	Format is X -> Y Z
	Lines that start with # are comments.
	"""
	fhandle = open(filename)
	productions = set()
	nonterminals = set()
	all_symbols = set()
	
	for line in fhandle:
		if len(line) > 0 and line[0] != "#":
			tokens = line.strip().split()
			l = len(tokens)
			if l == 0:
				# whitespace line
				continue
			if l == 1:
				# this is a recoverable syntax error
				raise ValueError("Only one token on line")
			if l > 1 and tokens[1] != "->":
				# another error 
				raise ValueError("wrong separator: should be ->")
			lhs = tokens[0]
			rhs = tuple(tokens[2:])
			prod = (lhs, rhs)
			nonterminals.add(lhs)
			productions.add(prod)
			for s in rhs:
				if s[0].isupper():
					nonterminals.add(s)
				all_symbols.add(s)
			all_symbols.add(lhs)
	fhandle.close()
	# Now we construct the set of terminals
	terminals = set()
	start = set()
	for s in all_symbols:
		if s in nonterminals:
			if s == "S" or s.startswith("S_"):
				start.add(s)
		else:
			terminals.add(s)
	grammar = ContextFreeGrammar()
	grammar.terminals = terminals
	grammar.nonterminals = nonterminals
	grammar.start_set = start
	grammar.productions = productions
	return grammar

def convert_from_pcfg(pcfg_grammar):
	"""
	Take a pcfg and convert it.
	"""
	grammar = ContextFreeGrammar()
	grammar.terminals = set(pcfg_grammar.terminals)
	grammar.nonterminals = set(pcfg_grammar.nonterminals)
	grammar.productions = set()
	for prod in pcfg_grammar.productions:
		grammar.productions.add((prod.lhs,tuple(prod.rhs)))
	grammar.start_set.add(pcfg_grammar.start)
	return grammar


def _tarjan(edges):
	"""
	For some reason we need a map and not a defaultdict(list)
	"""
	graph = {}
	for (a,b) in edges:
		if a in graph:
			graph[a].append(b)
		else:
			graph[a] = [b]
	#print "Graph is ", graph
	components = tarjan.strongly_connected_components(graph)
	return components


def _test_cyclic(edges):
	""" 
	return False if no cycle or a node that has a cycle.
	Use naive algorithm.

	"""
	if len(edges) == 0:
		return False
	# convert to 
	alist = collections.defaultdict(list)
	nodes = set()
	# map from each node to the set of nodes that can be construcetd from it.
	for (a,b) in edges:
		alist[a].append(b)
		nodes.add(a)
	for node in nodes:
		rr = set()
		_dfs(alist,node,rr)
		if node in rr:
			return [node]
	return False

def _dfs(alist, nt, result):
	"""
	find all nts reachable from nt using DFS.
	"""
	for next in alist[nt]:
		if not next in result:
			result.add(next)
			_dfs(alist, next, result)


