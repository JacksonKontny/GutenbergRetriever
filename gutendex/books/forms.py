from django import forms
from books import models


DISTANCE_METRICS = (
    ("0", "Cosine Distance"),
    ("1", "Jaccard Distance"),
    ("2", "Dice Coefficient"),
    ("3", "Pearson Correlation"),
    ("4", "Euclidean Distance"),
)
VECTOR_TRANSFORMATIONS = (
    ("0", "TF-IDF"),
    ("1", "No Transformation"),
    ("2", "Binary"),
)

class QueryForm(forms.Form):

    query = forms.CharField(label='Query', max_length=300)
    distance_metric = forms.ChoiceField(
        choices=DISTANCE_METRICS,
        initial="0",
        widget=forms.Select,
        label="Distance Metric",
        required=True
    )
    transformation = forms.ChoiceField(
        choices=VECTOR_TRANSFORMATIONS,
        initial="0",
        widget=forms.Select,
        label="Vector Transformation",
        required=True
    )

class RecommendForm(forms.Form):
    book = forms.ModelChoiceField(
        queryset=models.Book.objects.exclude(title=None).exclude(text='').order_by('title'),
        label='Recommend books for',
        required=True,
    )

    distance_metric = forms.ChoiceField(
        choices=DISTANCE_METRICS,
        initial="0",
        widget=forms.Select,
        label="Distance Metric",
        required=True
    )
    transformation = forms.ChoiceField(
        choices=VECTOR_TRANSFORMATIONS,
        initial="0",
        widget=forms.Select,
        label="Vector Transformation",
        required=True
    )
