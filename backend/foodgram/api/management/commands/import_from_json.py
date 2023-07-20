import json
import os

from django.core.management import BaseCommand
from django.conf import settings

from recipes.models import Ingredients

FILE_DIR = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    def handle(self, *args, **options):
        data_path = f'{FILE_DIR}/ingredients.json'
        with open(data_path, encoding='utf-8') as file:
            data = json.load(file)
        ingredients = []
        unique_names = set()
        for item in data:
            name = item['name']
            if name and name not in unique_names:
                unique_names.add(name)
                ingredient = Ingredients(
                    name=item['name'],
                    measurement_unit=item['measurement_unit'],
                )
                ingredients.append(ingredient)
        Ingredients.objects.bulk_create(ingredients)
