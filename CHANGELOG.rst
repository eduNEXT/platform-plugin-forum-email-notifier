Change Log
##########

..
   All enhancements and patches to forum_email_notifier will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
**********

*

0.3.2 - 2023-10-24
**********************************************

Changed
=======

* Used recursive-include to add ``locale`` folder.


0.3.1 - 2023-10-23
**********************************************

Changed
=======

* Added ``locale`` folder in MANIFEST.in.


0.3.0 - 2023-10-23
**********************************************

Added
=====
* Added templates of individual and digest emails.
* Added README with cron and cronjob information.
* Added documentation in instructor dashboard.
* Added translation support with Spanish translation (es_ES) and (es_419).


0.2.0 - 2023-10-09
**********************************************

Added
=====
* Added email notification for forum updates.
* Added instructor dashboard integration.
* Added ``forum_digest`` command to trigger digest notification.


0.1.0 - 2023-09-28
**********************************************

Added
=====

* First release on PyPI.
