from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys
import os
import codecs
import re

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

long_description = read('README.txt')


class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        # nosetests --with-coverage --cover-package=pmp_api
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import nose
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)

setup(
    name = 'py3-pmp-wrapper',
    packages = ['pmp_api', 
                'pmp_api.core',
                'pmp_api.recipes',
                'pmp_api.collectiondoc',
                'pmp_api.collectiondoc.stored_profiles', 
                'pmp_api.utils'],
    version = find_version('pmp_api', '__init__.py'),
    description = 'Python3 Wrapper Interface for Public Media Platform API',
    author = 'Erik Aker',
    author_email = "eraker@gmail.org",
    url = "https://github.com/KPBS/py3-pmp-wrapper",
    license = "GNU General Public License v2",
    download_url = "https://github.com/KPBS/py3-pmp-wrapper.git",
    keywords = ["pmp", "hateoas"],
    tests_require=['tox','nose', 'coverage'],
    cmdclass = {'test': Tox},
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries"
        ],
    install_requires=[
        "requests>=2.2.1",
        "six>=1.7.3",
        "uritemplate",
        "pelecanus"
    ],
    long_description = long_description
)
