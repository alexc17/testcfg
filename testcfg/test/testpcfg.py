import unittest
import pcfg
import partitionfunction
import inside
import math
import testfcp

#testcode for pcfgs

class PcfgTest(unittest.TestCase):

	def test_load(self):
		"""
		Test that it can load a file correctly.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/pcfg1.pcfg")

		self.assertEqual(len(grammar.terminals), 5)
		self.assertEqual(len(grammar.nonterminals), 1)


	def test_inside(self):
		grammar = pcfg.load_from_file("../data/pcfgs/pcfg1.pcfg")
		w = ['ax','c','bx']
		lp = inside.compute_log_inside_prob(grammar,w)
		predicted_value = math.log( 14.0/ 121.0)
		self.assertTrue(lp < 0.0)
		self.assertAlmostEqual(lp,predicted_value)


	def test_inside_unary(self):
		grammar = pcfg.load_from_file("../data/pcfgs/unary.pcfg")
		w = ['a']
		lp = inside.compute_log_inside_prob(grammar,w)
		predicted_value = 0
		self.assertAlmostEqual(lp,predicted_value)

	def test_inside2(self):
		grammar = pcfg.load_from_file("../data/pcfgs/pcfg7.pcfg")
		w = ['c']
		lp = inside.compute_log_inside_prob(grammar,w,"A")
		predicted_value = 0
		self.assertAlmostEqual(lp,predicted_value)

	def test_partition_function(self):
		grammar = pcfg.load_from_file("../data/pcfgs/pcfg1.pcfg")
		p = partitionfunction.compute_partition_function(grammar, 100)
		self.assertAlmostEqual(p,1.0)

	def test_partition_function2(self):
		grammar = pcfg.load_from_file("../data/pcfgs/inconsistent1.pcfg")
		p = partitionfunction.compute_partition_function(grammar, 100)
		self.assertAlmostEqual(p,0.5)

	def test_partition_function_improper(self):
		grammar = pcfg.load_from_file("../data/pcfgs/improper.pcfg",normalise=False)
		p = partitionfunction.compute_partition_function(grammar, 100)
		self.assertAlmostEqual(p,0.5)

	def test_infix_probability(self):
		"""
		Test the computation of infix probabilities.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/abab2.pcfg")
		s1 = ("a","b")
		ig = grammar.construct_infix_grammar(s1)
		self.assertTrue(ig)

	def test_context_probability1(self):
		"""
		Test the context probability.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/pcfg2.pcfg")
		context = (('ax',),())
		p = grammar.compute_context_probability(context)
		predicted_value = 2.0/9.0
		self.assertAlmostEqual(p,predicted_value)


	def test_context_probability2(self):
		"""
		Test the context probability.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/pcfg1.pcfg")
		context = (('ax',),('bx',))
		p = grammar.compute_context_probability(context)
		predicted_value = 2.0/11.0
		self.assertAlmostEqual(p,predicted_value)

	def test_sample_from_context(self):
		"""
		Check that we can sample from all strings having a given context correctly.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/pcfg1.pcfg")
		ol = grammar.isConsistent()
		context = (('ax','ax'),())
		cg = grammar.construct_context_grammar(context)
		#print "grammar constructed"
		expected_length = cg.isConsistent()
		self.assertAlmostEqual(ol + 4, expected_length)


	def test_nullary(self):
		"""
		Test the computation of nullary probabilities.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/nullary1.pcfg")
		z = grammar.compute_nullary()
		self.assertAlmostEqual(z['S'],0.5)
		self.assertAlmostEqual(z['A'],1.0)
		self.assertAlmostEqual(z['B'],0.0)

	def test_unary1(self):
		"""
		Test computation of unary probs.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/unary1.pcfg")
		#grammar.dump()
		z = grammar.compute_nullary()
		u = grammar.compute_unary(z)
		atoa = u["A"]["A"]
		stoa = u["A"]["S"]
		self.assertAlmostEqual(atoa, 2.0)
		self.assertAlmostEqual(stoa, 1.0)
		
	def test_unary2(self):
		"""
		Test computation of unary probs, with nullary.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/unary2.pcfg")
		#grammar.dump()
		z = grammar.compute_nullary()
		self.assertAlmostEqual(1.0, z["Z"])
		u = grammar.compute_unary(z)
		atoa = u["A"]["A"]
		stoa = u["A"]["S"]
		self.assertAlmostEqual(atoa, 2.0)
		self.assertAlmostEqual(stoa, 1.0)
		
	def test_insider_nullary(self):
		"""
		Test computation of unary probs, with nullary.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/unary2.pcfg")
		#grammar.dump()
		lp = inside.compute_log_inside_prob(grammar,['a'])	
		predicted_value = math.log(0.25)
		self.assertAlmostEqual(lp,predicted_value)		

	def test_insider_nullary2(self):
		"""
		Test computation of unary probs, with nullary.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/nullary2.pcfg")
		#grammar.dump()
		lp = inside.compute_log_inside_prob(grammar,['c'])	
		predicted_value = math.log(4.0/7.0)
		self.assertAlmostEqual(lp,predicted_value)	

	def test_insider_nullary3(self):
		"""
		Test computation of unary probs, with nullary.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/nullary3.pcfg")
		#grammar.dump()
		lp = inside.compute_log_inside_prob(grammar,['b', 'c'])	
		predicted_value = math.log(0.25)
		self.assertAlmostEqual(lp,predicted_value)	

	def test_nullaryF1(self):
		"""
		Test computation of unary probs, with nullary.
		"""
		for filename in ["../data/pcfgs/nullaryF1.pcfg","../data/pcfgs/nullaryF2.pcfg","../data/pcfgs/nullaryF3.pcfg"]:
			grammar = pcfg.load_from_file(filename)

			lp = inside.compute_log_inside_prob(grammar,['a'])	
			self.assertAlmostEqual(lp,0.0)	

	def test_fcp_intersection(self):
		"""
		Test the intersection code for contexts.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/large.normalised.pcfg")
		nonterminal = "NT1"
		c1 = ((),("lq",))
		c2 = (("gj",),("wi","va","xa"))
		contexts = [c1,c2]
		nsamples = 10
		#intersected = testfcp.intersect_contexts(grammar, contexts, nsamples)
		#self.assertEqual(len(intersected), nsamples )
		
	def test_fcp_nt1(self):
		"""
		Test the intersection code for contexts.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/large.normalised.pcfg")
		nonterminal = "NT1"
		nsamples = 10
		ncontexts = 100
		#self.assertTrue(testfcp.test_fcp_nt(grammar,2,nonterminal,ncontexts, nsamples))

	def test_fcp(self):
		"""
		Test the FCP for a 1 NT grammar.
		"""
		grammar = pcfg.load_from_file("../data/pcfgs/palindrome2.pcfg")
		k = 1
		ncontexts = 10
		nsamples = 10
		self.assertTrue(testfcp.test_fcp(grammar,k,ncontexts,nsamples))

	def test_fkp_1(self):
		grammar = pcfg.load_from_file("../data/pcfgs/abab2.pcfg")
		s1 = ("a","b")
		s2 = ("a","a","b","b")
		nonterminal = "O"
		nsamples = 10
		self.assertFalse(testfcp.test_kp_nt(grammar, nonterminal, [s1], nsamples))
		self.assertTrue(testfcp.test_kp_nt(grammar, nonterminal, [s1,s2], nsamples))

	def test_fkp_2(self):
		grammar = pcfg.load_from_file("../data/pcfgs/abab2.pcfg")
		s1 = ("a","b","b")
		s2 = ("a","a","b","b","b","b")
		nonterminal = "T"
		nsamples = 2
		self.assertTrue(testfcp.test_kp_nt(grammar, nonterminal, [s1,s2], nsamples))

if __name__ == '__main__':
    unittest.main()
