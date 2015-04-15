Project that search documents using query terms and returns the most relevant
documents.  Also implements the ability to search depending on a given document's
context.  For example "java" may have a different meaning if you have a document
about Indonesia, compared to if you have a document about computer science

The code is broken down into 2 python files.
index.py is used to build inverted indexes from data files
qry.py is used to query the index files created from index.py

-wiki.txt contains the documents the program searches and index is created from.  
          Each line starts with document title proceeded by all the words in the
          document
-in and in2 contain some queries that can be passed to qry.py
-apache contains files that were used to add "context" to queries. Querying
        the wiki collection using one of those files could add certain special
        meanings to words

First must build inverted index:
>> python index.py "name of txt data file" "name of index to create"

From there the code runs as follows:
- The data file is processed into a collection of document vectors of term 
	frequencies
- An index is created of document vectors with tfidf scores as specified
- The index is then inverted into term vectors with tfidf scores for each document
- The inverted index is then saved to file using shelve


To query the index:
Either pass queries, one per line
>> python qry.py "name of index file" "number of results to return" < "query text file"

or queries can be entered from prompts:
>> python qry.py "name of index file" "number of results to return"
where each time you will be prompted to provide a query with
"Enter query or EOF:"
To terminate you need to provide it with the EOF character
In Windows this is Ctrl+Z or Ctrl+D for Unix

Code is then implemented in following steps:
- Breaks query into terms and weights them as was specified
- It finds candidate documents where at least one query term occurs
- Then for each query term, scores for candidate documents are added together
- Returns the top number of documents and scores specified in input
- Prints results to command line


To create a pivot normalised inverted index, use the -p flag:
>> python index.py -p "value of s" "name of txt data file" "name of index to create"
s must be in range of (0,1] and will give an error otherwise

-a will return results only where all query terms have appeared in the document
>> python qry.py -a "name of index file" "number of results to return"

Using Rocchio's algorithm for PRF to add context to queries
It is implemented in qry.py using the -r flag:
>> python qry.py -r "name of forum file" "name of index file" "number of results to return"
Forum files (the context the queries are given from) are found in the apache folder

Rocchio requires a few more parameters so it will also prompt the user for 
these extra parameters.  These include:
- pivot: value of s for pivoted normalisation of forum index
- depth: how many documents to retrieve in original query
- number of terms: how many of the top terms to exapand query by
- alpha: weight of original query in expanded query
- beta: weight of psuedo average document in expanded query

An index for the forum is created at query time.  This can be done thanks to
the forum pages been much smaller than the wikipedia dataset.

For best result I set following parameters:
- pivot = 0.5
- depth = 5
- number of terms = 20
- alpha = 0.1
- beta = 0.9

Some of these values might be interesting.
20 produced best results for number of terms to add.  It's enough to add a good
amount of context but more than that and the terms start becoming to general 
and lose meaning.  This also restricts the size of the query whereas when I 
tried to run the expanded query with all the terms it took too long to run.

For setting alpha and beta I initially set them both to 0.5.  What I found is 
the original query term overpowered everything else since the weighting of each
term in a query was log(1 + fqt) which meant each term at smallest gets a score
of log(2).  Comparing this to terms from the retrieved documents whose scores 
were tfidf which were far less smaller.  So the original query had to be 
severely downweighted hence my chosen values.