# Generated manually for PopularSearchTerm

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OutdoorShop', '0002_delete_shippingaddress'),
    ]

    operations = [
        migrations.CreateModel(
            name='PopularSearchTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.CharField(db_index=True, max_length=200, unique=True)),
                ('hit_count', models.PositiveIntegerField(default=0)),
                ('last_searched_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Popular search term',
                'verbose_name_plural': 'Popular search terms',
                'ordering': ['-hit_count', '-last_searched_at'],
            },
        ),
    ]
