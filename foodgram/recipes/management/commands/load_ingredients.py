import csv
from django.conf import settings
from django.core.management import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка из csv файла'

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        try:
            with open(
                f'{data_path}/data/ingredients.csv',
                'r',
                encoding='utf-8'
            ) as file:
                read_data = csv.reader(file)
                bulk_list = list()
                for items in read_data:
                    name, measurement_unit = items
                    bulk_list.append(
                        Ingredient(name=name,
                                   measurement_unit=measurement_unit)
                    )
                Ingredient.objects.bulk_create(bulk_list)
            self.stdout.write(self.style.SUCCESS('Все ингридиенты загружены!'))
        except FileNotFoundError:
            raise CommandError('Добавьте файл ingredients в директорию data')
