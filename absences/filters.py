import django_filters
from accounts.models import Country
from django.contrib.auth import get_user_model
from django.forms import TextInput, SelectMultiple


class CalendarFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr='icontains', widget=TextInput(attrs={'id': 'filter_email'}))
    description = django_filters.CharFilter(lookup_expr='icontains',
                                            widget=TextInput(attrs={'id': 'filter_description'}))
    groups = django_filters.CharFilter(lookup_expr='icontains',
                                            widget=TextInput(attrs={'id': 'filter_groups'}))
    country_code = django_filters.ModelMultipleChoiceFilter(
        queryset=Country.objects.all(), to_field_name="alpha_3", widget=SelectMultiple(
            attrs={'id': 'filter_country', 'size': 2, 'class':
                'focus:ring-indigo-500 focus:border-indigo-500 block pl-7 pr-12 border-gray-300 rounded-md'}))

    class Meta:
        model = get_user_model()
        fields = []
