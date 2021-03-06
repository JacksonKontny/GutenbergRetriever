import xml.etree.ElementTree as parser
import math
import os
import re
import string
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import Counter, OrderedDict
from decimal import Decimal

from books import models

LINE_BREAK_PATTERN = re.compile(r'[ \t]*[\n\r]+[ \t]*')
NAMESPACES = {
    'dc': 'http://purl.org/dc/terms/',
    'dcam': 'http://purl.org/dc/dcam/',
    'pg': 'http://www.gutenberg.org/2009/pgterms/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
}


def fix_subtitles(title):
    """
    This formats subtitles with (semi)colons instead of new lines. The first
    subtitle is introduced with a colon, and the rest are introduced with
    semicolons.

    >>> fix_subtitles(u'First Across ...\r\nThe Story of ... \r\n'
    ... 'Being an investigation into ...')
    u'First Across ...: The Story of ...; Being an investigation into ...'
    """

    new_title = LINE_BREAK_PATTERN.sub(': ', title, 1)
    return LINE_BREAK_PATTERN.sub('; ', new_title)


def get_book(id, xml_file_path):
    """ Based on https://gist.github.com/andreasvc/b3b4189120d84dec8857 """

    # Parse the XML.
    document = None
    try:
        document = parser.parse(xml_file_path)
    except:
        raise Exception('The XML file could not be parsed.')

    # Get the book node.
    root = document.getroot()
    book = root.find('{%(pg)s}ebook' % NAMESPACES)

    result = {
        'id': int(id),
        'title': None,
        'authors': [],
        'type': None,
        'subjects': [],
        'languages': [],
        'formats': [],
        'downloads': None,
        'bookshelves': []
    }

    # Authors
    creators = book.findall('.//{%(dc)s}creator' % NAMESPACES)
    for creator in creators:
        author = {'birth': None, 'death': None}
        name = creator.find('.//{%(pg)s}name' % NAMESPACES)
        if name is None:
            continue
        author['name'] = safe_unicode(name.text, encoding='UTF-8')
        birth = creator.find('.//{%(pg)s}birthdate' % NAMESPACES)
        if birth is not None:
            author['birth'] = int(birth.text)
        death = creator.find('.//{%(pg)s}deathdate' % NAMESPACES)
        if death is not None:
            author['death'] = int(death.text)
        result['authors'] += [author]

    # Title
    title = book.find('.//{%(dc)s}title' % NAMESPACES)
    if title is not None:
        result['title'] = fix_subtitles(
            safe_unicode(title.text, encoding='UTF-8')
        )

    # Subjects
    result['subjects'] = set()
    for subject in book.findall('.//{%(dc)s}subject' % NAMESPACES):
        subject_type = subject.find('.//{%(dcam)s}memberOf' % NAMESPACES)
        if subject_type is None:
            continue
        subject_type = subject_type.get('{%(rdf)s}resource' % NAMESPACES)
        value = subject.find('.//{%(rdf)s}value' % NAMESPACES)
        value = value.text
        if subject_type in ('%(dc)sLCSH' % NAMESPACES):
            result['subjects'].add(value)
    result['subjects'] = list(result['subjects'])
    result['subjects'].sort()

    # Book Shelves
    result['bookshelves'] = set()
    for bookshelf in book.findall('.//{%(pg)s}bookshelf' % NAMESPACES):
        value = bookshelf.find('.//{%(rdf)s}value' % NAMESPACES)
        if value is not None:
            result['bookshelves'].add(value.text)
    result['bookshelves'] = list(result['bookshelves'])

    # Formats
    result['formats'] = {
        file.find('{%(dc)s}format//{%(rdf)s}value' % NAMESPACES).text:
        file.get('{%(rdf)s}about' % NAMESPACES)
        for file in book.findall('.//{%(pg)s}file' % NAMESPACES)
    }

    # Type
    book_type = book.find(
        './/{%(dc)s}type//{%(rdf)s}value' % NAMESPACES
    )
    if book_type is not None:
        result['type'] = book_type.text

    # Languages
    languages = book.findall(
        './/{%(dc)s}language//{%(rdf)s}value' % NAMESPACES
    )
    result['languages'] = [language.text for language in languages] or []

    # Download Count
    download_count = book.find('.//{%(pg)s}downloads' % NAMESPACES)
    if download_count is not None:
        result['downloads'] = int(download_count.text)

    return result


def safe_unicode(arg, *args, **kwargs):
    """ Coerce argument to Unicode if it's not already """
    return arg if isinstance(arg, str) else str(arg, *args, **kwargs)

def get_word_count(text, stem=True):
    stop_words = set(stopwords.words("english"))
    ps = PorterStemmer()
    for punc in string.punctuation:
        text = text.replace(punc, ' ')

    if not stem:
        words = text.lower().strip().split()
        return Counter(words)
    words = text.strip().split()

    stemmed_words = []
    for w in words:
        try:
            w = ps.stem(w)
            if w.lower() not in stop_words and w.isalpha():
                stemmed_words.append(w)
        except IndexError:
            continue

    return Counter(stemmed_words)

def get_sum_of_squares(vector):
    """ Return the sum of the square of all terms in the input vector
    """
    return sum([term**2 for term in vector])

def get_magnitude(vector):
    """ Return the magnitude of a vector, the square root of the sum of the
        squares
    """
    return math.sqrt(get_sum_of_squares(vector))

def get_mean(vector):
    """ Return the mean (float) of all terms in the input vector """
    return float(sum(vector))/float(len(vector))

def get_std(vector):
    """ Return the standard deviation (float) of the input vecotr """
    sum_of_square_of_diff = sum([(term - get_mean(vector))**2 for term in vector])
    return math.sqrt(sum_of_square_of_diff/float(len(vector)))

def get_corr(vector1, vector2):
    """ Return the correlation (float) of the input vectors """

    if len(vector1) != len(vector2):
        raise Exception("Input vectors have to be the same size.")

    x_mean = get_mean(vector1)
    y_mean = get_mean(vector2)

    n = len(vector1)

    sum_xy = 0
    for i in range(n):
        sum_xy += (vector1[i]-x_mean) * (vector2[i]-y_mean)

    x_std = get_std(vector1)
    y_std = get_std(vector2)

    return 1 - (sum_xy/(x_std*y_std))/(n - 1)

def get_minkowski(vector1, vector2, power):
    """ Return the minkowski distance between the input vectors
        power = 1: manhattan
        power = 2: euclidean
        power = inf: chebyshev
        more: https://en.wikipedia.org/wiki/Minkowski_distance
    """

    def nth_root(value, n_root):
        root_value = 1 / float(n_root)
        return Decimal(value) ** Decimal(root_value)

    if len(vector1) != len(vector2):
        raise Exception("Input vectors have to be the same size.")
    elif power < 1:
        raise ValueError("p must be at least 1")

    return nth_root(sum(pow(abs(a - b), power) for a, b in zip(vector1, vector2)), power)

def get_sparse_vector(postings_list):
    """ Takes a postings dictionary of {pk: value} pairs and returns a sparse
        vector for all tokens
    """
    sparse_dict = OrderedDict(
        zip(models.Token.objects.values_list('pk', flat=True),
            [0]*models.Token.objects.count())
    )
    for pk, value in postings_list.iteritems():
        sparse_dict[pk] = value

def create_postings(book, counter, tokenized=True):
    for word, count in counter.items():
        if not tokenized:
            token, created = models.Word.objects.get_or_create(
                name=word
            )
        else:
            token, created = models.Token.objects.get_or_create(
                name=word
            )
        token.total_occurances += count
        token.df += 1
        token.save()

        if tokenized:
            models.Posting.objects.update_or_create(
                book=book,
                token=token,
                defaults={'tf': count},
            )
        else:
            models.WordPosting.objects.update_or_create(
                book=book,
                word=token,
                defaults={'tf': count},
            )


def get_transformed_vector(query_postings, query, transformation):
    if transformation == 'tfidf':
        query_vector, book_vector = get_tfidf_vectors(
            query_postings, query
        )
    elif transformation == 'binary':
        query_vector, book_vector = (
            get_binary_vectors(query_postings, query)
        )
    else:
        query_vector, book_vector = (
            get_tf_vectors(query_postings, query)
        )
    return query_vector, book_vector

def get_tfidf_vectors(query_postings, query):
    new_query = {}
    for posting in query_postings:
        token_name = posting.token.name
        new_query[token_name] = query[token_name] * posting.token.idf

    # Get vector of query ordered by token name
    query_vector = [x[1] for x in sorted(new_query.items())]
    book_vector = [
        x.tfidf for x in query_postings.order_by('token__name')
    ]
    return query_vector, book_vector

def get_tf_vectors(query_postings, query):
    ordered_postings = query_postings.order_by(
        'token__name'
    )
    book_vector = ordered_postings.values_list('tf', flat=True)
    book_terms = ordered_postings.values_list('token__name', flat=True)
    query_vector = [x[1] for x in sorted(query.items()) if x[0] in book_terms]
    return query_vector, book_vector

def get_binary_vectors(query_postings, _):
    book_vector_length = query_postings.count()
    book_vector = query_vector = [1] * book_vector_length
    return query_vector, book_vector
