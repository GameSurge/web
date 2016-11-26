from flask_wtf import FlaskForm
from wtforms import FieldList
from wtforms.ext.sqlalchemy.fields import QuerySelectField


def _strip_whitespace(s):
    return s.strip() if isinstance(s, str) else s


class Form(FlaskForm):
    class Meta:
        def bind_field(self, form, unbound_field, options):
            # We don't set default filters for query-based fields as it breaks them if no query_factory is set
            # while the Form is instantiated. Also, it's quite pointless for those fields...
            # FieldList simply doesn't support filters.
            no_filter_fields = (QuerySelectField, FieldList)
            filters = [_strip_whitespace] if not issubclass(unbound_field.field_class, no_filter_fields) else []
            filters += unbound_field.kwargs.get('filters', [])
            return unbound_field.bind(form=form, filters=filters, **options)

    @property
    def error_list(self):
        """A list containing all errors, prefixed with the field's label.'"""
        all_errors = []
        for field_name, errors in self.errors.items():
            for error in errors:
                if isinstance(error, dict) and isinstance(self[field_name], FieldList):
                    for field in self[field_name].entries:
                        all_errors += ['{}: {}'.format(self[field_name].label.text, sub_error)
                                       for sub_error in field.form.error_list]
                else:
                    all_errors.append('{}: {}'.format(self[field_name].label.text, error))
        return all_errors
