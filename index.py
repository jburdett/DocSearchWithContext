# Converts BOW object into an inverted index
import math
import shelve
import argparse
import sys

def parse_wiki_coll(fname):
    """Parse a wiki data file into a collection.
    Fname is the file name of the wiki data file.  The parsed collection
    is returned."""
    coll = {}
    for line in open(fname):
        if line == None:
            sys.stderr.write("File error: No content found.\n")
            sys.exit()            
        line = line.strip().split()
        doc_name = line[0]
        coll[doc_name] = {}
        for token in line[1:]:
            if token in coll[doc_name]:
            	coll[doc_name][token] += 1
            else:
            	coll[doc_name][token] = 1
    return coll

def calc_idf(bow):
	"""Calculates IDF scores for terms in the collection"""
	ft = {}
	for doc in bow:
		for (term, _) in bow[doc].iteritems():
			if term in ft:
				ft[term] += 1
			else:
				ft[term] = 1
	idf = {}
	for term in ft:
		idf[term] = math.log(float(len(bow)) / ft[term])
	return idf

"""Redundant since pivot normalisation does both when s defaults to 1"""
"""Made during Question 1"""
# def normalise(tfidf):
# 	"""Normalises the docvecs"""
# 	for doc in tfidf:
# 		length = 0
# 		for score in tfidf[doc].values():
# 			length += score**2
# 		length = math.sqrt(length)
# 		for term in tfidf[doc]:
# 			tfidf[doc][term] /= length
# 	return tfidf

def pivot_normalise(tfidf, s, num_docs):
	"""Normalises the tfidf scores"""
	"""Implements Question 3"""
	lengths = {}
	total_length = 0
	for doc in tfidf:
		doc_length = 0
		for score in tfidf[doc].values():
			doc_length += score**2
		doc_length = math.sqrt(doc_length)
		lengths[doc] = doc_length
		total_length += doc_length

	for doc in tfidf:
		for term in tfidf[doc]:
			tfidf[doc][term] /= (1-s)*total_length/num_docs + s*lengths[doc]
	return tfidf

def bow_to_idx(bow, s):
	"""Convert the BOW object to an index"""
	tfidf = {}
	idf = calc_idf(bow)
	for doc in bow:
		tfidf[doc] = {}
		for (term, freq) in bow[doc].iteritems():
			tfidf[doc][term] = math.log(1 + float(freq)) * idf[term]
	# norm_tfidf = normalise(tfidf)
	norm_tfidf = pivot_normalise(tfidf, s, len(bow))
	return norm_tfidf

def invert_index(idx):
	"""Converts the doc-term index to a term-doc index"""
	inv = {}
	for doc in idx:
		for (term, score) in idx[doc].iteritems():
			if term in inv:
				inv[term][doc] = score
			else:
				inv[term] = {doc : score}
	return inv

def store_index(inv, fname):
	"""Stores the inverted index as a shelve file"""
	index = shelve.open(fname)
	for (term, scores) in inv.iteritems():
		index[term] = scores
	index.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("wiki_fname", help="name of wiki data file")
	parser.add_argument("index_fname", help="name of destination of index")
	parser.add_argument("-p", "--pivot", type=float, default=1.0, help="Use pivoted length normalization")
	args = parser.parse_args()
	if args.pivot <= 0 or args.pivot > 1:
		sys.stderr.write("%s must be within range of (0.0,1.0)\n" % args.pivot)
		sys.exit()

	bow = parse_wiki_coll(args.wiki_fname)
	idx = bow_to_idx(bow, args.pivot)
	inv_idx = invert_index(idx)
	store_index(inv_idx, args.index_fname)