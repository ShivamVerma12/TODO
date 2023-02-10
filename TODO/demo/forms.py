from django import forms
from django.contrib.auth import authenticate, get_user_model
from .models import TODO, CustomUser
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm


class TODOForm(forms.ModelForm):
    class Meta:
        model = TODO
        fields = ['tasks', 'status', 'priority']


class UpdateForm(TODOForm):
    '''Updating Todo List'''

    class Meta:
        model = TODO
        fields = ['tasks', 'priority']


# class SignupForm(UserCreationForm):
#     '''For Signing up User'''
#     email = forms.EmailField()
#
#
#     class Meta:
#         model = CustomUser
#         fields = ['email']

class SignupForm(forms.ModelForm):
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class ForgetPasswordForm(forms.ModelForm):
    '''For Changing Password'''
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['email']


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=100, widget=forms.PasswordInput)


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = '__all__'

    def clean(self,*args,**kwargs):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise forms.ValidationError('User Does Not Exist')

            if not user.check_password(password):
                raise forms.ValidationError('Incorrect Password')

        return super(UserLoginForm, self).clean(*args,**kwargs)

# user = get_user_model()
