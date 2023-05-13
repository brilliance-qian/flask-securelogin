Flask-securelogin
====================

Flask-securelogin is a library providing flask-based REST API services for account authentication with strong security protection.

When developers build a service for mobile app or for web, one important thing they have to consider is to build an authentication for their customers. Most developers would choose password-based login design and session-cooke-based authentication because it is easy to implement.

Unfortunately password-based authentication is a vulnerable design. Their customers could be victims of many security attacks: brutal force attack, phishing attack, password-leak if the web service didn't design their account security protection carefully. Besides, password-based authentciation is also a hassle to customers. For better security, the web service provider usually would ask their customers to have a complex password that must be 12+ charactors long and is with combination of uppercase, lowercase letters, digits and special charactors. This kind of password is usally hard to remember. Some customers might write it down somewhere, which is not a good approach on account security. Some customers might use a same password across many websites as people may have accounts on dozens of websites and it is hard to keep and remember different password per website. This is also not a good approach on account security. To enhance the security, many websites then ask their customers to provide multiple-factor-authentication (MFA), which make the system complicated and the login process less user friendly. Besides, account recovery from forget-password is also a painful process for customers.

Flask-securelogin provides a SMS-based passwordless authentication. The phone number is the customer's userid. After registration, when a customer is trying to login, just enter the phone number. The flask-securelogin sends SMS/OTP code to the customer. After SMS verification, the authentication is done. No password. No worry about phishing attack, brutal force attack or password leak. No worry about forgetting password. Concise and secure.

Installation
====================
To install the latest release on `PyPI <https://pypi.org/project/flask-securelogin>`_ 

simply run:

.. code:: text

    pip3 install flask-securelogin

Or to install the latest development version, run:

.. code:: text

    git clone git@github.com:brilliance-qian/flask-securelogin.git
    cd flask-securelogin
    python3 setup.py install
  
Quick Tutorial
====================
Flask-securelogin provides a set of authentication APIs that can be seamlessly integrated to your REST API service. In your flask application, just simply add a few lines then the whole set of APIs will be ready to support account registration and login.

Please refer to the `tutorial doc <https://github.com/brilliance-qian/flask-securelogin/blob/main/docs/tutorial.rst>`_  for more details.
