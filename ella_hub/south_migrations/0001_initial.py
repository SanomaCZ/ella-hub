# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Draft'
        db.create_table('ella_hub_draft', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('data', self.gf('jsonfield.fields.JSONField')()),
        ))
        db.send_create_signal('ella_hub', ['Draft'])

        # Adding model 'PublishableLock'
        db.create_table('ella_hub_publishablelock', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('publishable', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Publishable'], unique=True)),
            ('locked_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('ella_hub', ['PublishableLock'])

        # Adding model 'Permission'
        db.create_table('ella_hub_permission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('codename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('restriction', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ella_hub', ['Permission'])

        # Adding M2M table for field content_types on 'Permission'
        db.create_table('ella_hub_permission_content_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('permission', models.ForeignKey(orm['ella_hub.permission'], null=False)),
            ('contenttype', models.ForeignKey(orm['contenttypes.contenttype'], null=False))
        ))
        db.create_unique('ella_hub_permission_content_types', ['permission_id', 'contenttype_id'])

        # Adding model 'ModelPermission'
        db.create_table('ella_hub_modelpermission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ella_hub.Role'], null=True, blank=True)),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ella_hub.Permission'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal('ella_hub', ['ModelPermission'])

        # Adding model 'PrincipalRoleRelation'
        db.create_table('ella_hub_principalrolerelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], null=True, blank=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ella_hub.Role'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('content_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('ella_hub', ['PrincipalRoleRelation'])

        # Adding model 'Role'
        db.create_table('ella_hub_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('ella_hub', ['Role'])

        # Adding model 'Workflow'
        db.create_table('ella_hub_workflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('initial_state', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='workflow_initial_state', null=True, to=orm['ella_hub.State'])),
        ))
        db.send_create_signal('ella_hub', ['Workflow'])

        # Adding model 'State'
        db.create_table('ella_hub_state', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('codename', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='states', null=True, to=orm['ella_hub.Workflow'])),
        ))
        db.send_create_signal('ella_hub', ['State'])

        # Adding M2M table for field transitions on 'State'
        db.create_table('ella_hub_state_transitions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('state', models.ForeignKey(orm['ella_hub.state'], null=False)),
            ('transition', models.ForeignKey(orm['ella_hub.transition'], null=False))
        ))
        db.create_unique('ella_hub_state_transitions', ['state_id', 'transition_id'])

        # Adding model 'Transition'
        db.create_table('ella_hub_transition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ella_hub.Workflow'], blank=True)),
            ('destination', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ella_hub.State'])),
        ))
        db.send_create_signal('ella_hub', ['Transition'])

        # Adding model 'StateObjectRelation'
        db.create_table('ella_hub_stateobjectrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='state_object', null=True, to=orm['contenttypes.ContentType'])),
            ('content_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ella_hub.State'])),
        ))
        db.send_create_signal('ella_hub', ['StateObjectRelation'])

        # Adding unique constraint on 'StateObjectRelation', fields ['content_type', 'content_id', 'state']
        db.create_unique('ella_hub_stateobjectrelation', ['content_type_id', 'content_id', 'state_id'])

        # Adding model 'StatePermissionRelation'
        db.create_table('ella_hub_statepermissionrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ella_hub.State'])),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ella_hub.Permission'])),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ella_hub.Role'])),
        ))
        db.send_create_signal('ella_hub', ['StatePermissionRelation'])

        # Adding model 'WorkflowModelRelation'
        db.create_table('ella_hub_workflowmodelrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], unique=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wmr_workflow', to=orm['ella_hub.Workflow'])),
        ))
        db.send_create_signal('ella_hub', ['WorkflowModelRelation'])

        # Adding model 'WorkflowPermissionRelation'
        db.create_table('ella_hub_workflowpermissionrelation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wpr_workflow', to=orm['ella_hub.Workflow'])),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(related_name='permissions', to=orm['ella_hub.Permission'])),
        ))
        db.send_create_signal('ella_hub', ['WorkflowPermissionRelation'])


    def backwards(self, orm):
        # Removing unique constraint on 'StateObjectRelation', fields ['content_type', 'content_id', 'state']
        db.delete_unique('ella_hub_stateobjectrelation', ['content_type_id', 'content_id', 'state_id'])

        # Deleting model 'Draft'
        db.delete_table('ella_hub_draft')

        # Deleting model 'PublishableLock'
        db.delete_table('ella_hub_publishablelock')

        # Deleting model 'Permission'
        db.delete_table('ella_hub_permission')

        # Removing M2M table for field content_types on 'Permission'
        db.delete_table('ella_hub_permission_content_types')

        # Deleting model 'ModelPermission'
        db.delete_table('ella_hub_modelpermission')

        # Deleting model 'PrincipalRoleRelation'
        db.delete_table('ella_hub_principalrolerelation')

        # Deleting model 'Role'
        db.delete_table('ella_hub_role')

        # Deleting model 'Workflow'
        db.delete_table('ella_hub_workflow')

        # Deleting model 'State'
        db.delete_table('ella_hub_state')

        # Removing M2M table for field transitions on 'State'
        db.delete_table('ella_hub_state_transitions')

        # Deleting model 'Transition'
        db.delete_table('ella_hub_transition')

        # Deleting model 'StateObjectRelation'
        db.delete_table('ella_hub_stateobjectrelation')

        # Deleting model 'StatePermissionRelation'
        db.delete_table('ella_hub_statepermissionrelation')

        # Deleting model 'WorkflowModelRelation'
        db.delete_table('ella_hub_workflowmodelrelation')

        # Deleting model 'WorkflowPermissionRelation'
        db.delete_table('ella_hub_workflowpermissionrelation')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.author': {
            'Meta': {'object_name': 'Author'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'photo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['photos.Photo']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'core.category': {
            'Meta': {'unique_together': "(('site', 'tree_path'),)", 'object_name': 'Category'},
            'app_data': ('app_data.fields.AppDataField', [], {'default': "'{}'"}),
            'content': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'template': ('django.db.models.fields.CharField', [], {'default': "'category.html'", 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tree_parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Category']", 'null': 'True', 'blank': 'True'}),
            'tree_path': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'core.publishable': {
            'Meta': {'object_name': 'Publishable'},
            'announced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'app_data': ('app_data.fields.AppDataField', [], {'default': "'{}'"}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Author']", 'symmetrical': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Category']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'photo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['photos.Photo']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'publish_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(3000, 1, 1, 0, 0, 0, 2)', 'db_index': 'True'}),
            'publish_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Source']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'static': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'core.source': {
            'Meta': {'object_name': 'Source'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'ella_hub.draft': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'Draft'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'data': ('jsonfield.fields.JSONField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'ella_hub.modelpermission': {
            'Meta': {'object_name': 'ModelPermission'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ella_hub.Permission']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ella_hub.Role']", 'null': 'True', 'blank': 'True'})
        },
        'ella_hub.permission': {
            'Meta': {'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'content_types': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'content_types'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'restriction': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'ella_hub.principalrolerelation': {
            'Meta': {'object_name': 'PrincipalRoleRelation'},
            'content_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ella_hub.Role']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'ella_hub.publishablelock': {
            'Meta': {'object_name': 'PublishableLock'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'publishable': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Publishable']", 'unique': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'ella_hub.role': {
            'Meta': {'object_name': 'Role'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'ella_hub.state': {
            'Meta': {'object_name': 'State'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'transitions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['ella_hub.Transition']", 'null': 'True', 'blank': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'states'", 'null': 'True', 'to': "orm['ella_hub.Workflow']"})
        },
        'ella_hub.stateobjectrelation': {
            'Meta': {'unique_together': "(('content_type', 'content_id', 'state'),)", 'object_name': 'StateObjectRelation'},
            'content_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'state_object'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ella_hub.State']"})
        },
        'ella_hub.statepermissionrelation': {
            'Meta': {'object_name': 'StatePermissionRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ella_hub.Permission']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ella_hub.Role']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ella_hub.State']"})
        },
        'ella_hub.transition': {
            'Meta': {'object_name': 'Transition'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'destination': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ella_hub.State']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ella_hub.Workflow']", 'blank': 'True'})
        },
        'ella_hub.workflow': {
            'Meta': {'object_name': 'Workflow'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_state': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'workflow_initial_state'", 'null': 'True', 'to': "orm['ella_hub.State']"}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ella_hub.Permission']", 'through': "orm['ella_hub.WorkflowPermissionRelation']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'ella_hub.workflowmodelrelation': {
            'Meta': {'object_name': 'WorkflowModelRelation'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wmr_workflow'", 'to': "orm['ella_hub.Workflow']"})
        },
        'ella_hub.workflowpermissionrelation': {
            'Meta': {'object_name': 'WorkflowPermissionRelation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permissions'", 'to': "orm['ella_hub.Permission']"}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wpr_workflow'", 'to': "orm['ella_hub.Workflow']"})
        },
        'photos.photo': {
            'Meta': {'object_name': 'Photo'},
            'app_data': ('app_data.fields.AppDataField', [], {'default': "'{}'"}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'photo_set'", 'symmetrical': 'False', 'to': "orm['core.Author']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255'}),
            'important_bottom': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'important_left': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'important_right': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'important_top': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Source']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'taggit.tag': {
            'Meta': {'ordering': "['namespace', 'name']", 'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'namespace': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['ella_hub']