from django import forms
from django.db.models import get_model
from ervin.widgets import WYMEditor

class DbContentAdminModelForm(forms.ModelForm):
    data = forms.CharField(widget=WYMEditor())

    class Meta:
        model = get_model('ervin', 'dbcontent')

class PageAdminModelForm(forms.ModelForm):
    content = forms.CharField(widget=WYMEditor())
    blurb = forms.CharField(widget=WYMEditor())

    class Meta:
        model = get_model('ervin', 'page')
        
