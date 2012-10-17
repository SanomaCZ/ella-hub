from django.contrib.contenttypes.models import ContentType

from ella.core.models import Author

from ella_hub.models import Workflow, State, Transition
from ella_hub.models import Permission, Role, ModelPermission
from ella_hub.models import WorkflowPermissionRelation, StatePermissionRelation



def create_basic_workflow(case):
    case.workflow = Workflow.objects.create(title="Test workflow")

    case.test_role = Role.objects.create(title="Test role")

    case.state1 = State.objects.create(title="State 1", codename="state_1",
        workflow=case.workflow)
    case.state2 = State.objects.create(title="State 2", codename="state_2",
        workflow=case.workflow)
    case.state3 = State.objects.create(title="State 3", codename="state_3",
        workflow=case.workflow)

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

    #case.addCleanup(Workflow.objects.clear_cache)
    #case.addCleanup(State.objects.clear_cache)
    #case.addCleanup(Transition.objects.clear_cache)
    #case.addCleanup(Permission.objects.clear_cache)
    #case.addCleanup(Role.objects.clear_cache)
    #case.addCleanup(ModelPermission.objects.clear_cache)
    #case.addCleanup(WorkflowPermissionRelation.objects.clear_cache)
    #case.addCleanup(StatePermissionRelation.objects.clear_cache)
