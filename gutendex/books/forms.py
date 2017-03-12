from django import forms
from books import models


VECTOR_TRANSFORMATIONS = (
    ("0", "TF-IDF"),
    ("1", "No Transformation"),
    ("2", "Binary"),
)

class QueryForm(forms.Form):
    DISTANCE_METRICS = (
        ("0", "Cosine Distance"),
        ("1", "Jaccard Distance"),
        ("2", "Dice Coefficient"),
    )

    query = forms.CharField(label='Query', max_length=300,
                            widget=forms.TextInput(attrs={'size': 50}))
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
    DISTANCE_METRICS = (
        ("0", "Cosine Distance"),
        ("1", "Jaccard Distance"),
        ("2", "Dice Distance"),
        ("3", "Pearson Correlation Distance"),
        ("4", "Euclidean Distance"),
    )
    book = forms.ModelChoiceField(
        queryset=models.Book.objects.exclude(title=None).exclude(text='').order_by('title'),
        label='Recommend books for',
        required=True,
    )
    distance_type = forms.ModelChoiceField(
        queryset=models.DistanceType.objects.all(),
        initial="0",
        widget=forms.Select,
        label="Distance Metric",
        required=True,
    )
