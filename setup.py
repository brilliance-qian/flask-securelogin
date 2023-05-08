from setuptools import setup
import setuptools
import os


def read_content(filename):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    with open(file_path, "r") as fh:
        file_contents = fh.read()
    return file_contents


setup(
    name='flask-securelogin',
    version='0.1.0',
    description='A Flask-based installable library that provides secure login capabilities with SMS and auth tokens.',
    long_description=read_content("README.rst"),
    long_description_content_type="text/markdown",
    url='https://github.com/brilliance-qian/flask-securelogin',
    author='Brilliance Qian',
    license_files=('LICENSE.txt',),
    packages=setuptools.find_packages(),
    install_requires=[
        'aiohttp',
        'aiohttp-retry',
        'aiosignal',
        'alembic',
        'async-timeout',
        'attrs',
        'Babel',
        'bcrypt',
        'certifi',
        'charset-normalizer',
        'click',
        'exceptiongroup',
        'Flask',
        'flask-babel',
        'flask-blueprint',
        'Flask-JWT-Extended',
        'Flask-Migrate',
        'Flask-SQLAlchemy',
        'frozenlist',
        'greenlet',
        'idna',
        'importlib-metadata',
        'importlib-resources',
        'iniconfig',
        'itsdangerous',
        'Jinja2',
        'Mako',
        'MarkupSafe',
        'multidict',
        'packaging',
        'pluggy',
        'PyJWT',
        'pytest',
        'pytest-mock',
        'python-dateutil',
        'python-dotenv',
        'pytz',
        'requests',
        'six',
        'SQLAlchemy',
        'tencentcloud-sdk-python',
        'time-machine',
        'tomli',
        'twilio',
        'typing-extensions',
        'urllib3',
        'Werkzeug',
        'yarl',
        'zipp',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
            "pytest-clarity",
            'mock;python_version>="3.7"']
    }
)
