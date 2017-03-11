from django import forms
from books import models


DISTANCE_METRICS = (
    ("0", "Cosine Distance"),
    ("1", "Jaccard Distance"),
    ("2", "Dice Coefficient"),
)

class QueryForm(forms.Form):

    query = forms.CharField(label='Query', max_length=300,
                            widget=forms.TextInput(attrs={'size': 50}))
    distance_metric = forms.ChoiceField(
        choices=DISTANCE_METRICS,
        initial="0",
        widget=forms.Select,
        label="Distance Metric",
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
