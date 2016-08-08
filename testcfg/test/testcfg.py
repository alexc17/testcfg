# test cfg

import unittest
import cfg
import cfgfcp
import generatecfg
import earleyparser
import partitionfunction
import inside
import math
import logging
import sys, random
import uniformsampler, generatepcfg
#testcode for pcfgs

class CfgTest(unittest.TestCase):

	def test_load(self):
		"""
		Test that it can load a file correctly.
		"""
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")

		self.assertEqual(len(grammar.terminals), 5)
		self.assertEqual(len(grammar.nonterminals), 1)
		n = grammar.compute_nullable()
		self.assertEqual(len(n), 0)

	def test_nullable1(self):
		"""
		Test that it can load a file correctly.
		"""
		grammar = cfg.load_from_file("../data/cfgs/cfg2.cfg")

		self.assertEqual(len(grammar.terminals), 4)
		self.assertEqual(len(grammar.nonterminals), 1)
		n = grammar.compute_nullable()
		self.assertEqual(len(n), 1)

	def test_nullable2(self):
		"""
		Test that it can load a file correctly.
		"""
		grammar = cfg.load_from_file("../data/cfgs/cfg3.cfg")

		n = grammar.compute_nullable()
		self.assertEqual(len(n), 4)
		cor = grammar.compute_coreachable()
		self.assertEqual(len(cor), 4)
		trim = grammar.compute_trim_set()
		self.assertEqual(len(trim), 3)


	def test_parser(self):
		"""
		Basic tests of the Earley parser.
		"""
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		parser = earleyparser.EarleyParser(grammar)
		self.assertTrue(parser.parse(("ax","c","bx")))
		self.assertTrue(parser.parse(("c",)))
		self.assertFalse(parser.parse(("ax",)))
		self.assertFalse(parser.parse(()))

	def test_parser2(self):
		"""
		Basic tests of the Earley parser.
		"""
		grammar = cfg.load_from_file("../data/cfgs/cfg2.cfg")
		parser = earleyparser.EarleyParser(grammar)
		self.assertTrue(parser.parse(("ax","bx")))
		self.assertTrue(parser.parse(("ax","ax","ax","bx","bx","bx")))
		self.assertTrue(parser.parse(("ax","ay","ax","bx","by","bx")))
		self.assertFalse(parser.parse(("ax","ay","ax","bx","by")))
		self.assertFalse(parser.parse(("ax",)))
		self.assertTrue(parser.parse(()))

	def test_nullParser(self):
		grammar = cfg.load_from_file("../data/cfgs/null1.cfg")
		parser = earleyparser.EarleyParser(grammar)
		self.assertTrue(parser.parse(()))

	def test_nullParser2(self):
		grammar = cfg.load_from_file("../data/cfgs/null2.cfg")
		parser = earleyparser.EarleyParser(grammar)
		self.assertTrue(parser.parse(()))
		self.assertTrue(parser.parse(("a","b","c")))
		self.assertTrue(parser.parse(("b","c")))
		self.assertTrue(parser.parse(("a",)))
		self.assertTrue(parser.parse(("a","c")))
		self.assertFalse(parser.parse(("c","a")))


	def test_rightrecursion(self):
		grammar = cfg.load_from_file("../data/cfgs/rr.cfg")
		parser = earleyparser.EarleyParser(grammar)
		self.assertFalse(parser.parse(()))
		self.assertTrue(parser.parse(("a","x","x","b")))

	def test_errormay(self):
		grammar = cfg.load_from_file("../data/cfgs/parseerror1.cfg")
		parser = earleyparser.EarleyParser(grammar)
		w = ('pl', 'bc', 'zd', 'cl')
		self.assertTrue(parser.parse(w))

	def test_cfg4(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg4.cfg")
		parser = earleyparser.EarleyParser(grammar)
		self.assertTrue(parser.parse(()))
		self.assertTrue(parser.parse(("b","b")))

	def test_parse_other_nt(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg3.cfg")
		parser = earleyparser.EarleyParser(grammar)
		self.assertTrue(parser.parse(("ax","c","bx")))
		self.assertFalse(parser.parse_start(("ax","c","bx"), "A"))
		self.assertTrue(parser.parse(("b","b")))
		self.assertTrue(parser.parse_start(("b","b"), "A"))

	def test_parse_context(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		parser = earleyparser.EarleyParser(grammar)
		#logging.basicConfig( filename='parser.log',  level=logging.INFO)
		root = logging.getLogger()

		#root.setLevel(logging.INFO)
		#logging.basicConfig(filename='parser.log', level=logging.INFO)
		logging.info('Started test_parse_context')
		self.assertTrue(parser.parse_nonterminal_context(("ax",), "S", ("bx",)))
		logging.info('Ended test_parse_context')
		#root.setLevel(logging.WARNING)

	def test_trim(self):
		grammar = cfg.load_from_file("../data/cfgs/large1.cfg")
		trimset = grammar.compute_trim_set()
		self.assertTrue("S" in trimset)

	def test_trim2(self):
		grammar = cfg.load_from_file("../data/cfgs/trimerror.cfg")
		trimset = grammar.compute_trim_set()
		self.assertTrue("S" in trimset)
		trim = grammar.trim()
		self.assertTrue("S" in trim.nonterminals)
		self.assertFalse("Nc_0->0" in trim.nonterminals)
		self.assertFalse("Nc_0->0" in trim.nonterminals)
		#trim.dump()


	def test_cyclic1(self):
		arcs = set()
		for edge in [ (0,1), (1,2) , (1,3), (1,5), (1,0)]:
			arcs.add(edge)

		self.assertTrue(cfg._test_cyclic(arcs))

	def test_unary_loops1(self):
		grammar = cfg.load_from_file("../data/cfgs/unary_loops1.cfg")
		
		self.assertTrue(grammar.has_unary_loops())

	def test_unary_loops2(self):
		grammar = cfg.load_from_file("../data/cfgs/unary_loops2.cfg")
		
		self.assertFalse(grammar.has_unary_loops())

	def test_count_parses(self):
		grammar = cfg.load_from_file("../data/cfgs/sigmaplus2.cfg")
		parser = earleyparser.EarleyParser(grammar)

		w = ("a", "b", "a", "a", "b", "a", "a", "a", "a", "b", "a", "a", "b", "a", "a", "a")

		x = parser.parse_forest(w)
		self.assertEqual(1, len(x))
		self.assertEqual(x[0].count_trees(),9694845.0 )

	def test_merge(self):
		grammar = cfg.load_from_file("../data/cfgs/unary_loops1.cfg")
		self.assertTrue(grammar.has_unary_loops())
		grammar2 = grammar.merge_unary()
		#grammar2.dump()
		self.assertTrue(len(grammar.nonterminals) > len(grammar2.nonterminals))
		#self.assertFalse(grammar2.has_unary_loops())

	def test_infix_grammar(self):
		grammar = cfg.load_from_file("../data/cfgs/abab2.cfg")
		substring = ("a1", "a1", "a1", "a1", "b1", "b1", "b1", "b1")
		ig = grammar.infix_grammar(substring)

 
	def test_infinite1(self):
		#print "Testing infinite1"
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		self.assertTrue(grammar.language_infinite())

	def test_infinite2(self):
		#print "Testing infinite2"
		grammar = cfg.load_from_file("../data/cfgs/finite1.cfg")
		self.assertFalse(grammar.language_infinite())

	
	def test_topologicalsort(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		sort = grammar.topological_sort()
		self.assertEqual(len(sort), 1)

	def test_topologicalsort2(self):
		grammar = cfg.load_from_file("../data/cfgs/unary_noloops.cfg")
		sort = grammar.topological_sort()
		self.assertEqual(len(sort), 7)

	def test_uniformsampler(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		sampler = uniformsampler.UniformSampler(grammar, 20)
		self.assertEqual(sampler.get("S",0),0)
		self.assertEqual(sampler.get("S",1),1)
		self.assertEqual(sampler.get("S",2),0)
		self.assertEqual(sampler.get("S",3),2)
		self.assertEqual(sampler.get("S",5),4)
		#print "about to sample."
		tree = sampler.sample(5)
		self.assertEqual(tree.width(), 5)

		#tree.dump()

	def test_uniformsampler2(self):
		grammar = cfg.load_from_file("../data/cfgs/count1.cfg")
		sampler = uniformsampler.UniformSampler(grammar, 10)
		#sampler.dump()
		self.assertEqual(sampler.get("S",0),1)
		self.assertEqual(sampler.get("S",1),2)
		self.assertEqual(sampler.get("S",2),1)
		self.assertEqual(sampler.get("S",3),0)
		self.assertEqual(sampler.get("S",5),0)

	def test_density1(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		sampler = uniformsampler.UniformSampler(grammar, 10)
		density = 4.0 /(5 ** 5)
		self.assertAlmostEqual(sampler.density(5),density)

	def test_generate(self):
		factory = generatecfg.CfgFactory()
		factory.number_terminals = 10
		factory.number_nonterminals = 10
		factory.number_productions = 100
		grammar = factory.make_grammar()
		#grammar.dump()
		self.assertEqual(factory.number_terminals, len(grammar.terminals))	
		self.assertEqual(factory.number_nonterminals, len(grammar.nonterminals))	


	def test_generate2(self):
		factory = generatecfg.CfgFactory()
		factory.number_terminals = 100
		factory.number_nonterminals = 10
		factory.number_productions = 200
		factory.max_rhs_length = 3
		factory.min_nt_rhs = 3
		grammar = factory.make_grammar()
		#grammar.dump()
		self.assertEqual(factory.number_terminals, len(grammar.terminals))	
		self.assertEqual(factory.number_nonterminals, len(grammar.nonterminals))
		for nt in grammar.nonterminals:
			self.assertTrue(grammar.count_productions_rhs(nt) >= 3)	

	def test_generate3(self):
		factory = generatecfg.CfgFactory()
		factory.no_lexical_ambiguity = True 
		factory.number_nonterminals = 10
		factory.number_productions = 200
		factory.max_rhs_length = 3
		factory.min_nt_rhs = 3
		grammar = factory.make_grammar()
		#grammar.dump()
		random.seed(3)
		self.assertEqual(factory.number_nonterminals, len(grammar.nonterminals))
		for nt in grammar.terminals:
			#print nt, grammar.count_productions_rhs(nt)
			self.assertEqual(grammar.count_productions_rhs(nt),1)	

	def test_intersection1(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		prefix = ("ax",)
		pg = grammar.prefix_grammar(prefix)
		#print "Dump prefix grammar"
		#pg.dump()
		self.assertTrue("S" in pg.nonterminals)
		sampler = uniformsampler.UniformSampler(pg, 10)

		#print "Dumping intersected sampler"
		#sampler.dump()
		self.assertEqual(sampler.get("S",0),0)
		# self.assertEqual(sampler.get("S",1),0)
		# self.assertEqual(sampler.get("S",2),0)
		# self.assertEqual(sampler.get("S",3),0)
		# self.assertEqual(sampler.get("S",5),1)


	def test_context_intersection(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		igr = grammar.single_occurrence_grammar("ax")
		#igr.dump()
		self.assertTrue("S" in igr.nonterminals)

	def test_context_sampler(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		cs = uniformsampler.CrudeContextSampler(grammar, "S", 20)
		#print cs.sampler
		#cs.sampler.dump()
		self.assertEqual(cs.sampler.get_total(1),1)
		
		#self.assertTrue(cs.sample_context(0)==((),()))
		#c4 = cs.sample_context(4)
		#self.assertTrue(len(c4[0]) + len(c4[1]) == 4)

	def test_look_at_distribution_of_nt(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		parser = earleyparser.EarleyParser(grammar)
		d = cfgfcp.look_at_distribution_of_nt(grammar, parser, "S", 10)
		self.assertTrue(d < 10)

	def test_intersect_contexts_of_strings(self):
		"""
		Test that we can intersect the contexts of a set of strings correctly.
		"""
		grammar = cfg.load_from_file("../data/cfgs/abab2.cfg")
		parser = earleyparser.EarleyParser(grammar)
		w1 = ("a1","b1")
		w2 = ("a1", "a1", "b1","b1")
		w3 = ("a1",  "b1","b1")
		w4 = ("a1", "a1", "b1","b1", "b1", "b1")

		# contexts = cfgfcp.intersect_strings(grammar, [w1,w2], parser, 20)
		# # all of these contexts should be of the form (A^n, B^n)
		# for l,r in contexts:
		# 	self.assertEqual(len(l),len(r))
		# contexts2 = cfgfcp.intersect_strings(grammar, [w3,w4], parser, 20)
		# # all of these contexts should be of the form (A^n, B^n)
		# for l,r in contexts2:
		# 	self.assertEqual(2* len(l),len(r))

	def test_fkp_strong_fkp_strings(self):
		"""
		Test whether given strings characterise a given nonterminal.
		"""
		grammar = cfg.load_from_file("../data/cfgs/abab2.cfg")
		parser = earleyparser.EarleyParser(grammar)
		w1 = ("a1","b1")
		w2 = ("a1", "a1", "b1","b1")
		w3 = ("a2", "b2")
		nonterminal = "O"
		#self.assertTrue(cfgfcp.test_strong_fkp_strings(grammar, parser, nonterminal, [w1,w2], 100))
		#self.assertFalse(cfgfcp.test_strong_fkp_strings(grammar, parser, nonterminal, [w1,w3], 100))

	def test_fkp_strong_1nt(self):
		"""
		Test finding strings for a given NT.
		"""
		grammar = cfg.load_from_file("../data/cfgs/abab2.cfg")
		parser = earleyparser.EarleyParser(grammar)
		sampler = uniformsampler.UniformSampler(grammar, 100)
		k = 2
		n = 5
		nonterminal = "O"
		#(good,bad) = cfgfcp.test_strong_fkp_nt(grammar, parser, sampler, nonterminal, k, n)
		#self.assertTrue(good > 0)
		#print (good,bad)
	
	def test_smart_infix(self):
		grammar = cfg.load_from_file("../data/cfgs/abab2.cfg")
		# sample from the ones that don't have
		w1 = ("a1","b1")
		nonterminal = "O"
		ig = grammar.infix_grammar_without_nt(w1, nonterminal)
		self.assertTrue(len(ig.nonterminals) > 0)
		sampler = uniformsampler.UniformSampler(ig,20)
		self.assertEqual(sampler.get_total(3), 2)

	def test_one_fkp_nt_string_exact1(self):
		grammar = cfg.load_from_file("../data/cfgs/abab2.cfg")
		nonterminal = "O"
		w = ("a1","b1")
		self.assertFalse(cfgfcp.test_one_fkp_nt_string_exact(grammar, nonterminal, w))

	def test_one_fcp_nt_context_exact1(self):
		grammar = cfg.load_from_file("../data/cfgs/abab2.cfg")
		nonterminal = "O"
		context = (("a1",),("b1",))
		self.assertFalse(cfgfcp.test_one_fcp_nt_context_exact(grammar, nonterminal, context))

	def test_one_fcp_nt_context_exact2(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		nonterminal = "S"
		context = (("ax",),("bx",))
		self.assertTrue(cfgfcp.test_one_fcp_nt_context_exact(grammar, nonterminal, context))


	def test_one_fkp_nt_string_exact2(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		nonterminal = "S"
		w = ("ax","bx")
		self.assertTrue(cfgfcp.test_one_fkp_nt_string_exact(grammar, nonterminal, w))

	def test_one_fkp_nt_string_exact3(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg5.cfg")
		nonterminal = "S"
		w = ("ax","bx")
		self.assertFalse(cfgfcp.test_one_fkp_nt_string_exact(grammar, nonterminal, w))

	def test_full_1fkp_exact(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		self.assertTrue(cfgfcp.test_one_fkp_exact(grammar, 1))

	def test_full_1fkp_exact2(self):
		grammar = cfg.load_from_file("../data/cfgs/abab2.cfg")
		self.assertFalse(cfgfcp.test_one_fkp_exact(grammar, 10))

	def test_full_1fkp_exact3(self):
		grammar = cfg.load_from_file("../data/cfgs/atwice.cfg")
		self.assertTrue(cfgfcp.test_one_fkp_exact(grammar, 10))

	def test_context_sampler1(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg6.cfg")
		us = uniformsampler.UniformSampler(grammar,5)
		cs = uniformsampler.ContextSampler(grammar,us,5)
		self.assertEqual(cs.index["B"][0],0)
		self.assertEqual(cs.index["S"][0],1)
		self.assertEqual(cs.index["B"][2],3)
		context0 = cs.sample_context("S",0)
		self.assertEqual(context0, ((),()))
		for i in xrange(100):
			l,r = cs.sample_context("B",2)
			#print l, "---", r
			self.assertEqual(len(l) + len(r),2)


	def test_full_1fcp_exact(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		self.assertTrue(cfgfcp.test_one_fcp_exact(grammar, 1))

	def test_full_1fcp_exact2(self):
		grammar = cfg.load_from_file("../data/cfgs/abab2.cfg")
		self.assertFalse(cfgfcp.test_one_fcp_exact(grammar, 10))

	def testconvert_cfg_lengths(self):
		grammar = cfg.load_from_file("../data/cfgs/cfg1.cfg")
		count = 100
		length_distribution = [0,1,0,10,0,10,0]
		pcfg = generatepcfg.convert_cfg_lengths(grammar, length_distribution, count)
		el = pcfg.isConsistent()
		self.assertTrue(el < 5 and el > 3)