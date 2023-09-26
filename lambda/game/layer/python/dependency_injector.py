from opyoid import Injector, Module


class DependencyInjector(Module):

    handlers = []
    dependencies = {}
    instance_cache = {}
    injector = None

    @classmethod
    def register_handler(cls, handler_cls):
        cls.handlers.append(handler_cls)

    @classmethod
    def register_dependency(cls, interface, instance):
        cls.dependencies[interface] = instance

    @classmethod
    def inject(cls, handler_cls):
        if cls.injector is None:
            cls.injector = Injector([DependencyInjector])
        if handler_cls not in cls.instance_cache:
            cls.instance_cache[handler_cls] = cls.injector.inject(handler_cls)
        return cls.instance_cache[handler_cls]

    def configure(self) -> None:
        for handler in self.handlers:
            self.bind(handler)
        for interface_cls, instance in self.dependencies.items():
            self.bind(interface_cls, to_instance=instance)
        