from django.contrib import admin

from .models import (Ingredient, IngredientsRecipe, Tag,
                     Recipe, Favorite, ShoppingCart)

# Register your models here.
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(IngredientsRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
