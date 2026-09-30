from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .validators import validate_url_list


class CrawlTaskForm(forms.Form):
    name = forms.CharField(
        label="Nom de la mission", max_length=80, required=False,
        widget=forms.TextInput(attrs={"placeholder": "ex. Veille prix concurrents"}),
    )
    urls = forms.CharField(
        label="Adresses à explorer",
        widget=forms.Textarea(attrs={
            "rows": 6, "spellcheck": "false", "autocomplete": "off",
            "placeholder": "https://exemple.fr/produit-1\nhttps://exemple.fr/produit-2",
        }),
    )

    def clean_urls(self):
        urls = validate_url_list(self.cleaned_data["urls"])
        self.cleaned_urls = urls
        return "\n".join(urls)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Adresse e-mail", required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec cette adresse.")
        return email
