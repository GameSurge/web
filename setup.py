import ast
import re
from pip.req import parse_requirements
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('gsweb/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(f.read().decode('utf-8')).group(1)))

requirements = [str(x.req) for x in parse_requirements('requirements.txt', session=False)]

setup(
    name='gsweb',
    version=version,
    description='The GameSurge website',
    url='https://github.com/GameSurge/web',
    download_url='https://github.com/GameSurge/web',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    install_requires=requirements
)
