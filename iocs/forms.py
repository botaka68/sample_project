from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField()


class SubmitIndicatorsForm(forms.Form):
    indicators = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Input IOC's here, (single IOC per line)"}))