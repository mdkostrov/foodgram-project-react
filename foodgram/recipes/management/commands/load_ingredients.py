import csv
import logging
from django.conf import settings
from django.core.management import BaseCommand, CommandError

from recipes.models import Ingredient

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filemode='w',
)


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
                for items in read_data:
                    name, measurement_unit = items
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
            self.stdout.write(self.style.SUCCESS('Все ингридиенты загружены!'))
        except FileNotFoundError:
            raise CommandError('Добавьте файл ingredients в директорию data')
        logging.info('Successfully loaded all data into database')
