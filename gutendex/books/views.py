from django.conf import settings
from django.db.models import Q
from django.shortcuts import render
from django.views import View

from rest_framework import viewsets
from rest_framework.response import Response

from books import utils

from .models import *
from .serializers import *
from .forms import QueryForm


class AuthorViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows authors to be viewed. """
    queryset = Author.objects.all().order_by('birth_year')
    serializer_class = AuthorSerializer


class BookViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows books to be viewed. """

    lookup_field = 'gutenberg_id'

    queryset = Book.objects.all()
    queryset = queryset.order_by('-download_count')
    queryset = queryset.exclude(download_count__isnull=True)

    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = self.queryset

        author_year_end = self.request.GET.get('author_year_end')
        if author_year_end is not None:
            queryset = queryset.filter(
                Q(authors__birth_year__lte=author_year_end) |
                Q(authors__death_year__lte=author_year_end)
            )

        author_year_start = self.request.GET.get('author_year_start')
        if author_year_start is not None:
            queryset = queryset.filter(
                Q(authors__birth_year__gte=author_year_start) |
                Q(authors__death_year__gte=author_year_start)
            )

        id_string = self.request.GET.get('ids')
        if id_string is not None:
            ids = id_string.split(',')
            queryset = queryset.filter(gutenberg_id__in=ids)

        language_string = self.request.GET.get('languages')
        if language_string is not None:
            language_codes = [code.lower() for code in language_string.split(',')]
            queryset = queryset.filter(languages__code__in=language_codes)

        mime_type = self.request.GET.get('mime_type')
        if mime_type is not None:
            queryset = queryset.filter(format__mime_type__startswith=mime_type)

        search_string = self.request.GET.get('search')
        if search_string is not None:
            search_terms = search_string.split(' ')
            for term in search_terms:
                queryset = queryset.filter(
                    Q(authors__name__icontains=term) | Q(title__icontains=term)
                )

        topic = self.request.GET.get('topic')
        if topic is not None:
            queryset = queryset.filter(
                Q(bookshelves__name__icontains=topic) | Q(subjects__name__icontains=topic)
            )

        return queryset.distinct()


class BookshelfViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows book shelves to be viewed. """
    queryset = Bookshelf.objects.all().order_by('name')
    serializer_class = BookshelfSerializer


class FormatViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows book formats to be viewed. """
    queryset = Format.objects.all().order_by('book__download_count')
    serializer_class = FormatSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows languages to be viewed. """
    queryset = Language.objects.all().order_by('code')
    serializer_class = LanguageSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    """ This is an API endpoint that allows book subjects to be viewed. """
    queryset = Subject.objects.all().order_by('name')
    serializer_class = SubjectSerializer

def get_ranked_books(query):
    counter = utils.get_word_count(query)
    postings = Posting.objects.filter(token__name__in=counter.keys())

    # only get books that have at least one of the terms queried
    books = Book.objects.filter(posting__in=postings)

    # get cosine distane for every book
    rated_books = [(book, book.cosine_distance(query)) for book in books]

    # sort by the cosine distance, lowest to highest
    ranked_books = sorted(rated_books, key=lambda x: x[1])

    return [rank_tuple[0] for rank_tuple in ranked_books][:10]

class QueryView(View):
    form_class = QueryForm
    template_name = 'query.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request, query):
        form = QueryForm(self.request.POST)
        if form.is_valid():
            relevant_books = get_ranked_books(form.query)
