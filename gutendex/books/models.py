from collections import OrderedDict
from django.db import models

<<<<<<< HEAD
import math
=======
from scipy.spatial.distance import cosine, jaccard, dice

>>>>>>> book_rec
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
    tokens = models.ManyToManyField('Token', through='Posting')
    euclidian_sim = models.ManyToManyField('self', through='Euclidean',
                                           symmetrical=False,
                                           related_name='euclidean_of')
    correlation_sim = models.ManyToManyField('self', through='Correlation',
                                             symmetrical=False,
                                             related_name='correlation_of')

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
        )
        query_vector, book_vector = utils.get_transformed_vector(
            query_postings, query, transformation
        )

        return 1 - cosine(query_vector, book_vector)

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
        return 1 - jaccard(query_vector, book_vector)

    def dice_coefficient(self, query, transformation='tfidf'):
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
        return self.title


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

class Token(models.Model):
    name = models.CharField(max_length=128, unique=True)
    df = models.PositiveIntegerField(default=0)
    total_occurances = models.PositiveIntegerField(default=0)

    @property
    def idf(self):
        return math.log(Book.objects.count() / self.df, 2)

    def __str__(self):
        return self.name

class Euclidean(models.Model):
    book_1 = models.ForeignKey('Book', related_name='book1_euc+')
    book_2 = models.ForeignKey('Book', related_name='book2_euc+')
    distance = models.FloatField(default=0)

class Correlation(models.Model):
    book_1 = models.ForeignKey('Book', related_name='book1_corr+')
    book_2 = models.ForeignKey('Book', related_name='book2_corr+')
    distance = models.FloatField(default=0)

