from collections import OrderedDict

import math

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from scipy.spatial.distance import cosine, jaccard, dice

from books import utils


class Author(models.Model):
    birth_year = models.SmallIntegerField(blank=True, null=True)
    death_year = models.SmallIntegerField(blank=True, null=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Book(models.Model):
    authors = models.ManyToManyField('Author')
    bookshelves = models.ManyToManyField('Bookshelf')
    download_count = models.PositiveIntegerField(blank=True, null=True)
    gutenberg_id = models.PositiveIntegerField(unique=True)
    languages = models.ManyToManyField('Language')
    media_type = models.CharField(max_length=16)
    subjects = models.ManyToManyField('Subject')
    title = models.CharField(blank=True, max_length=1024, null=True)
    text = models.TextField(blank=True)
    is_parsed = models.BooleanField(default=False)
    has_word_vector = models.BooleanField(default=False)
    tokens = models.ManyToManyField('Token', through='Posting')
    distance = models.ManyToManyField('self', through='Distance',
                                           symmetrical=False,
                                           related_name='distance_to')

    @property
    def sparse_tfidf_vector(self):
        """ Return this book's sparse term frequency vector
        """
        sparse_dict = OrderedDict(
            zip(Token.objects.values_list('pk', flat=True),
                [0]*Token.objects.count())
        )
        for posting in self.posting_set.all().select_related('token'):
            sparse_dict[posting.token.pk] = posting.tfidf

        return [x[1] for x in sparse_dict.items()]

    @property
    def tfidf_dict(self):
        """ Return this book's sparse term frequency vector
        """
        posting_dict = {}
        for posting in self.posting_set.all().select_related('token'):
            posting_dict[posting.token.pk] = posting.tfidf

        return posting_dict

    @property
    def sum_of_squares(self):
        """ Get the sum of the squared terms
        """
        return utils.get_sum_of_squares(
            self.posting_set.values_list('tf', flat=True)
        )

    @property
    def magnitude(self):
        """ Get the magnitude of this book's term vector

            Magnitude is the sum of the squares of all terms that belong to
            this book.
        """
        return utils.get_magnitude(
            self.posting_set.values_list('tf', flat=True)
        )

    def query_dot_product(self, query, transformation=None):
        """ Get the dot product of the input query and this book's term
            frequency vector
        """
        # If no transformation offered, just return the same value as passed in
        if not transformation:
            transformation = lambda x: x

        # query = transformation(query)

        # obtain this document's postings that pertain to query tokens
        postings = self.posting_set.filter(
            token__name__in=query.keys()
        )
        dot_product = 0
        for posting in postings:
            dot_product += posting.tf * query[posting.token.name]
        return dot_product

    def cosine_distance(self, query, transformation='tfidf'):
        """ Return the cosine distance between a query and the book's term
            frequency vector.

            Dices coefficient is two times the dot product of the query and the
            book divided by the sum of the squared terms of each book
        """
        query_postings = self.posting_set.filter(
            token__name__in=query.keys()
        ).distinct()
        query_vector, book_vector = utils.get_transformed_vector(
            query_postings, query, transformation
        )

        return cosine(query_vector, book_vector)

    def jaccard_distance(self, query, transformation='tfidf'):
        """ Return the jaccard distance between a query and the book's term
            frequency vector.

            jaccard distance is the dot product of the query and the book
            divided by the sum of all squared terms in both the query and the
            book minus the original dot product

            jaccard =
            dot(query, book)
            /
            ((sum of book squared terms + sum of query squared terms) - dot(query, book))
        """
        query_postings = self.posting_set.filter(
            token__name__in=query.keys()
        )
        query_vector, book_vector = utils.get_transformed_vector(
            query_postings, query, transformation
        )
        return jaccard(query_vector, book_vector)

    def dice_distance(self, query, transformation='tfidf'):
        """ Return the dice coefficient between a query and the book's term
            frequency vector.

            the Dice coefficient is 2 times the dot product of the query and the book
            divided by the sum of all squared terms in both the query and the book

            Dice =
            2 * dot(query, book)
            /
            (sum of book squared terms + sum of query squared terms)
        """
        query_postings = self.posting_set.filter(
            token__name__in=query.keys()
        )
        query_vector, book_vector = utils.get_transformed_vector(
            query_postings, query, transformation
        )
        return 1 - dice(query_vector, book_vector)

    def get_formats(self):
        return Format.objects.filter(book_id=self.id)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return 'No Title'


class Bookshelf(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


class Format(models.Model):
    book = models.ForeignKey('Book')
    mime_type = models.CharField(max_length=32)
    url = models.CharField(max_length=256)


class Language(models.Model):
    code = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return self.code


class Subject(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

class Posting(models.Model):
    book = models.ForeignKey('Book')
    token = models.ForeignKey('Token')
    tf = models.PositiveIntegerField(default=0)

    @property
    def tfidf(self):
        return self.tf * self.token.idf

    class Meta:
        unique_together = (
            ('book', 'token'),
        )

class WordPosting(models.Model):
    book = models.ForeignKey('Book')
    word = models.ForeignKey('Word')
    tf = models.PositiveIntegerField(default=0)

    @property
    def tfidf(self):
        return self.tf * self.token.idf

    class Meta:
        unique_together = (
            ('book', 'word'),
        )

class Token(models.Model):
    name = models.CharField(max_length=128, unique=True)
    df = models.PositiveIntegerField(default=0)
    total_occurances = models.PositiveIntegerField(default=0)

    @property
    def idf(self):
        return math.log(Book.objects.count() / self.df, 2)

    def __str__(self):
        if self.name:
            name = self.name
        else:
            name = 'None'
        return 'Token: {}'.format(name)

class Word(models.Model):
    name = models.CharField(max_length=128, unique=True)
    df = models.PositiveIntegerField(default=0)
    total_occurances = models.PositiveIntegerField(default=0)

    @property
    def idf(self):
        return math.log(Book.objects.count() / self.df, 2)

    def __str__(self):
        if self.name:
            name = self.name
        else:
            name = 'None'
        return 'Word: {}'.format(name)


class Sentence(models.Model):
    book = models.ForeignKey('Book')
    index = models.PositiveIntegerField()
    compound = models.FloatField(default=0)
    pos = models.FloatField(default=0)
    neg = models.FloatField(default=0)
    neu = models.FloatField(default=0)


class Distance(models.Model):
    book_1 = models.ForeignKey('Book', related_name='book1_distance+')
    book_2 = models.ForeignKey('Book', related_name='book2_distance+')
    distance = models.FloatField(default=0)
    distance_type = models.ForeignKey('DistanceType')

    def __str__(self):
        return '{} - {}, {}: {}'.format(
            self.book_1, self.book_2, self.distance_type, self.distance
        )

    class Meta:
        unique_together = (
            ('book_1', 'book_2', 'distance_type'),
        )

class DistanceType(models.Model):
    COSINE='cosine'
    EUCLIDEAN='euclidean'
    PEARSON='pearson'
    JACCARD='jaccard'
    DICE='dice'

    code = models.CharField(max_length=64)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Cluster(models.Model):
    POLARITY = 'polarity'
    TOKENS = 'tokens'
    WORDS = 'words'

    book = models.ForeignKey('Book')
    n_clusters = models.SmallIntegerField()
    n = models.SmallIntegerField()
    clustered_on = models.CharField(max_length=64)

    class Meta:
        unique_together = (
            ('book', 'n_clusters', 'clustered_on'),
        )

class Euclidean(models.Model):
    book_1 = models.ForeignKey('Book', related_name='book1_euc+')
    book_2 = models.ForeignKey('Book', related_name='book2_euc+')
    distance = models.FloatField(default=0)

class Correlation(models.Model):
    book_1 = models.ForeignKey('Book', related_name='book1_corr+')
    book_2 = models.ForeignKey('Book', related_name='book2_corr+')
    distance = models.FloatField(default=0)

class BookRating(models.Model):
    book = models.ForeignKey('Book')
    user = models.ForeignKey(User)
    rating = models.SmallIntegerField()
