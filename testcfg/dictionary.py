# Code for generating random words for use in randomly generated grammars

import random
import math

def generateRandomString(n):
	"""generate a random string of lower case letters of length n"""
	myString = ""
	for i in range(n):
		a = random.randint(0,25)
		letter = chr(ord('a') + a)
		myString += letter
	return myString

def generateDictionary(n):
	""" Generate a list of n tokens that can be used to be 
	words in a synthetic example"""
	# compute how long the words should be
	length = int(math.ceil(math.log10(n)))
	dictionary = set()
	count = 0
	while len(dictionary) < n :
		newWord = generateRandomString(length)
		count = count + 1
		if not newWord in dictionary:
			dictionary.add(newWord)
#	print count, " iterations for ", n 
	return dictionary

def dumpDictionary(dict):
	for word in dict:
		print word

if __name__ == '__main__':
	dict = generateDictionary(1000)
	dumpDictionary(dict)


