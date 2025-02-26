# forms.py
from django import forms
from .models import *
from django.contrib.auth.models import User

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'img_product', 'price', 'stock', 'description', 'category']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class MemberForm(forms.ModelForm):
    # Additional fields for the User model
    username = forms.CharField(max_length=255)
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)  # Optional password field
    password_confirm = forms.CharField(widget=forms.PasswordInput(), required=False)  # Confirm password field
    role = forms.ChoiceField(choices=Member.ROLE_CHOICES)

    class Meta:
        model = Member
        fields = ['username', 'first_name', 'last_name', 'role', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password != password_confirm:
            raise forms.ValidationError("รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน")

        return cleaned_data

    def save(self, commit=True):
        # Check if the Member instance has an associated User
        if not self.instance.pk:
            user = User()
        else:
            user = self.instance.user

        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        # Only set the password if it has been provided
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])

        if commit:
            try:
                user.save()
            except IntegrityError:
                raise forms.ValidationError("Username already exists. Please choose a different username.")

        # Save the Member instance
        member = super().save(commit=False)
        member.user = user
        if commit:
            member.save()

        return member

