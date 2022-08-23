import csv

from main.models import Ingredient
from django.core.management.base import BaseCommand


path = '/Users/peter/Dev/food_backend/data/ingredients.csv'


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                data = {'name': row[0].split(',')[0], 'measurement_unit': row[0].split(',')[1]}
                Ingredient.objects.create(**data)
