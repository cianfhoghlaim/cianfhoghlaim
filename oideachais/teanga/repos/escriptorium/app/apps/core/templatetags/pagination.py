from django import template

register = template.Library()


@register.simple_tag
def url_replace(request, *url_parameters):
    dict_ = request.GET.copy()
    for field, value in zip(url_parameters[::2], url_parameters[1::2]):
        dict_[field] = value
    return dict_.urlencode()
