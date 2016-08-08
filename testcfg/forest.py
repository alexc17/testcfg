# Based on Elizabeth Scott 2008 paper
import logging
import earleyparser

class ForestBuilder:
	"""
	A shared packed parse forest Tomita style.
	For representing the output of a parser.

	We binarise the tree. 

	"""

	def __init__(self, word,cfg, parser):
		self.word = word
		self.cfg = cfg
		self.parser = parser
		# map from the spans to Nodes
		self.index = {}
		# set of completed items
		self.completed = set()

	def dump(self):
		for x in self.index:
			print self.index[x].get_index()


	def get_node(self, start, end, label):
		"""
		return the right node with this label 
		and create a new node if needed.
		"""
		cspan = (start,end,label)
		if cspan in self.index:
			return self.index[cspan]
		else:
			newNode = ForestNode(start,end,label)
			self.index[cspan] = newNode
			return newNode
	

	def build_tree(self, u, item):
		self.completed.add(item)
		parser = self.parser
		logging.info("Build tree item %s node %s" % (earleyparser.to_string(item), u.get_index()))
		(lhs,rhs,position, start,end) = item
		assert u.start == start
		assert u.end == end
		if len(rhs) == 0:
			# epsilon production
			v = self.get_node(start,end,lhs)
			u.add_unary(v)
			return
		if position == 0:
			return
		if position == 1 and rhs[0] in self.cfg.terminals:
			v = self.get_node(start,end,rhs[0])
			u.add_unary(v)
			return
		if position == 1:
			v = self.get_node(start,end,rhs[0])
			u.add_unary(v)
			for complete_item in parser.reduced_states[item]:
				assert complete_item[3] == start
				assert complete_item[4] == end
				if not complete_item in self.completed:
					self.build_tree(v,complete_item)
			return
		# position is > 1
		if rhs[position - 1] in self.cfg.terminals:
			v = self.get_node(end-1,end,rhs[position -1 ])
			w = self.get_node(start,end-1, (lhs,rhs,position-1))
			
			for incomplete in parser.previous_states[item]:
				assert incomplete[3] == start
				assert incomplete[4] == end -1
				self.build_tree(w,incomplete)
			u.add_pair(w,v)
			return
		# otherwise
		for complete_item in parser.reduced_states[item]:
			(clhs,crhs,cposition, cstart,cend) = complete_item
			assert clhs == rhs[position -1]
			assert cend == end
			v = self.get_node(cstart,end,clhs)
			if not complete_item in self.completed:
				self.build_tree(v,complete_item)
			w = self.get_node(start,cstart,  (lhs,rhs, position -1))
			for incomplete_item in parser.previous_states[item]:
				if not incomplete_item in self.completed:
					if incomplete_item[4] == cstart:
						self.build_tree(w,incomplete_item)
			u.add_pair(w,v)







class ForestNode:
	""" 
	This represents the set of all subtrees that generate a given span and label. 
	The label is either a nonterminal or a production, index pair for longer productions
	"""
	def __init__(self, start, end, label):
		self.start = start
		self.end = end
		self.label = label
		# each subtree is a tuple of ForestNodes or terminals. 
		# of arity 0,1 or 2
		# we can recover the rule then just from the labels.
		self.subtrees = []
		self.subtree_set = set()


	def count_trees(self):
		"""
		Returns -1 if infinite.
		"""
		counts = {}
		visited = set()
		try:
			return self.count_trees2(counts, visited)
		except ValueError:
			return -1

	def count_trees2(self, counts, visited):
		logging.info("Counting : %s ", self.get_index())
		if not self in counts:
			if self in visited:
				logging.info("Loop with %s", self.get_index())
				raise ValueError("infinite")
			visited.add(self)
			if len(self.subtrees) == 0:
				counts[self] = 1.0
			else:
				total = 0
				for subtree in self.subtrees:
					logging.info( "subtree length %d" % len(subtree))
					total += reduce(lambda x, y: x*y, [ x.count_trees2(counts, visited) for x in subtree ], 1.0)
				counts[self] = total
		logging.info("Leaving : %s, %s " % (self.get_index(), counts[self]))
		return counts[self]

	def count_trees_finite(self):
		"""
		Will not terminate if there are an infinite number of trees.
		"""
		if len(self.subtrees) == 0:
			return 1.0
		total = 0
		for subtree in self.subtrees:
			total += reduce(lambda x, y: x*y, [ x.count_trees_finite() for x in subtree ], 1.0)
		return total

	def gather_trees(self):
		if len(self.subtrees) == 0:
			return [ label ]
		for (x,y) in self.subtrees:
			xtrees = x.gather_trees()
			ytrees = y.gather_trees()


	def get_index(self):
		return (self.start,self.end,self.label)

	def add_pair(self, first, second):
		"""
		arguments are two ForestNodes
		"""
		index = (first.get_index(),second.get_index())
		if not index in self.subtree_set:
			self.subtrees.append((first,second))
			self.subtree_set.add(index)	

	def add_unary(self, first):
		"""
		arguments is one ForestNode
		"""
		if not first.get_index() in self.subtree_set:
			self.subtrees.append((first,))
			self.subtree_set.add(first.get_index())	
