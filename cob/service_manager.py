import redis

_DISABLED = {'enabled': False}

class Services:

    redis = None

    def __init__(self, project):

        service_config = project.config.get('services')
        if service_config is not None:
            if not isinstance(service_config, dict):
                service_config = {service_name: {'enabled': True} for service_name in service_config}
            service_config = service_config.copy()

            if service_config.pop('redis', _DISABLED).get('enabled', True):
                self.redis = redis.Redis('redis' if project.is_dockerized() else None)


class ServiceProxy:

    def __getattr__(self, attr):
        if not attr.startswith('_'):
            project = get_project()

            return getattr(project.services, attr)
        return super().__getattribute__(attr)


services = ServiceProxy()

from .project import get_project
