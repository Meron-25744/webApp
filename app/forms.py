from django import forms
from .models import Item, Experience


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'price', 'category', 'slug', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['title', 'slug', 'description', 'price', 'duration_minutes', 'capacity', 'location', 'image', 'active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
