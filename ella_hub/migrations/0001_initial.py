# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings
import ella.core.cache.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
        ('core', '0002_auto_20150430_1332'),
    ]

    operations = [
        migrations.CreateModel(
            name='Draft',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name='Name', blank=True)),
                ('timestamp', models.DateTimeField(editable=False)),
                ('data', jsonfield.fields.JSONField(default=dict, verbose_name='Data')),
                ('content_type', models.ForeignKey(verbose_name='Model', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-timestamp',),
                'verbose_name': 'Draft item',
                'verbose_name_plural': 'Draft items',
            },
        ),
        migrations.CreateModel(
            name='ModelPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_type', ella.core.cache.fields.CachedForeignKey(verbose_name='Content type', to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Model Permission',
                'verbose_name_plural': 'Model Permissions',
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=128, verbose_name='Name')),
                ('codename', models.CharField(unique=True, max_length=128, verbose_name='Codename')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('restriction', models.BooleanField(default=False, verbose_name='Restriction')),
                ('content_types', models.ManyToManyField(related_name='content_types', null=True, verbose_name='Content Types', to='contenttypes.ContentType', blank=True)),
            ],
            options={
                'verbose_name': 'Permission',
                'verbose_name_plural': 'Permissions',
            },
        ),
        migrations.CreateModel(
            name='PrincipalRoleRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_id', models.PositiveIntegerField(null=True, verbose_name='Content id', blank=True)),
                ('content_type', ella.core.cache.fields.CachedForeignKey(verbose_name='Content type', blank=True, to='contenttypes.ContentType', null=True)),
                ('group', ella.core.cache.fields.CachedForeignKey(verbose_name='Group', blank=True, to='auth.Group', null=True)),
            ],
            options={
                'verbose_name': 'Principal Role Relation',
                'verbose_name_plural': 'Principal Role Relations',
            },
        ),
        migrations.CreateModel(
            name='PublishableLock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('locked_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('publishable', models.ForeignKey(verbose_name='Locked publishable', to='core.Publishable', unique=True)),
            ],
            options={
                'verbose_name': 'Publishable lock',
                'verbose_name_plural': 'Publishable locks',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
            ],
            options={
                'verbose_name': 'Role',
                'verbose_name_plural': 'Roles',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
                ('codename', models.CharField(max_length=128, verbose_name='Codename')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
            ],
            options={
                'verbose_name': 'State',
                'verbose_name_plural': 'States',
            },
        ),
        migrations.CreateModel(
            name='StateObjectRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_id', models.PositiveIntegerField(null=True, verbose_name='Content id', blank=True)),
                ('content_type', ella.core.cache.fields.CachedForeignKey(related_name='state_object', verbose_name='Content type', blank=True, to='contenttypes.ContentType', null=True)),
                ('state', ella.core.cache.fields.CachedForeignKey(verbose_name='State', to='ella_hub.State')),
            ],
            options={
                'verbose_name': 'State-Object Relation',
                'verbose_name_plural': 'State-Object Relations',
            },
        ),
        migrations.CreateModel(
            name='StatePermissionRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', ella.core.cache.fields.CachedForeignKey(verbose_name='Permission', to='ella_hub.Permission')),
                ('role', ella.core.cache.fields.CachedForeignKey(verbose_name='Role', to='ella_hub.Role')),
                ('state', ella.core.cache.fields.CachedForeignKey(verbose_name='State', to='ella_hub.State')),
            ],
            options={
                'verbose_name': 'State-Permission Relation',
                'verbose_name_plural': 'State-Permission Relations',
            },
        ),
        migrations.CreateModel(
            name='Transition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('destination', ella.core.cache.fields.CachedForeignKey(verbose_name='Destination', to='ella_hub.State')),
            ],
            options={
                'verbose_name': 'Transition',
                'verbose_name_plural': 'Transition',
            },
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=128, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('initial_state', ella.core.cache.fields.CachedForeignKey(related_name='workflow_initial_state', verbose_name='Initial state', blank=True, to='ella_hub.State', null=True)),
            ],
            options={
                'verbose_name': 'Workflow',
                'verbose_name_plural': 'Workflows',
            },
        ),
        migrations.CreateModel(
            name='WorkflowModelRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content_type', ella.core.cache.fields.CachedForeignKey(verbose_name='Content Type', to='contenttypes.ContentType', unique=True)),
                ('workflow', ella.core.cache.fields.CachedForeignKey(related_name='wmr_workflow', verbose_name='Workflow', to='ella_hub.Workflow')),
            ],
            options={
                'verbose_name': 'Workflow-Model Relation',
                'verbose_name_plural': 'Workflow-Model Relations',
            },
        ),
        migrations.CreateModel(
            name='WorkflowPermissionRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permission', ella.core.cache.fields.CachedForeignKey(related_name='permissions', to='ella_hub.Permission')),
                ('workflow', ella.core.cache.fields.CachedForeignKey(related_name='wpr_workflow', verbose_name='Workflow', to='ella_hub.Workflow')),
            ],
            options={
                'verbose_name': 'Workflow-Permission Relation',
                'verbose_name_plural': 'Workflow-Permission Relations',
            },
        ),
        migrations.AddField(
            model_name='workflow',
            name='permissions',
            field=models.ManyToManyField(to='ella_hub.Permission', verbose_name='Permissions', through='ella_hub.WorkflowPermissionRelation'),
        ),
        migrations.AddField(
            model_name='transition',
            name='workflow',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Workflow', blank=True, to='ella_hub.Workflow'),
        ),
        migrations.AddField(
            model_name='state',
            name='transitions',
            field=models.ManyToManyField(to='ella_hub.Transition', null=True, verbose_name='Transitions', blank=True),
        ),
        migrations.AddField(
            model_name='state',
            name='workflow',
            field=ella.core.cache.fields.CachedForeignKey(related_name='states', verbose_name='Workflow', blank=True, to='ella_hub.Workflow', null=True),
        ),
        migrations.AddField(
            model_name='principalrolerelation',
            name='role',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Role', to='ella_hub.Role'),
        ),
        migrations.AddField(
            model_name='principalrolerelation',
            name='user',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='User', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='modelpermission',
            name='permission',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Permission', to='ella_hub.Permission'),
        ),
        migrations.AddField(
            model_name='modelpermission',
            name='role',
            field=ella.core.cache.fields.CachedForeignKey(verbose_name='Role', blank=True, to='ella_hub.Role', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='workflowpermissionrelation',
            unique_together=set([('workflow', 'permission')]),
        ),
        migrations.AlterUniqueTogether(
            name='workflowmodelrelation',
            unique_together=set([('content_type', 'workflow')]),
        ),
        migrations.AlterUniqueTogether(
            name='statepermissionrelation',
            unique_together=set([('state', 'permission', 'role')]),
        ),
        migrations.AlterUniqueTogether(
            name='stateobjectrelation',
            unique_together=set([('content_type', 'content_id', 'state')]),
        ),
        migrations.AlterUniqueTogether(
            name='modelpermission',
            unique_together=set([('role', 'permission', 'content_type')]),
        ),
    ]
