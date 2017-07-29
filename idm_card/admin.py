from django.contrib import admin

from . import models


class CardAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Card, CardAdmin)