Forum Email Notifier
####################################


|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge| |status-badge|

Purpose
*******

This is a plugin for the Open edX platform that sends email notifications to
users when there are forum updates.

This plugin allows to configure notification digest frequency.

Getting Started
***************

Developing
==========

One Time Setup
--------------
.. code-block::

  # Clone the repository
  git clone git@github.com:eduNEXT/platform_plugin_forum_email_notifier.git
  cd platform_plugin_forum_email_notifier

  # Set up a virtualenv with the same name as the repo and activate it
  # Here's how you might do that if you have virtualenvwrapper setup.
  mkvirtualenv -p python3.8 platform_plugin_forum_email_notifier


Every time you develop something in this repo
---------------------------------------------
.. code-block::

  # Activate the virtualenv
  # Here's how you might do that if you're using virtualenvwrapper.
  workon platform_plugin_forum_email_notifier

  # Grab the latest code
  git checkout main
  git pull

  # Install/update the dev requirements
  make requirements

  # Run the tests and quality checks (to verify the status before you make any changes)
  make validate

  # Make a new branch for your changes
  git checkout -b <your_github_username>/<short_description>

  # Using your favorite editor, edit the code to make your change.
  vim ...

  # Run your new tests
  pytest ./path/to/new/tests

  # Run all the tests and quality checks
  make validate

  # Commit all your changes
  git commit ...
  git push

  # Open a PR and ask for review.

Deploying
=========

The email digest feature works by acumulating the notifications in a database table
per user, per course and per digest frequency. Then, a scheduled task is run to
send the notifications to the users.

As Open edX doesn't support celery beat for scheduled tasks, so we need to use
another tool to run them.

For tutor local installations we need to use cron to run the scheduled tasks.

An example of a cron job to run the scheduled tasks once every day at midnight:

.. code-block::

  0 0 * * * /bin/bash -l -c 'tutor local exec lms ./manage.py lms forum_digest --digest daily'

For tutor k8s installations we need to use a cronjob to run the scheduled tasks. The default
cronjob is configured to run the scheduled tasks once every day at midnight and can be found
in the folder ``tutor-plugins``. It's compatible with the Open edX release ``olive`` and
can be modified to work with other later releases.

License
*******

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

Contributing
************

Contributions are very welcome.
Please read `How To Contribute <https://openedx.org/r/how-to-contribute>`_ for details.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features.  However, please make sure
to have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

The Open edX Code of Conduct
****************************

All community members are expected to follow the `Open edX Code of Conduct`_.

.. _Open edX Code of Conduct: https://openedx.org/code-of-conduct/

People
******

The assigned maintainers for this component and other project details may be
found in `Backstage`_. Backstage pulls this data from the ``catalog-info.yaml``
file in this repo.

.. _Backstage: https://backstage.openedx.org/catalog/default/component/platform_plugin_forum_email_notifier

Reporting Security Issues
*************************

Please do not report security issues in public. Please email security@openedx.org.

.. |pypi-badge| image:: https://img.shields.io/pypi/v/platform_plugin_forum_email_notifier.svg
    :target: https://pypi.python.org/pypi/platform_plugin_forum_email_notifier/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/eduNEXT/platform_plugin_forum_email_notifier/workflows/Python%20CI/badge.svg?branch=main
    :target: https://github.com/eduNEXT/platform_plugin_forum_email_notifier/actions
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/eduNEXT/platform_plugin_forum_email_notifier/coverage.svg?branch=main
    :target: https://codecov.io/github/eduNEXT/platform_plugin_forum_email_notifier?branch=main
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/platform_plugin_forum_email_notifier/badge/?version=latest
    :target: https://docs.openedx.org/projects/platform_plugin_forum_email_notifier
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/platform_plugin_forum_email_notifier.svg
    :target: https://pypi.python.org/pypi/platform_plugin_forum_email_notifier/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/eduNEXT/platform_plugin_forum_email_notifier.svg
    :target: https://github.com/eduNEXT/platform_plugin_forum_email_notifier/blob/main/LICENSE.txt
    :alt: License

.. TODO: Choose one of the statuses below and remove the other status-badge lines.
.. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
