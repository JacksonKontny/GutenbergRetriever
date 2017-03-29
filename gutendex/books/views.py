from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.urls import reverse

from rest_framework import viewsets
from rest_framework.response import Response

from books import utils

from .models import *
from .serializers import *
from .forms import QueryForm, RecommendForm


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

def get_ranked_books(query, distance_metric, transformation, limit=10):
    metric_mapping = {
        '0': 'cosine_distance',
        '1': 'jaccard_distance',
        '2': 'dice_distance',
    }
    transformation_mapping = {
        '0': 'tfidf',
        '1': '', # No tranformation
        '2': 'binary',
    }
    counter = utils.get_word_count(query)

    # only get books that have at least one of the terms queried
    books = Book.objects.filter(tokens__name__in=counter.keys()).distinct()

    # get distance metric for every book
    rated_books = [
        (
            book.pk,
            getattr(
                book, metric_mapping[distance_metric]
            )(counter, transformation=transformation_mapping[transformation]),
         ) for book in books
    ]

    # sort by the cosine distance, lowest to highest
    ranked_books = sorted(rated_books, key=lambda x: x[1])

    return [rank_tuple[0] for rank_tuple in ranked_books][:limit]

class RecommendView(LoginRequiredMixin, View):
    form_class = RecommendForm
    template_name = 'recommend.html'

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {'form': self.form_class()},
        )

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)
        if form.is_valid():
            book = form.cleaned_data['book']
            distance_type = form.cleaned_data['distance_type']
            relevant_books = list(
                Distance.objects.filter(
                    book_1=book,
                    distance_type=distance_type,
                ).order_by('distance').values_list('book_2__pk', flat=True)
            )[:10]
            self.request.session['books'] = relevant_books
            return HttpResponseRedirect(
                reverse('books:ranked-list')
            )
        else:
            return self.get(request, *args, **kwargs)

class QueryView(LoginRequiredMixin, View):
    form_class = QueryForm
    template_name = 'query.html'

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {'form': self.form_class()},
        )

    def post(self, request, *args, **kwargs):
        form = QueryForm(self.request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            distance_metric = form.cleaned_data['distance_metric']
            transformation = form.cleaned_data['transformation']
            relevant_books = get_ranked_books(
                query,
                distance_metric,
                transformation
            )
            self.request.session['books'] = relevant_books
            return HttpResponseRedirect(
                reverse('books:ranked-list')
            )
        else:
            return self.get(request, *args, **kwargs)

class ListView(LoginRequiredMixin, View):
    template_name = 'ranked-list.html'

    def get(self, request, *args, **kwargs):
        book_list = []
        for book_pk in request.session['books']:
            book_list.append(Book.objects.get(pk=book_pk))

        return render(
            request,
            self.template_name,
            {'books': book_list},
        )

class DetailView(LoginRequiredMixin, View):
    template_name = 'book-text.html'

    def get(self, request, pk, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {'text': Book.objects.get(pk=pk).text}
        )
