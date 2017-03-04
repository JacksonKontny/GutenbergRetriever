from django.db import models

import math


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
