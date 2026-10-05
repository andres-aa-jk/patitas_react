from django.apps import apps as global_apps
from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.auth.management import create_permissions
from django.contrib.contenttypes.apps import ContentTypesConfig
from django.db.models.signals import post_migrate


def create_mongo_permissions(app_config, **kwargs):
    kwargs["apps"] = global_apps
    create_permissions(app_config, **kwargs)


class MongoAdminConfig(AdminConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAuthConfig(AuthConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"

    def ready(self):
        super().ready()
        post_migrate.disconnect(
            dispatch_uid="django.contrib.auth.management.create_permissions"
        )
        post_migrate.connect(
            create_mongo_permissions,
            dispatch_uid="django.contrib.auth.management.create_permissions",
        )


class MongoContentTypesConfig(ContentTypesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"