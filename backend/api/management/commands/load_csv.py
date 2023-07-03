# import csv

# from django.conf import settings
# from django.core.management import BaseCommand

# from recipes.models import Ingredients


# TABLES_DICT = {
#     Ingredients: 'ingredients.csv'
# }


# class Command(BaseCommand):
#     help = 'Load data from csv files'

#     def handle(self, *args, **kwargs):
#         for model, base in TABLES_DICT.items():
#             with open(
#                 f'{settings.BASE_DIR}/data/{base}',
#                 'r', encoding='utf-8'
#             ) as csv_file:
#                 reader = csv.DictReader(csv_file)
#                 if model == Title.genre.through:
#                     objs = []
#                     for data in reader:
#                         title = Title.objects.get(id=data['title_id'])
#                         genre = Genre.objects.get(id=data['genre_id'])
#                         objs.append(model(title=title, genre=genre))
#                     model.objects.bulk_create(objs)
#                 else:
#                     model.objects.bulk_create(model(**data) for data in reader)

#         self.stdout.write(self.style.SUCCESS('Successfully load data'))
