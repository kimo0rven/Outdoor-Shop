from django.contrib import admin

from .models import PopularSearchTerm


@admin.register(PopularSearchTerm)
class PopularSearchTermAdmin(admin.ModelAdmin):
    list_display = ('term', 'hit_count', 'last_searched_at')
    search_fields = ('term',)
    ordering = ('-hit_count', '-last_searched_at')
