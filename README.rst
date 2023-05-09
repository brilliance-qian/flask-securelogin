*******************
flask-securelogin
*******************

Description
-------------------
Flask-securelogin is a library providing flask-based security authentication REST API services.

Installation
-------------------
To install the latest release on `PyPI <https://pypi.org/project/flask-securelogin/>`_,
simply run:
::
  pip3 install flask-securelogin
Or to install the latest development version, run:
::
  git clone git@github.com:brilliance-qian/flask-securelogin.git
  cd flask-securelogin
  python3 setup.py install
  
Quick Tutorial
-------------------
Flask-securelogin provides a set of authentication APIs that can be seamlessly integrated to your REST API service. In your flask application, just simply add a few lines then the whole set of APIs will be ready to support account registration and login.

Create the environment
::
  $ mkdir sample_api
  $ cd sample_api
  $ python3 -m venv venv
  $ source venv/bin/activate
  $ pip install flask-securelogin
  $ pip freeze > requirements.txt
  
Directory tree structure
::
    sample_api
    ├── app
    │   ├── __init__.py
    │   └── routes.py
    ├── entry.py
    ├── config.py
    └── tests
        └── test_routes.py

app/__init__.py
::
