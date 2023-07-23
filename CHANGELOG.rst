
Changelog
=========

Current (2023-07-23)
--------------------

0.2.3 (2023-07-23)
--------------------

* Added a backup_directory property to the RunManager
* Added the copy_file_to method to the RunManager
* Added the backup_file method to the RunManager

Not numbered (2022-10-24)
-------------------------

* Added a data_directory property to the RunManager

0.2.2 (2022-10-25)
------------------

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
