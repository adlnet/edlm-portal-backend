from django.contrib import admin

from vacancies.models import Vacancy

# Register your models here.


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('vacancy_key', 'JobTitle', 'JobPostingID')