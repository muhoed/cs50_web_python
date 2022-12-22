from django.template.defaultfilters import slugify


def get_icon_upload_path(instance, filename):
    instance_type = type(instance).__name__.lower()
    slug = slugify(instance.name)
    return "icons/%s/%s-%s" % (instance_type, slug, filename)