from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Follow, User


admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'pk', 'email',
        'first_name', 'last_name',
        'followers_count', 'recipes_count')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'

    @admin.display(description='Количество подписчиков')
    def followers_count(self, user):
        return user.following.count()

    @admin.display(description='Количество рецептов')
    def recipes_count(self, user):
        return user.recipe_author.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'following',
    )
    empty_value_display = '-пусто-'
