#
# Better code for testing whether a given CFG has the FKP or FCP or some combinations.
# The problem is the large number of different parameters that we need to set in a reasonable way.
# So we need some intelligent way of determining what the values should be or 
# it won't terminate or be far too slow.
# 
# The key factors are the length of the strings we need.
#


# start with primal
import cfg
import uniformsampler
import earleyparser

import numpy
import logging

# these two are  used for the samplers -- this should be a lot bigger than the actual strings
# we look at.
max_context_length = 50
max_substring_length = 50

# for primal approach, we try to use 
number_yields = 10

# when trying to find a kernel or whatever, 
# we try max_attempts times.
max_attempts = 50

#
# FCP code
#
def test_strong_fcp_full(grammar, k):
	"""
	Main entry point for the dual tester.

	Method:
	"""
	result = dict()
	parser = earleyparser.EarleyParser(grammar)
	sampler = uniformsampler.UniformSampler(grammar, max_substring_length)
	contextsampler = uniformsampler.ContextSampler(grammar, sampler, max_context_length)
	ncontexts = 25
	for nt in grammar.nonterminals:
		r = test_strong_fcp_nt(grammar, parser, sampler, contextsampler,  nt, k, ncontexts, stop=True)
		if r:
			print "nt", nt,  r
			result[nt] = r
		else:
			print "Fail ", nt
			return False
	return result

def test_strong_fcp_nt(grammar, parser, sampler, contextsampler, nt, k, ncontexts, stop = True):
	"""
	Test whether this nt has a the k FCP.
	
	Method: pick some contexts in some sensible way.

	"""
	
	contexts = list(pick_some_contexts(grammar, sampler, contextsampler, nt, ncontexts))
	fake_list = range(len(contexts))
	done = set()
	good = 0
	bad = 0
	nsamples = 100
	if len(contexts) <= k:

		# we can't sample
		if test_strong_fcp_contexts(grammar, parser, nt, contexts, nsamples):
			return contexts
		else:
			return False

	for i in xrange(max_attempts):
		# pick k strings withour replacement

		cis = numpy.random.choice(fake_list, k, replace = False)
		cis = sorted(cis)
		cis = tuple(cis)
		#print "Attempt ", i, " strings", strings
		if not cis in done:
			done.add(cis)

			xcontexts = [ contexts[x] for x in cis]
			print "XXX testing contexts", xcontexts
			if test_strong_fcp_contexts(grammar, parser, nt, xcontexts, nsamples):
				good += 1
				if stop:
					return xcontexts
				#return strings	
			else:
				bad += 1
	if stop:
		return False
	else:
		return (good,bad)
	for i in xrange(number_attempts):
		pass


def test_one_fcp_exact(grammar, ncontexts):
	"""
	See if this has the exact 1-fcp. Use ncontexts
	"""
	sampler = uniformsampler.UniformSampler(grammar, max_substring_length)
	contextsampler = uniformsampler.ContextSampler(grammar, sampler, max_context_length)
	result = dict()
	#ok = True
	for nt in grammar.nonterminals:
		if nt in grammar.start_set and len(grammar.start_set) == 1:
			result[nt] = ((),())
		else:
			c = test_one_fcp_nt_exact(grammar,sampler, contextsampler,nt,ncontexts)
			if c:
				print nt, c
				result[nt] = c
			else:
				print "FAIL ", nt
				#ok = False
				return False
	return result

def count_one_fcp_exact(grammar, ncontexts):
	"""
	See if this has the exact 1-fcp. Use ncontexts
	"""
	sampler = uniformsampler.UniformSampler(grammar, max_substring_length)
	contextsampler = uniformsampler.ContextSampler(grammar, sampler, max_context_length)
	result = dict()
	#ok = True
	for nt in grammar.nonterminals:
		if nt in grammar.start_set and len(grammar.start_set) == 1:
			result[nt] = ((),())
		else:
			c = test_one_fcp_nt_exact(grammar,sampler, contextsampler,nt,ncontexts)
			if c:
				result[nt] = c		
	return result



def test_strong_fcp_contexts(grammar, parser,  nonterminal, contexts, nsamples):
	"""
	Test whether this nonterminal is characterised by these contexts or not.

	Method: sample from 1 context. 
	excluding ones that are derived from the nonterminal.
	Then check whether it is accepted by all of the others.
	If it is then test if it is derived from the nonterminal.
	"""
	first_context = contexts[0]
	(leftpart,rightpart) = first_context
	totalwidth = len(leftpart) + len(rightpart)
	ig = grammar.context_grammar_without_nt(first_context, nonterminal)
	#ig.dump()
	if ig.is_empty():
		print "Exact FCP success"
		return True
	# otherwise 
	sample_strings = pick_some_inside_strings(ig, first_context, nsamples)
	#print "Sample strings ", len(sample_strings), sample_strings
	for w in sample_strings:
		#print "W = ", w
		if len(w) > 0:
			if not parser.parse_start(w,nonterminal):
				#print "Possible ce", w
				# ok now this string might be a counterexample
				# since it is accepted by the first context 
				# bit not in the yield of the nonterminal. 
				for l,r in contexts[1:]:
					lwr = l + tuple(w) + r
					#print "LWR", lwr
					if not parser.parse(lwr):
						#print "Not parsed"
						break
				else:
					#print "accepted by all "
					logging.info("failed %s" , w)
					return False
	return True

def pick_some_inside_strings(igrammar, context, nsamples):
	"""
	Pick some strings that are generated by this grammar 
	which is the intersection of a context automata.

	Method: construct sampler; fiddle about a bit to get the right length.
	Sample and then snip off.
	"""
	(left,right) = context
	ll = len(left)
	lr = len(right)
	l = len(left) + len(right)
	sampler = uniformsampler.UniformSampler(igrammar, l + max_substring_length)
	# this will not generate any strings of length less than l
	raw =  list(set(sampler.multiple_sample(nsamples, nsamples*2)))
	#print context
	#print "RAW", raw
	result = [ x[ll: len(x) -lr] for x in raw ]
	#print result
	return result

#
# FKP code
#

def test_strong_fkp_full(grammar, k):
	"""
	Main entry point for the primal tester.
	Returns a tuple (True|False, map[ nonterminals to k-tuples of strings ])
	"""
	result = dict()
	parser = earleyparser.EarleyParser(grammar)
	sampler = uniformsampler.UniformSampler(grammar, max_substring_length)
	ncontexts = 25
	for nt in grammar.nonterminals:
		r = test_strong_fkp_nt(grammar, parser, sampler, nt, k, ncontexts, stop=True)
		if r:
			result[nt] = r
		else:
			return False
	return result




def test_one_fkp_exact(grammar, nyields):
	"""
	See if this has the exact 1-fkp.
	"""
	sampler = uniformsampler.UniformSampler(grammar, max_substring_length)
	result = dict()
	for nt in grammar.nonterminals:
		w = test_one_fkp_nt_exact(grammar,sampler,nt,nyields)
		if w:
			result[nt] = w
		else:
			logging.info("failed on %s" % nt)
			return False
	return result


def test_one_fkp_nt_exact(grammar, sampler, nonterminal, nyields):
	"""
	Try a few different strings.
	"""
	yields = pick_some_yields(grammar, sampler, nonterminal, nyields)
	#print "testing nonterminal", nonterminal
	#print yields
	for w in yields:
		if test_one_fkp_nt_string_exact(grammar, nonterminal, w):
			return w
	return False


def test_one_fcp_nt_context_exact(grammar, nonterminal, context):
	"""
	Test if this nonterminal is exactly characterised by this context.

	Test to see if the only way we can get this context is as a context of nt.
	This is too strong.
	"""
	logging.info("Testing context %s", context)
	ig = grammar.context_grammar_without_nt(context, nonterminal)
	#ig.dump()
	if ig.is_empty():
		return True
	else:
		logging.info("Generates %s", ig.generate_string())
		return False



def test_one_fcp_nt_exact(grammar, sampler, contextsampler, nonterminal, ncontexts):
	"""
	Test if this nonterminal is exactly characterised by some context; try ncontexts times.

	"""
	contexts = pick_some_contexts(grammar, sampler, contextsampler, nonterminal, ncontexts)

	#print "num contexts", len(contexts)
	#print "contexts", contexts
	for c in contexts:
		#print c
		if test_one_fcp_nt_context_exact(grammar, nonterminal,c):
			return c
	return False



def test_one_fkp_nt_string_exact(grammar, nonterminal, w):
	"""
	See if this nonterminal is characterised by this single substring
	which is one of its yields.

	Use an over strong condition: test to see if the only occurrences of 
	w are yields of nonterminal.
	"""
	ig = grammar.infix_grammar_without_nt(w, nonterminal)
	return ig.is_empty()

def test_one_fkp_nt_string_inexact(grammar, nonterminal, w, ncontexts):
	"""
	See if this nonterminal is characterised by this single substring
	which is one of its yields.

	First
	"""
	ig = grammar.infix_grammar_without_nt(w, nonterminal)
	if ig.is_empty():
		return True
	# it is noempty so sample
	sampler = uniformsampler.UniformSampler(ig, max_substring_length)
	samples = sampler.multiple_sample(ncontexts, ncontexts ** 2)
	contexts = []
	for lwr in set(samples):
		# extract the contexts
		# for each context test if it is a context of the nonterminal.
		for context in extract(lwr,w):

			contexts.append(context)

def test_strong_fkp_nt(grammar, parser, sampler, nonterminal, k, ncontexts, stop=False):
	"""
	Test whether this  nonterminal is well characterised by k substrings.

	We pick some substrings that are generated by the nonterminal.
	Sample k-sized subsets of these randomly.
	We test whether the shared contexts of these substrings are all contexts of the nonterminal.
	"""
	print "testing ", nonterminal
	possible_strings = list(pick_some_yields(grammar,sampler, nonterminal, number_yields))
	print possible_strings
	if len(possible_strings) <= k:
		return test_strong_fkp_strings(grammar, parser, nonterminal, possible_strings, ncontexts)
			
	fake_list = range(len(possible_strings))
	done = set()
	good = 0
	bad = 0
	for i in xrange(max_attempts):
		# pick k strings withour replacement

		strings = numpy.random.choice(fake_list, k, replace = False)
		strings = sorted(strings)
		strings = tuple(strings)
		#print "Attempt ", i, " strings", strings
		if not strings in done:
			done.add(strings)
			real_strings = [ possible_strings[x] for x in strings]
			if test_strong_fkp_strings(grammar, parser, nonterminal, real_strings, ncontexts):
				good += 1
				if stop:
					return real_strings
				#return strings	
			else:
				bad += 1
	if stop:
		return False
	else:
		return (good,bad)

def look_at_distribution_of_nt(grammar, parser, nonterminal, num):
	"""
	Test to see if there are lots of short contexts of the nonterminal.
	Return the length of context we need to get num derivation samples.
	If this number is too long. 
	
	If there aren't then we need to use smaller amounts of samples, 
	and maybe use some exhaustive sampling techniques.
	"""
	csampler = uniformsampler.CrudeContextSampler(grammar, nonterminal, max_context_length)
	total = 0
	for i in xrange(max_context_length):
		c = csampler.sampler.get_total(i+1)
		total += c 
		if total > num:
			return i
	else:
		return -1



def pick_some_contexts(grammar, sampler, contextsampler, nonterminal, n):
	"""
	pick a bunch of contexts of this nonterminal that might be good characterisations of it.
	"""
	result = set()
	short = contextsampler.collect_shortest_contexts(nonterminal)
	for context in short:
		result.add(context)
	total = 0
	lengths = []
	counts = []
	# pick a length so that we have > 2n possibilities 
	for i in xrange(max_context_length):
		c = contextsampler.get(nonterminal=nonterminal, length= i)
		#print "COntexts of length %d are %d" % (i,c)
		total += c
		lengths.append(i)
		counts.append(c)
		if total > 2 * n:
			break
	if total == 0:
		raise ValueError("no short contexts at all of nonterminal.")
	# now we 
	distribution = [x / total for x in counts]
	max_attempts = n * n
	# by sampling from these we will end up with a distribution
	# that is mostly long.
	clengths = numpy.random.choice(lengths, max_attempts, p=distribution )
	for length in clengths:
		context = contextsampler.sample_context(nonterminal = nonterminal, length=length)
		result.add(context)
		if len(result) >= n:
			return result

	return result

	


def pick_some_yields(grammar, sampler, nonterminal, n):
	"""
	return n short strings that are generated by this nonterminal.
	We will pick n quite large normally, so that we have some variety.
	"""
	result = set()
	# make sure we get the easy ones too.
	for prod in grammar.productions:
		if prod[0] == nonterminal:
			if grammar.is_terminal_production(prod):
				logging.info("adding lexical rule %s -> %s" % (nonterminal, prod[1]))
				result.add(prod[1])
	# pick some lengths
	total = 0
	lengths = []
	counts = []
	# pick a length so that we have > 2n possibilities 
	for i in xrange(max_substring_length):
		c = sampler.get(nonterminal=nonterminal, length= i)
		total += c
		lengths.append(i)
		counts.append(c)
		if total > 2 * n:
			break
	if total == 0:
		raise ValueError("no short yields of nonterminal.")
	# now we 
	distribution = [x / total for x in counts]
	max_attempts = n * n
	# by sampling from these we will end up with a distribution
	# that is mostly long.
	clengths = numpy.random.choice(lengths, max_attempts, p=distribution )
	for length in clengths:
		w = sampler.sample_from_nonterminal(nonterminal = nonterminal, length=length).collectYield()
		result.add(tuple(w))
		if len(result) >= n:
			return result

	return result



def test_strong_fkp_strings(grammar, parser, nonterminal, strings, ncontexts):
	"""
	Test whether these strings are a good characterisation of this nonterminal.
	"""
	contexts = intersect_strings(grammar, strings, parser, ncontexts )
	for context in contexts:
		if not parser.parse_nonterminal_context(context[0], nonterminal, context[1]):
			return False
	return True


def intersect_strings(grammar, strings, parser,ncontexts):
	"""
	Find some shared contexts of these strings.
	"""
	base = strings[0]
	print "testing string", base
	contexts = sample_from_substring(grammar,base,ncontexts)
	
	results = set()
	for context in contexts:
		for w in strings[1:]:
			lwr = context[0] + tuple(w) + context[1]
			#print lwr
			if not parser.parse(lwr):
				break
		else:
			results.add(context)
	print "intersected strings", len(results)
	return results


def sample_from_substring(grammar, w, n):
	"""
	return a set of n short contexts of this substring.
	
	If we can't find any then return.
	"""
	infixgrammar = grammar.infix_grammar(w)
	
	max_length = 10
	sampler = uniformsampler.UniformSampler(infixgrammar, len(w) + max_context_length)
	total = 0
	counts = []
	lengths = []
	for i in xrange(len(w), len(w) + max_context_length):
		c = sampler.get_total(i)
		counts.append(c)
		lengths.append(i)
		total += c
		if total > n * n:
			break
	else:
		# we are in some situation where the number of strings is low.
		logging.warning("Sparse contexts")
	max_attempts = n * n
	result = set()
	distribution = [x / total for x in counts]
	clengths = numpy.random.choice(lengths, max_attempts, p=distribution )
	for l in clengths:
		lwr = sampler.sample(l).collectYield()
		for context in extract(lwr,w):
			result.add(context)
		if len(result) >= n:
			return result
	else:
		logging.warning("Didn't find all of the contexts.")
		return result
		# pick a length and then sample 


def extract(sentence, substring):
	sentence = list(sentence)
	substring = list(substring) 
	contexts = []
	l = len(substring)
	for i in xrange(len(sentence)):
		if sentence[i:i+l] == substring:
			left = sentence[0:i]
			right = sentence[i+l: len(sentence)]
			contexts.append((tuple(left),tuple(right)))
	return contexts