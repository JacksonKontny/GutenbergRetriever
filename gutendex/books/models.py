from django.db import models

import math

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

    def magnitude(self):
        """ Get the magnitude of this book's term vector

            Magnitude is the sum of the squares of all terms that belong to
            this book.
        """
        return utils.get_magnitude(self.posting.values_list('tf', flat=True))

    def query_dot_product(self, query, transformation=None):
        """ Get the dot product of the input query and this book's term
            frequency vector
        """
        # If no transformation offered, just return the same value as passed in
        if not transformation:
            transformation = lambda x: x

        # query = transformation(query)

        # obtain this document's postings that pertain to query tokens
        postings = self.posting.objects.filter(token__name__in=query.keys())
        dot_product = 0
        for posting in postings:
            dot_product += posting.tf * query[posting.token.name]
        return dot_product

    def cosine_distance(self, query, transformation=None):
        """ Return the cosine distance between a query and the book's term
            frequency vector.

            Cosine distance is the dot product of the query and the book
            divided by the product of the magnitude of the query and the book
        """

        return (
            self.query_dot_product(query, transformation=transformation)
            /
            self.magnitude * utils.get_magnitude(query.values())
        )

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
