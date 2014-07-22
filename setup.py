from distutils.core import setup

set(
    name = 'py3-pmp-wrapper',
    packages = ['pmp_api']
    version = '1.0.2',
    description = 'API Interface for Public Media Platform',
    author = 'Erik Aker',
    author_email = "eraker@gmail.org",
    url = "https://github.com/KPBS/py3-pmp-wrapper",
    download_url = "https://github.com/KPBS/py3-pmp-wrapper.git",
    keywords = ["pmp", "hateoas"],
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
    long_description = """\
Python3 Wrapper for PMP API
-------------------------------------


Authorization
    - Generate and revoking access credentials
    - Generate access tokens

Connecting
    - Use authorization objects to make requests of PMP API

This version requires Python 3 or later.
"""
)
