import os
from setuptools import setup, find_packages

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser



# Get some values from the setup.cfg
conf = ConfigParser()
conf.read(['setup.cfg'])
metadata = dict(conf.items('metadata'))

PACKAGENAME = metadata.get('package_name', 'subtools')
DESCRIPTION = metadata.get('description', '')
LONG_DESCRIPTION = metadata.get('long_description', '')
AUTHOR = metadata.get('author', 'Ivan Sharankov')
AUTHOR_EMAIL = metadata.get('author_email', '')
LICENSE = metadata.get('license', 'unknown')
URL = metadata.get('url', 'https://github.com/iisharankov/Effelsberg')
__minimum_python_version__ = metadata.get("minimum_python_version", "3.5")

if os.path.exists('README.md'):
    with open('README.md') as f:
        LONG_DESCRIPTION = f.read()


with open("README.md", "r") as md_file:
    long_description = md_file.read()

setup(
    name=PACKAGENAME,
    version='0.0.1',
    packages=find_packages(),
    # package_dir={'subtools': 'src'},
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    license=LICENSE,
    entry_points={
        "console_scripts": [
            "subreflector_program = subtools.subreflector_start_server:main",
            "subreflector_mockserver = subtools.mock_start_server:main",
            ]},
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    zip_safe=False,
    python_requires='>={}'.format(__minimum_python_version__),
)

