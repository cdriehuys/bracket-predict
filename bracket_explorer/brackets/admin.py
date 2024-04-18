from django.contrib import admin

from brackets import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Bracket)
class BracketAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at", "updated_at")
    fields = ("id", "name", "owner", "random_seed", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
