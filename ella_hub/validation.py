import logging
from django.forms.util import ErrorDict, ErrorList
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from tastypie.validation import Validation

logger = logging.getLogger(__name__)


class ModelValidation(Validation):
    validate_unique = True
    error_class = ErrorList

    def __init__(self, **kwargs):
        super(ModelValidation, self).__init__(**kwargs)
        self.validate_unique = kwargs.get('validate_unique', self.validate_unique)

    def _update_errors(self, errors, obj):
        opts = obj._meta
        fields = tuple(opts.concrete_fields) + tuple(opts.virtual_fields) + tuple(opts.many_to_many)
        for field, messages in errors.error_dict.items():
            if field not in fields:
                continue
            field = fields[field]
            for message in messages:
                if isinstance(message, ValidationError):
                    if message.code in field.error_messages:
                        message.message = field.error_messages[message.code]

        message_dict = errors.message_dict
        for k, v in message_dict.items():
            if k != NON_FIELD_ERRORS:
                self._errors.setdefault(k, self.error_class()).extend(v)
                # Remove the data from the cleaned_data dict since it was invalid
                # if k in self.cleaned_data:
                #    del self.cleaned_data[k]
        if NON_FIELD_ERRORS in message_dict:
            messages = message_dict[NON_FIELD_ERRORS]
            self._errors.setdefault(NON_FIELD_ERRORS, self.error_class()).extend(messages)

    def is_valid(self, bundle, request=None):
        self._errors = ErrorDict()
        try:
            bundle.obj.full_clean(validate_unique=self.validate_unique)
        except ValidationError as e:
            self._update_errors(e, bundle.obj)
            logger.error('Validation Error', exc_info=True)
        return bool(self._errors) and self._errors or {}
