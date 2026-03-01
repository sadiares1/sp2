from django import forms

from core.models import PassportData


class PassportDataForm(forms.ModelForm):
    class Meta:
        model = PassportData
        fields = "__all__"
