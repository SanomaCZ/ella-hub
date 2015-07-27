# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ella_hub', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='content_types',
            field=models.ManyToManyField(related_name='content_types', verbose_name='Content Types', to='contenttypes.ContentType', blank=True),
        ),
        migrations.AlterField(
            model_name='publishablelock',
            name='publishable',
            field=models.OneToOneField(verbose_name='Locked publishable', to='core.Publishable'),
        ),
        migrations.AlterField(
            model_name='state',
            name='transitions',
            field=models.ManyToManyField(to='ella_hub.Transition', verbose_name='Transitions', blank=True),
        ),
    ]
