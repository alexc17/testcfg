import collections
import logging
import argparse
import time


import cfg
import forest


time_parser = False


# item format = 
# (lhs, rhs, position, start, end)
def production(item):
	return (item[0],item[1])

def next_category(item):
	return item[1][item[2]]

def span(item):
	return (item[3],item[4])





def is_complete(item):
	return (item[2] == len(item[1]))

def to_string(item):
	answer = str(span(item)) + ":" + item[0] + " ->"
	pos = item[2]
	answer += " ".join(item[1][:pos])
	answer += "*"
	answer += " ".join(item[1][pos:])

	return answer



class EarleyParser:
	"""
	Implementation of Earley style parser for arbitrary CFGs.
	Incremental, left to right.
	Items are coded as (lhs,rhs, rhsposition, start,end) tuples.
	"""

	def __init__(self, grammar):
		if grammar == None:
			raise ValueError("can't parse without a grammar.")
		self.grammar = grammar
		# other initialisations here,
		# including any necessary precomputations on the grammar.
		self.nullable = grammar.compute_nullable()
		self.chart = []
		self.chart_set = []
		# map from items to previous states
		self.previous_states = collections.defaultdict(list)
		self.reduced_states = collections.defaultdict(list)




	def _init_chart(self, length):
		self.chart = []
		self.chart_set = []
		self.length = length
		self.previous_states = collections.defaultdict(list)
		self.reduced_states = collections.defaultdict(list)
		for i in range(length+1):
			self.chart_set.append(set())
			self.chart.append(collections.deque())

	def _initialise_state_sets(self,length):
		self._init_chart(length)
		for prod in self.grammar.productions:
			if prod[0] in self.grammar.start_set:
				self.enqueue((prod[0],prod[1],0,0,0))

	def _initialise_state_sets_nt(self,length, nonterminal):
		self._init_chart(length)
		for prod in self.grammar.productions:
			if prod[0] == nonterminal:
				self.enqueue((prod[0],prod[1],0,0,0))


	def parse_nonterminal_context(self, left, nonterminal, right):
		"""
		Return true if a start symbol parses lAr.
		"""
		input_tuple = left + (nonterminal,) + right
		self.input = input_tuple
		length = len(input_tuple)
		logging.info("Parse nonterminal context %d ", str(length))
		self._initialise_state_sets(length)
		# now add the 
		#item = (nonterminal, (), 0, len(left), len(left)+ 1)
		#self.add_to_chart(item)
		self.process()
		for x in self.chart[length]:
			logging.info("Checking %s", to_string(x))
			if is_complete(x) and x[3] == 0 and x[0] in self.grammar.start_set:
				return True
		logging.info("No parse found.")
		return False



	def parse_start(self, input_tuple, nonterminal):
		"""
		Parse this using the given nonterminal as a start symbol.
		"""
		self._initialise_state_sets_nt(len(input_tuple),nonterminal)
		self.input = input_tuple
		self.process()
		for x in self.chart[len(input_tuple)]:
			logging.info("Checking %s", to_string(x))
			if is_complete(x) and x[3] == 0 and x[0] == nonterminal:
				return True
		return False

	def parse(self, input_tuple):
		"""
		Takes as input a tuple and parses it.
		Returns True or False

		"""
		t0 = time.time()
		self._initialise_state_sets(len(input_tuple))
		self.input = input_tuple
		self.process()
		t1 = time.time()
		logging.info("Finished parsing")
		if time_parser:
			logging.warning("Parse: l = %d, t = %f" % (len(input_tuple), t1-t0))
		for x in self.chart[len(input_tuple)]:
			logging.info("Checking for complete %s", to_string(x))
			if is_complete(x) and x[3] == 0 and x[0] in self.grammar.start_set:
				return True
		return False	


	def count_parses(self, input_tuple):
		print "parse started"
		roots = self.parse_forest(input_tuple)
		print "parse ended"
		logging.info("Parsed ok, now counting	")
		total = 0
		if not roots:
			return total
		for x in roots:
			n = x.count_trees()
			if n < 0:
				return -1
			total += x.count_trees()
		return total


	def parse_forest(self, input_tuple):
		"""
		Return a shared packed binarised parse forest.
		"""
		self._initialise_state_sets(len(input_tuple))
		self.input = input_tuple
		l = len(self.input)
		self.process()
		builder = forest.ForestBuilder(self.input, self.grammar,self)
		roots = set()
		for x in self.chart[l]:
			logging.info("Checking %s", to_string(x))
			if is_complete(x) and x[3] == 0 and x[0] in self.grammar.start_set:
				logging.info("Found root node %s", to_string(x))
				u = builder.get_node(0,l,x[0])
				builder.build_tree(u,x)
				roots.add(u)
		#builder.dump()
		

		return list(roots)

	def process(self):
		"""
		Loop through until agenda is empty.
		"""
		t0 = time.time()
		for i in xrange(self.length + 1):
			chartx = self.chart[i]
			j = 0
			while j < len(chartx):
				item = chartx[j]
				j = j+1
				logging.info("Processing %s", to_string(item))
				if is_complete(item):
					logging.info("Complete item")
					self.completer(item)
				else:
					next = next_category(item)
					if next in self.grammar.terminals:
						self.scanner(item)
					else:
						# we only need this if we have cheated with the chart
						# and added some blank items 
						self.scanner(item)
						self.predictor(item)
		t1 = time.time()
		if time_parser:
			logging.warning("Parse: l = %d, t = %f" % (len(self.input), t1-t0))		
					

	def completer(self,item):
		"""
		Item is a complete constituent, so we look for  and enqueue them.
		"""
		position = item[3]
		label = item[0]
		
		#for other_item in self.chart[position]:
		chartx = self.chart[position]
		i = 0
		while i < len(chartx):
			other_item = chartx[i]
			i += 1
			logging.info("Matching with %s ", to_string(other_item))
			if not is_complete(other_item):
				if next_category(other_item) == label:
					## match!
					new_item = (other_item[0],other_item[1],other_item[2]+1, other_item[3],item[4])
					#print "appending", to_string(item), "to", to_string(new_item)
					# append the complete,incomplete pair
					self.reduced_states[new_item].append(item)
					if other_item[2]> 0:
						self.previous_states[new_item].append(other_item)
					logging.info("Creating new item  %s ", to_string(new_item))
					self.enqueue(new_item)

	def enqueue(self,item):
		"""
		agenda_set is the set of all things we have put on the agenda at any time.
		"""
		pos = item[4]
		if not item in self.chart_set[pos]:
			self.chart_set[pos].add(item)
			self.chart[pos].append(item)



	def dump_complete_items(self):
		for c in self.chart:
			for item in c:
				if is_complete(item):
					print to_string(item)

	def scanner(self,item):
		"""
		Incomplete item looking for a terminal.
		"""
		terminal = next_category(item)
		logging.info("Scanning %s", terminal)
		if item[4] >= len(self.input):
			logging.info("End of string")
			return False
		if terminal == self.input[item[4]]:
			# match

					
			new_item = (item[0],item[1],item[2]+1,item[3],item[4]+1)
			#self.previous_states[new_item].append((terminal,item))
			#rint "appending", terminal, "to", to_string(new_item)
			self.enqueue(new_item)
			return True

	def predictor(self,item):
		"""
		Incomplete item looking for a nonterminal.
		"""
		nonterminal = next_category(item)
		if nonterminal in self.nullable:
			logging.info("Nullable item %s", nonterminal)
			# Aycock and Horspool
			new_item = (item[0],item[1],item[2]+1, item[3],item[4])
			self.enqueue(new_item)
		for prod in self.grammar.productions:
			if prod[0] == nonterminal:

				new_item = (prod[0],prod[1],0,item[4],item[4])
				logging.info("Predicting %s", to_string(new_item))
				self.enqueue(new_item)
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="""
			Interactive Earley parser for an arbitrary CFG.
		""")
	parser.add_argument("grammar", help="File containing pcfg")
	args = parser.parse_args()

	grammar = cfg.load_from_file(args.grammar)
	parser = EarleyParser(grammar)
	while True:
		line = raw_input("Type in line:")
		print parser.parse(tuple(line.split()))






