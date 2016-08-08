import numpy
import string

class TreeNode:

	def __init__(self,label):
		self.label = label
		self.daughters = []

	def depth(self):
		if self.isLeaf():
			return 0
		else:
			return 1 + max([ d.depth() for d in self.daughters])

	def width(self):
		if self.isLeaf():
			return 1
		else:
			w = 0
			for d in self.daughters:
				w += d.width()
			return w

	def dump(self):
		print "(", self.label, 
		for daughter in self.daughters:
			daughter.dump()
		print ")",

	def yield1(self, current):
		if self.isLeaf():
			current.append(self.label)
		else:
			for daughter in self.daughters:
				daughter.yield1(current)

	def collectYield(self):
		current = []
		self.yield1(current)
		return current

	def collectPreterminals(self):
		current = []
		self.collectPreterminals1(current)
		return current

	def collectPreterminals1(self,current):
		if not self.isLeaf() and len(self.daughters) == 1 and self.daughters[0].isLeaf():
			current.append(self.label)
			return
		if not self.isLeaf():
			for d in self.daughters:
				d.collectPreterminals1(current)

	def collect_contexts_of_nt(self,nonterminal):
		"""
		Returns a list of all contexts of nonterminal in this tree.
		If there are none then the list is empty.
		"""
		occurrences = set()
		self.find_nt_occurrences(nonterminal,occurrences)
		answer = []
		for subtree in occurrences:
			answer.append(self.collect_context_of_subtree(subtree))
		return answer

	def find_nt_occurrences(self,nonterminal,occurrences):
		if self.label == nonterminal:
			occurrences.add(self)
		for d in self.daughters:
			d.find_nt_occurrences(nonterminal,occurrences)

	def collect_context_of_subtree(self,subtree):
		"""
		Return the context of subtree in this tree. The subtree must occur in the tree.
		"""
		left = []
		right = []
		passed = self.collect_context_of_subtree_lr(subtree,left,right,False)
		if passed:
			return (tuple(left),tuple(right))
		else:
			raise ValueError("Doesnt occur in tree")


	def collect_context_of_subtree_lr(self,subtree, left,right, passed):
		"""
		Returns True once we have passed the occurrence of the subtree.
		"""
		if self == subtree:
			# we are in the middle
			if passed:
				raise ValueError("This subtree occurs twice in this tree.")
			else:
				return True
		elif passed:
			# then we attach to the right
			if self.isLeaf():
				right.append(self.label)
			else:
				for d in self.daughters:
					d.collect_context_of_subtree_lr(subtree,left,right,passed)
		else:
			# not passed
			if self.isLeaf():
				left.append(self.label)
			else:
				for d in self.daughters:
					# we may pass in one of the daughters so we update passed
					passed = d.collect_context_of_subtree_lr(subtree,left,right,passed)

		return passed

	def isLeaf(self):
		"""
		return true if this is a leaf
		"""
		return len(self.daughters) == 0 and self.label[0].islower()

	def storeTreeToFile(self,fileobject):
		"""Store it in bracketed format on one line"""
		if self.isLeaf():
			fileobject.write(self.label + " ")
		else:
			fileobject.write("( " + self.label + " ")
			for daughter in self.daughters:
				daughter.storeTreeToFile(fileobject)
			fileobject.write(" )")

	def count_productions(self, counter):
		if not self.isLeaf():
			rhs = [ x.label for x in self.daughters]
			prod = (self.label,tuple(rhs))
			counter[prod] += 1
			for x in self.daughters:
				x.count_productions(counter)

def storeYieldToFile(node,file_object):
	yieldlist = node.collectYield()
	for leaf in yieldlist:
		file_object.write(leaf)
		file_object.write(' ')
	file_object.write('\n')

def storeYieldToFile(node,file_object):
	yieldlist = node.collectYield()
	for leaf in yieldlist:
		file_object.write(leaf)
		file_object.write(' ')
	file_object.write('\n')


