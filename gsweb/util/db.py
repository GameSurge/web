import os
from importlib import import_module

import pkg_resources


def import_all_models(package_name):
    """Import all modules inside 'models' folders of a package.

    The purpose of this is to import all SQLAlchemy models when the
    application is initialized so there are no cases where models
    end up not being imported e.g. because they are only referenced
    implicitly in a relationship instead of being imported somewhere.

    :param package_name: Top-level package name to scan for models.
    """
    distribution = pkg_resources.get_distribution(package_name)
    package_root = os.path.join(distribution.location, package_name)
    modules = []
    for root, dirs, files in os.walk(package_root):
        if os.path.basename(root) == 'models':
            package = os.path.relpath(root, package_root).replace(os.sep, '.')
            modules += ['{}.{}.{}'.format(package_name, package, name[:-3])
                        for name in files
                        if name.endswith('.py') and name != '__init__.py' and not name.endswith('_test.py')]

    for module in modules:
        import_module(module)
