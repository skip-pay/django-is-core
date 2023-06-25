class MiddlewareMixin:

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        response = response or self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


def get_last_parent_pk_field_name(obj):
    for field in obj._meta.fields:
        if field.primary_key and (not field.is_relation or not field.auto_created):
            return field.name
    raise RuntimeError('Last parent field name was not found (cannot happen)')
