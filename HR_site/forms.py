from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Manager, Employee


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')
        
        
class CustomManagerCreationForm(UserCreationForm):

    class Meta:
        model = Manager
        fields = ('username', 'email')


class CustomManagerChangeForm(UserChangeForm):

    class Meta:
        model = Manager
        fields = ('username', 'email')


class CustomEmployeeCreationForm(UserCreationForm):
    class Meta:
        model = Employee
        fields = ('username', 'email')


class CustomEmployeeChangeForm(UserChangeForm):
    class Meta:
        model = Employee
        fields = ('username', 'email')
