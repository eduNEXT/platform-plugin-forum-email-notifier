Forum Email Notifier
####################################


|ci-badge| |license-badge| |status-badge|

Purpose
*******

This plugin for the Open edX platform sends email notifications to users when there are forum updates. It also allows
to configure notification digest frequency for the instructor.

Compatibility Notes
===================

+------------------+--------------+
| Open edX Release | Version      |
+==================+==============+
| Palm             | >= 0.3.0     |
+------------------+--------------+
| Quince           | >= 0.3.0     |
+------------------+--------------+
| Redwood          | >= 0.3.0     |
+------------------+--------------+

The settings can be changed in ``platform_plugin_forum_email_notifier/settings/common.py``
or, for example, in tutor configurations.

**NOTE**: the current ``common.py`` works with Open edX Palm, Quince and Redwood
version.

Dependencies
************

This plugin depends on the `following commit`_, which emits the forum events.
Depending on the version of Open edX you are using, it is necessary to make a
backport.

These changes are available from **Redwood** release.

.. _`following commit`: https://github.com/eduNEXT/edx-platform/commit/9e6502474482b8c5310ac069bd58f813fa3be73c

View from the Learning Management System (LMS)
**********************************************

.. image:: https://github.com/eduNEXT/platform-plugin-forum-email-notifier/assets/64440265/d4a3ad91-608f-48c7-b89c-1945cfb1955d
   :alt: Instructor panel integration


Configuring required in the Open edX platform
*********************************************

You must include the following setting in the LMS to enable the filter that will
display add the new tab for On Task:

.. code-block:: python

    OPEN_EDX_FILTERS_CONFIG = {
      "org.openedx.learning.instructor.dashboard.render.started.v1": {
          "fail_silently": False,
          "pipeline": [
            "platform_plugin_forum_email_notifier.extensions.filters.AddInstructorNotifierTab",
          ]
      },
    }

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

Tutor environments
------------------

To use this plugin in a Tutor environment, you must install it as a requirement of the ``openedx`` image. To achieve this, follow these steps:

.. code-block:: bash

    tutor config save --append OPENEDX_EXTRA_PIP_REQUIREMENTS=git+https://github.com/edunext/platform-plugin-forum-email-notifier@vX.Y.Z
    tutor images build openedx

Then, deploy the resultant image in your environment.

The email digest feature accumulates the notifications in a database table
per user, per course, and digest frequency. Then, a scheduled task is run to
send the notifications to the users.

As Open edX doesn't support Celery Beat for scheduled tasks, we need to use
another tool to run them.

For Tutor local installations, we must use `cron <https://en.wikipedia.org/wiki/Cron>`_ to run the scheduled tasks.

An example of a cron expression to run the scheduled tasks once every day at midnight:

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

Please do not report security issues in public. Please email security@edunext.co.

.. It's not required by our contractor at the moment but can be published later
.. .. |pypi-badge| image:: https://img.shields.io/pypi/v/platform_plugin_forum_email_notifier.svg
    :target: https://pypi.python.org/pypi/platform_plugin_forum_email_notifier/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/eduNEXT/platform-plugin-forum-email-notifier/actions/workflows/ci.yml/badge.svg?branch=main
    :target: https://github.com/eduNEXT/platform-plugin-forum-email-notifier/actions
    :alt: CI

.. |license-badge| image:: https://img.shields.io/github/license/eduNEXT/platform-plugin-forum-email-notifier.svg
    :target: https://github.com/eduNEXT/platform-plugin-forum-email-notifier/blob/main/LICENSE.txt
    :alt: License

.. TODO: Choose one of the statuses below and remove the other status-badge lines.
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Experimental-yellow
.. |status-badge| image:: https://img.shields.io/badge/Status-Maintained-brightgreen
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Deprecated-orange
.. .. |status-badge| image:: https://img.shields.io/badge/Status-Unsupported-red
