from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.exceptions import ValidationError
import re

def validate_reg_no(value):
    patt = re.compile(r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$')
    res = patt.search(value)
    if res:
        return value
    else:
        raise ValidationError('Enter valid registration number as MH01AA1111 or MH01A1111')

class Register(UserCreationForm):    
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']

class Login(forms.Form):
    username = forms.CharField(error_messages={'required':'Please enter username'},widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))

class FindChallan(forms.Form):
    reg_no = forms.CharField(label="Registration Number", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Eg. : ZZ01AA1234'}),validators=[validate_reg_no])
    filter = forms.ChoiceField(label='',choices=(('all','All'),('paid','Paid'),('unpaid','Unpaid'),('closed','Closed')),widget=forms.Select(attrs={'class':'form-control'}))

class FindTransaction(forms.Form):
    filter = forms.ChoiceField(label='',choices=(('all','All'),('success','Success'),('failed','Failed')),widget=forms.Select(attrs={'class':'form-control'}))

class Subscribe(forms.Form):
    reg_no = forms.CharField(label="Registration Number", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Eg. : ZZ01AA1234'}),validators=[validate_reg_no])