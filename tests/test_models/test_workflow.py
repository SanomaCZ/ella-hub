# -*- coding: utf-8 -*-

from nose import tools
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Author
from ella.utils import timezone

from ella_hub.models import State, Transition, Workflow, Permission, Role, CommonArticle
from ella_hub.models import (StatePermissionRelation, StateObjectRelation,
    WorkflowModelRelation, WorkflowPermissionRelation)
from ella_hub.utils.workflow import get_workflow


class TestWorkflowModels(TestCase):
    def setUp(self):
        self.workflow = Workflow.objects.create(title="Test Workflow", description="Test desc.")
        self.state = State.objects.create(title="Test State", description="Test desc.")
        self.transition = Transition.objects.create(title="Test Transition",
            workflow=self.workflow, destination=self.state)

        self.permission = Permission.objects.create(title="Test Permission",
            codename="test_perm", description="Good perm.")
        self.role = Role.objects.create(title="Test Role", description="Good role.")
        self.content_type = ContentType.objects.get_for_model(CommonArticle)

        self.spr = StatePermissionRelation.objects.create(state=self.state,
            permission=self.permission, role=self.role)
        self.sor = StateObjectRelation.objects.create(state=self.state,
            content_type=self.content_type)
        self.wmr = WorkflowModelRelation.objects.create(workflow=self.workflow,
            content_type=self.content_type)
        self.wpr = WorkflowPermissionRelation.objects.create(workflow=self.workflow,
            permission=self.permission)

    def tearDown(self):
        Transition.objects.all().delete()
        State.objects.all().delete()
        Workflow.objects.all().delete()

    def test_to_string(self):
        # workflow
        tools.assert_equals(unicode(self.workflow), u"%s" % self.workflow.title)
        self.workflow.initial_state = self.state
        self.workflow.save()
        tools.assert_equals(unicode(self.workflow),
            u"%s : %s" % (self.workflow.title, self.workflow.initial_state.title))

        # state
        tools.assert_equals(unicode(self.state), u"%s (%d transitions)" % (
            self.state.title, self.state.transitions.count()))

        self.state.title = u"Someľčť titleščľ"
        self.state.transitions.add(Transition.objects.create(title="Transition to hell",
            workflow=self.workflow, destination=self.state))
        self.state.save()

        tools.assert_equals(unicode(self.state), u"%s (%d transitions)" % (
            self.state.title, self.state.transitions.count()))

        # transition
        tools.assert_equals(unicode(self.transition), u"%s (-> %s)" % (
            self.transition.title, self.state.title))

        self.transition.title = u"Someľčť titleščľ"
        self.transition.save()

        tools.assert_equals(unicode(self.transition), u"%s (-> %s)" % (
            self.transition.title, self.state.title))

        # state_permission_relation
        tools.assert_equals(unicode(self.spr), u"%s / %s / %s" % (
            self.spr.state.title, self.spr.role.title, self.spr.permission.title))

        # state_object_relation
        tools.assert_equals(unicode(self.sor), u"%s %s - %s" % (
            self.sor.content_type.name, self.sor.content_id, self.sor.state.title))

        # workflow_model_relation
        tools.assert_equals(unicode(self.wmr), u"%s / %s" % (
            self.wmr.content_type.name, self.wmr.workflow.title))

        # workflow_permission_relation
        tools.assert_equals(unicode(self.wpr), u"%s / %s" % (
            self.wpr.workflow.title, self.wpr.permission.title))

    def test_workflow_initial_state(self):
        tools.assert_equals(self.workflow.get_initial_state(), None)

        self.state.workflow = self.workflow
        self.state.save()
        tools.assert_equals(self.workflow.get_initial_state(), self.state)

        self.workflow.initial_state = self.state
        self.workflow.save()
        tools.assert_equals(self.workflow.get_initial_state(), self.state)

    def test_set_workflow_existing_model_relation(self):
        self.workflow.set_to_model(CommonArticle)
        self.new_workflow = Workflow.objects.create(title="New Workflow", description="Test desc.")
        self.new_workflow.set_to_model(CommonArticle)

        tools.assert_equals(get_workflow(CommonArticle), self.new_workflow)
