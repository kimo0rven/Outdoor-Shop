from django.db import models
from django.db.models import F
from django.utils import timezone


class PopularSearchTerm(models.Model):
    """Aggregated storefront search phrases, ranked by frequency."""

    term = models.CharField(max_length=200, unique=True, db_index=True)
    hit_count = models.PositiveIntegerField(default=0)
    last_searched_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-hit_count', '-last_searched_at']
        verbose_name = 'Popular search term'
        verbose_name_plural = 'Popular search terms'

    def __str__(self):
        return f"{self.term} ({self.hit_count})"

    @classmethod
    def record(cls, raw_query: str) -> None:
        term = ' '.join((raw_query or '').strip().lower().split())
        if len(term) < 2:
            return
        max_len = cls._meta.get_field('term').max_length
        term = term[:max_len]
        obj, created = cls.objects.get_or_create(term=term, defaults={'hit_count': 1})
        if not created:
            cls.objects.filter(pk=obj.pk).update(
                hit_count=F('hit_count') + 1,
                last_searched_at=timezone.now(),
            )
