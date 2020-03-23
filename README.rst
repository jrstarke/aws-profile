aws-profile
===========

.. image:: https://img.shields.io/travis/jrstarke/aws-profile/master.svg?style=flat-square
    :target: https://travis-ci.org/jrstarke/aws-profile

.. image:: https://img.shields.io/coveralls/jrstarke/aws-profile/master.svg?style=flat-square
    :target: https://coveralls.io/r/jrstarke/aws-profile

.. image:: https://img.shields.io/pypi/v/aws-profile.svg?style=flat-square
    :target: https://pypi.python.org/pypi/aws-profile

.. image:: https://img.shields.io/pypi/pyversions/aws-profile.svg?style=flat-square
    :target: https://pypi.python.org/pypi/aws-profile

.. image:: https://img.shields.io/pypi/implementation/coveralls.svg?style=flat-square
    :target: https://pypi.python.org/pypi/aws-profile

Wrapper script to generate and pass AWS AssumeRole keys to other scripts


Usage
-----

There are two primary ways to use **aws-profile**, inline using arguments and with environment variables.

**Inline Profile Name**

`aws-profile [-p, --profile <profile name> -r, --region <region>] <command>`

**Profile Environment Variable**

`aws-profile --profile dev --region us-west-2 <command>`
or
`aws-profile -p dev -r us-west-2 <command>`

Options
-------

**AWS_CACHE**: Set the AWS_CACHE environment variable to control caching.
Use `AWS_CACHE=false` to disable caching, or any other value
(or unset) to keep caching enabled. When set to false the MFA
code will be requested every time.

Configuring Profiles
--------------------

`aws-profile` uses the built in profiles from the AWS CLI. For full details see `Named Profiles <https://docs.aws.amazon.com/cli/latest/userguide/cli-multiple-profiles.html>`_ in the AWS Documentation.

Here is an example of how to configure a profile for a role, with MFA::

    [profile my_profile]
    role_arn = arn:aws:iam::<account_id>:role/<role_name>
    source_profile = default
    mfa_serial = arn:aws:iam::<account_id>:mfa/<username>

Where `<account_id>` is your AWS Account ID, `<role_name>` is the name of the role you want to assume, and `<username>` is the username of the AWS User used fo your default profile.

Development
-----------

Clone from github (or preferably from your own fork)

``git clone https://github.com/jrstarke/aws-profile.git``

Create a clean virtual environment examples for virtualenv and pyenv with virtualenv wrapper

``virtualenv venv``
``source venv/bin/activate``

or

``pyenv virtualenv aws-profile``
``pyenv activate aws-profile``

Install the development dependencies

``pip install -e ".[dev]"``

Run the tests before making changes and then again before creating a pull request (There will be 3 warnings about external dependencies which can be ignored)

``pytest --cov=awsprofile --cov-report term-missing``

