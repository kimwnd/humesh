from django import forms

class ControlLEDForm(forms.Form):
    command = forms.CharField()