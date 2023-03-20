import django.dispatch


export_success = django.dispatch.Signal(providing_args=['exported_file'])
export_failure = django.dispatch.Signal(providing_args=['exception'])
