from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from ella.core.models import Author, Publishable
from ella.articles.models import Article

from ella_hub.models import Workflow, State, Transition
from ella_hub.models import Permission, Role, ModelPermission
from ella_hub.models import WorkflowPermissionRelation, StatePermissionRelation


def create_advanced_workflow(case, resources):
    case.workflow = Workflow.objects.get_or_create(title="Advanced workflow")[0]

    case.super_role = Role.objects.get_or_create(title=unicode(_("Super role")))[0]

    STATES = (
        (_("State 1"), "state1"),
        (_("State 2"), "state2"),
        (_("State 3"), "state3"),
        (_("State 4"), "state4"),
        (_("State 5"), "state5"),
    )

    PERMISSIONS = (
        (_("Can view"), "can_view"),
        (_("Can add"), "can_add"),
        (_("Can edit"), "can_change"),
        (_("Can delete"), "can_delete"),
    )

    case.all_models = [resource._meta.object_class for resource in resources]
    case.publishable_models = [model for model in case.all_models
        if issubclass(model, Publishable) and model != Publishable]

    state_obj_list = []
    perm_obj_list = []

    state_obj_list = _create_states(STATES, case.workflow)
    case.workflow.initial_state = state_obj_list[0]
    case.workflow.save()

    _make_all_possible_transitions(state_obj_list, case.workflow)

    # set workflow to all models
    for model in case.all_models:
        case.workflow.set_to_model(model)

    # create basic permissions
    for (perm_name, perm_codename) in PERMISSIONS:
        p = Permission.objects.get_or_create(title=unicode(perm_name), codename=perm_codename)[0]
        perm_obj_list.append(p)

    # map permissions to models for roles (only for super role)
    for model in case.all_models:
        content_type = ContentType.objects.get_for_model(model)
        for perm_obj in perm_obj_list:
            ModelPermission.objects.get_or_create(role=case.super_role,
                permission=perm_obj, content_type=content_type)

    for perm_obj in perm_obj_list:
        WorkflowPermissionRelation.objects.get_or_create(workflow=case.workflow,
            permission=perm_obj)

        for state_obj in state_obj_list:
            StatePermissionRelation.objects.get_or_create(state=state_obj,
                permission=perm_obj, role=case.super_role)

    ##### Base role
    case.base_role = Role.objects.get_or_create(title=unicode(_("Base role")))[0]

    STATES = (
        (_("State 1"), "state1"),
        (_("State 2"), "state2"),
        (_("State 5"), "state5")
    )

    # create states
    case.state1 = State.objects.get_or_create(title=unicode(_("State 1")),
        codename="state1", workflow=case.workflow)[0]
    case.state2 = State.objects.get_or_create(title=unicode(_("State 2")),
        codename="state2", workflow=case.workflow)[0]
    case.state5 = State.objects.get_or_create(title=unicode(_("State 5")),
        codename="state5", workflow=case.workflow)[0]


    state_obj_list = _create_states(STATES, case.workflow)

    case.to_state1 = Transition.objects.get_or_create(title="to %s" % case.state1.title,
            workflow=case.workflow, destination=case.state1)[0]
    case.to_state2 = Transition.objects.get_or_create(title="to %s" % case.state2.title,
            workflow=case.workflow, destination=case.state2)[0]
    case.to_state5 = Transition.objects.get_or_create(title="to %s" % case.state5.title,
            workflow=case.workflow, destination=case.state5)[0]

    case.state1.transitions.add(case.to_state1)
    case.state1.transitions.add(case.to_state2)
    case.state1.transitions.add(case.to_state5)
    case.state2.transitions.add(case.to_state1)
    case.state2.transitions.add(case.to_state2)
    case.state5.transitions.add(case.to_state1)
    case.state5.transitions.add(case.to_state5)

    # only view permissions
    for model in case.all_models:
        content_type = ContentType.objects.get_for_model(model)
        for perm_obj in perm_obj_list[:1]:
            ModelPermission.objects.get_or_create(role=case.base_role,
                permission=perm_obj, content_type=content_type)

    for perm_obj in perm_obj_list[:1]:
        WorkflowPermissionRelation.objects.get_or_create(workflow=case.workflow,
            permission=perm_obj)

        for state_obj in state_obj_list:
            StatePermissionRelation.objects.get_or_create(state=state_obj,
                permission=perm_obj, role=case.base_role)

    r = Permission.objects.get_or_create(title="Readonly content",
        restriction=True, codename="readonly_content")[0]
    d = Permission.objects.get_or_create(title="Disabled authors",
        restriction=True, codename="disabled_authors")[0]

    content_type = ContentType.objects.get_for_model(Article)

    ModelPermission.objects.get_or_create(role=case.base_role,
        permission=r, content_type=content_type)
    ModelPermission.objects.get_or_create(role=case.base_role,
        permission=d, content_type=content_type)

    WorkflowPermissionRelation.objects.get_or_create(workflow=case.workflow,
        permission=r)
    WorkflowPermissionRelation.objects.get_or_create(workflow=case.workflow,
        permission=d)

    for state_obj in state_obj_list:
        StatePermissionRelation.objects.get_or_create(state=state_obj,
            permission=r, role=case.base_role)
        StatePermissionRelation.objects.get_or_create(state=state_obj,
            permission=d, role=case.base_role)

    return case.workflow

def _create_states(states, workflow):
    state_obj_list = []
    for state_name, state_codename in states:
        s = State.objects.get_or_create(title=unicode(state_name),
            codename=state_codename, workflow=workflow)[0]
        state_obj_list.append(s)
    return state_obj_list


def _make_all_possible_transitions(state_obj_list, workflow):
    for state_obj_dest in state_obj_list:
        t = Transition.objects.get_or_create(title="to %s" % state_obj_dest.title,
            workflow=workflow, destination=state_obj_dest)[0]

        for state_obj_src in state_obj_list:
            state_obj_src.transitions.add(t)
            state_obj_src.save()



def create_basic_workflow(case):
    case.workflow = Workflow.objects.create(title="Test workflow")
    case.workflow.set_to_model(Author)

    case.test_role = Role.objects.create(title="Test role")

    case.state1 = State.objects.create(title="State 1", codename="state_1",
        workflow=case.workflow)
    case.state2 = State.objects.create(title="State 2", codename="state_2",
        workflow=case.workflow)
    case.state3 = State.objects.create(title="State 3", codename="state_3",
        workflow=case.workflow)

    case.workflow.initial_state = case.state1

    case.to_state2 = Transition.objects.create(title="to state 2",
        workflow=case.workflow, destination=case.state2)
    case.to_state3 = Transition.objects.create(title="to state 3",
        workflow=case.workflow, destination=case.state3)

    case.state1.transitions.add(case.to_state2)
    case.state2.transitions.add(case.to_state3)

    case.can_view = Permission.objects.create(title="Can view",
        codename="can_view")
    case.can_add = Permission.objects.create(title="Can add",
        codename="can_add")
    case.can_change = Permission.objects.create(title="Can edit",
        codename="can_change")
    case.can_delete = Permission.objects.create(title="Can delete",
        codename="can_delete")

    content_type = ContentType.objects.get_for_model(Author)

    ModelPermission.objects.create(role=case.test_role,
        permission=case.can_view, content_type=content_type)
    ModelPermission.objects.create(role=case.test_role,
        permission=case.can_add, content_type=content_type)
    ModelPermission.objects.create(role=case.test_role,
        permission=case.can_change, content_type=content_type)
    ModelPermission.objects.create(role=case.test_role,
        permission=case.can_delete, content_type=content_type)

    WorkflowPermissionRelation.objects.create(workflow=case.workflow,
        permission=case.can_view)
    WorkflowPermissionRelation.objects.create(workflow=case.workflow,
        permission=case.can_add)
    WorkflowPermissionRelation.objects.create(workflow=case.workflow,
        permission=case.can_change)
    WorkflowPermissionRelation.objects.create(workflow=case.workflow,
        permission=case.can_delete)

    StatePermissionRelation.objects.create(state=case.state1,
        permission=case.can_view, role=case.test_role)
    StatePermissionRelation.objects.create(state=case.state1,
        permission=case.can_add, role=case.test_role)
    StatePermissionRelation.objects.create(state=case.state1,
        permission=case.can_change, role=case.test_role)
    StatePermissionRelation.objects.create(state=case.state1,
        permission=case.can_delete, role=case.test_role)

    StatePermissionRelation.objects.create(state=case.state2,
        permission=case.can_view, role=case.test_role)
    StatePermissionRelation.objects.create(state=case.state2,
        permission=case.can_add, role=case.test_role)
    StatePermissionRelation.objects.create(state=case.state2,
        permission=case.can_change, role=case.test_role)

    StatePermissionRelation.objects.create(state=case.state3,
        permission=case.can_view, role=case.test_role)
    StatePermissionRelation.objects.create(state=case.state3,
        permission=case.can_add, role=case.test_role)


def delete_test_workflow():
    Workflow.objects.all().delete()
    State.objects.all().delete()
    Transition.objects.all().delete()
    Permission.objects.all().delete()
    Role.objects.all().delete()
    ModelPermission.objects.all().delete()
    WorkflowPermissionRelation.objects.all().delete()
    StatePermissionRelation.objects.all().delete()
