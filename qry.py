import sys
import shelve
import index
import math
from operator import itemgetter
from sys import stdin
import argparse

def weight_query(query):
	"""Weights each term in the query"""
	qvec = {}
	for term in query:
		if term in qvec:
			qvec[term] += 1
		else:
			qvec[term] = 1
	for (term, freq) in qvec.iteritems():
		qvec[term] = math.log(1 + float(freq))
	return qvec

def refine_search(idx, query, has_all):
	"""Finds a list of candidate docs for the query"""
	"""Question 4 is implemented here"""
	doc_freq = {}
	for term in query:
		if term in idx:
			for doc in idx[term]:
				if doc in doc_freq:
					doc_freq[doc] += 1
				else:
					doc_freq[doc] = 1
	if has_all:
		doc_list = []
		for (doc, freq) in doc_freq.iteritems():
			if freq == len(query):
			 	doc_list.append(doc)
	else:
		doc_list = doc_freq.keys()
	init_dict = {}
	for doc in doc_list:
		init_dict[doc] = 0
	return init_dict

def query_index(idx, num_results, qvec, has_all, query):
	"""Queries the index with qvec and return top num_results"""
	results = refine_search(idx, query, has_all)
	print len(results)
	for (term, weight) in qvec.iteritems():
		if term in idx:
			for doc in results:
				if doc in idx[term]:
					results[doc] += weight*idx[term][doc]
	return sorted(results.iteritems(), key=itemgetter(1), reverse=True)[:num_results]

def print_results(results):
	"""Prints out the top results"""
	for (title, score) in results:
		print "%s %.6f" % (title, score)
	print "\n"

def average_doc(docs, idx):
	"""Finds the average doc from docs"""
	dvec = {}
	for (doc, _) in docs:
		for (term, score) in idx[doc].iteritems():
			if term in dvec:
				dvec[term] += score
			else:
				dvec[term] = score
	for term in dvec:
		dvec[term] /= len(docs)
	return dvec

def add_query_feedback(qvec, dvec, alpha, beta):
	"""Creates a query vector according to rocchio's algorithm"""
	qe = {}
	for (term, score) in qvec.iteritems():
		qe[term] = score*alpha
	for (term, score) in dvec.iteritems():
		if term in qe:
			qe[term] += score*beta
		else:
			qe[term] = score*beta
	return qe

def expand_query(query, inv_idx, depth, has_all, alpha, beta, idx, num_terms):
	"""Expands the query using rocchio's algorithm"""
	qvec = weight_query(query)
	results = query_index(inv_idx, depth, qvec, has_all, query)
	dvec = average_doc(results, idx)
	expanded = add_query_feedback(qvec, dvec, alpha, beta)
	top_terms = sorted(expanded.iteritems(), key=itemgetter(1), reverse=True)[:(num_terms+1)]
	optimised_qe = {}
	for (term, score) in top_terms:
		optimised_qe[term] = score
	return optimised_qe

def get_input(msg, type_):
	"""Prompts the user for input of a certain type"""
	while True:
		print msg
		value = stdin.readline()
		try:
			value = type_(value)
			break
		except:
			print "Please enter a %s" % type_
	return value

def setup_rocc():
	"""Set the parameters to perform rocchio's algorithm"""
	while True:
		pivot = get_input("Enter pivot value for context index:", float)
		if pivot<=0 or pivot>1:
			print "Please enter float between (0,1]"
		else:
			break
	bow = index.parse_wiki_coll(args.rocc)
	context_idx = index.bow_to_idx(bow, pivot)
	context_inv_idx = index.invert_index(context_idx)
	while True:
		depth = get_input("How many documents to expand query by?", int)
		if depth <= 0:
			print "Please enter a positive integer"
		else:
			break
	while True:
		expand_num = get_input("How many terms to expand query by?", int)
		if expand_num <=0:
			print "Please enter a positive integer"
		else:
			break
	alpha = get_input("Enter alpha:", float)
	beta = get_input("Enter beta:", float)
	return [context_idx, context_inv_idx, depth, expand_num, alpha, beta]

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("index_fname", help="name of index file")
	parser.add_argument("num_results", type=int, help="top number of results to return")
	parser.add_argument("-a", "--all", action="store_true", help="Results contain all query terms")
	parser.add_argument("-r", "--rocc", "--rocchio", help="Adds context to the query from file /ROCC/")
	args = parser.parse_args()

	if args.rocc == None:
		context = False
	else:
		context = True
		[context_idx, context_inv_idx, depth, expand_num, alpha, beta] = setup_rocc()

	idx = shelve.open(args.index_fname)
	while True:
		print "Enter query or EOF:"
		query = stdin.readline()
		if query == "":
			break
		print "Query: %s" % query
		query = query.lower().split()
		if context:
			qvec = expand_query(query, context_inv_idx, depth, args.all, alpha, beta, context_idx, expand_num)
		else:
			qvec = weight_query(query)
		results = query_index(idx, args.num_results, qvec, args.all, query)
		print_results(results)
	idx.close()