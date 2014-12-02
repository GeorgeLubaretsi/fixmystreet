from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from apps.users.models import FMSUser
from django import forms


class FMSUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(FMSUserCreationForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            FMSUser.objects.get(username=username)
        except FMSUser.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    class Meta:
        model = FMSUser
        fields = ('username', 'first_name', 'last_name', 'email')


class FMSUserChangeForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(FMSUserChangeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FMSUser
        fields = ('username', 'first_name', 'last_name', 'email')