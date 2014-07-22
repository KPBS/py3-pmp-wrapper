from distutils.core import setup

setup(
    name = 'py3-pmp-wrapper',
    packages = ['pmp_api', 'pmp_api.core', 'pmp_api.utils', 'pmp_api.config'],
    version = '0.0.2',
    description = 'Wrapper Interface for Public Media Platform API',
    author = 'Erik Aker',
    author_email = "eraker@gmail.org",
    url = "https://github.com/KPBS/py3-pmp-wrapper",
    download_url = "https://github.com/KPBS/py3-pmp-wrapper.git",
    keywords = ["pmp", "hateoas"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries"
        ],
    install_requires=[
        "requests",
        "six"
    ],
    long_description = """\
Python3 Wrapper for PMP API
-------------------------------------


Client
    - Create a Public Media Platform API client and use it to receive docs

Authorization
    - Generate and revoke access credentials
    - Generate access tokens

Connecting
    - Use authorization objects to make requests of PMP API

This version requires Python 3 or later.
"""
)
