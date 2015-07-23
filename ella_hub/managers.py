from django.db.models import Manager


class StateObjectRelationManager(Manager):

    def get_for_ids_as_dict(self, ids, ct):
        """
        Return dict with key as obj_id and val is his state
        """
        qs = self.select_related('state').filter(content_id__in=ids, content_type=ct)
        return dict((obj.content_id, obj.state) for obj in qs)


class StateManager(Manager):

    def get_states_choices_as_dict(self):
        return dict((state.codename, state.title) for state in self.all().order_by('id'))
