
Changelog
=========

Current (2022-10-19)
--------------------

* Added the version of LIP-PPS-Run-Manager to the script backup

0.2.0 (2022-10-19)
------------------

* Added TelegramReporter class, to handle a connection to telegram via the bot API and to publish messages to it
* Integrated TelegramReporter into RunManager and TaskManager so that the status and progress of runs and tasks can be published to telegram for ease of monitoring
* Changed RunManager to use the 'with syntax', **this is a breaking change**
* Fixed some typos in the documentation

0.1.0 (2022-09-28)
------------------

* First fully functional version


0.0.0 (2022-09-27)
------------------

* First release on PyPI.
