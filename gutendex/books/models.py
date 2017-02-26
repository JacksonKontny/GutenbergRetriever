from django.db import models


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

