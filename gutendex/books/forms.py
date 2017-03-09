from django import forms

class QueryForm(forms.Form):

    DISTANCE_METRICS = (
        ("0", "Cosine Distance"),
        ("1", "Jaccard"),
    )

    query = forms.CharField(label='Query', max_length=300)
    distance_metric = forms.ChoiceField(
        choices=DISTANCE_METRICS,
        initial="0",
        widget=forms.Select,
        label="Distance Metric",
        required=True
    )

