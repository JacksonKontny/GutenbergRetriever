import math
from books import models
from collections import Counter

query = "books about Lincoln speech"

# create a HashMapVector, Q, for the query
q_tokens = Counter(query.split())

# for each token, T, in Q:
# Let I be the IDF of T, and K be the count of T in Q:
# Set the weight of T in Q: W = freq * I
for tok, freq in q_tokens.items():
	df = models.Token.objects.first(
		name = tok
		).df
	I = math.log(models.Book.objects.count() / df, 2)
	W = freq * I                      # calculate weight
	q_tokens[tok]['W'] = W            # store weight

# Let L be the list of TokenOccurences of T from database

