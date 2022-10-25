
Changelog
=========

Current (2022-10-24)
--------------------

* Added common functions for the instruments
* Started adding SetupManager to hold the experimental setup
* Started tests for instruments
* Added library version to task report file

0.2.1 (2022-10-24)
------------------

* Added the version of LIP-PPS-Run-Manager to the task script backup
* Added the possibility to load bot details from a config file using names. Names override explicit tokens and ids
* Started adding a class to handle a Keithley 6487 device

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
