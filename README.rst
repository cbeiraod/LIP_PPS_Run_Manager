========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |github-actions| |travis| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/lip-pps-run-manager/badge/?version=latest
    :target: https://lip-pps-run-manager.readthedocs.io/
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.com/cbeiraod/LIP_PPS_Run_Manager.svg?branch=main
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/github/cbeiraod/LIP_PPS_Run_Manager

.. |github-actions| image:: https://github.com/cbeiraod/LIP_PPS_Run_Manager/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/cbeiraod/LIP_PPS_Run_Manager/actions

.. |requires| image:: https://requires.io/github/cbeiraod/LIP_PPS_Run_Manager/requirements.svg?branch=main
    :alt: Requirements Status
    :target: https://requires.io/github/cbeiraod/LIP_PPS_Run_Manager/requirements/?branch=main

.. |codecov| image:: https://codecov.io/gh/cbeiraod/LIP_PPS_Run_Manager/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://codecov.io/github/cbeiraod/LIP_PPS_Run_Manager

.. |version| image:: https://img.shields.io/pypi/v/lip-pps-run-manager.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/lip-pps-run-manager

.. |wheel| image:: https://img.shields.io/pypi/wheel/lip-pps-run-manager.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/lip-pps-run-manager

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/lip-pps-run-manager.svg
    :alt: Supported versions
    :target: https://pypi.org/project/lip-pps-run-manager

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/lip-pps-run-manager.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/lip-pps-run-manager

.. |commits-since| image:: https://img.shields.io/github/commits-since/cbeiraod/LIP_PPS_Run_Manager/v0.2.3.svg
    :alt: Commits since latest release
    :target: https://github.com/cbeiraod/LIP_PPS_Run_Manager/compare/v0.2.3...main



.. end-badges

Run Manager used in the LIP PPS software stack for handling data taking and analysis

* Free software: MIT license

Installation
============

::

    pip install lip-pps-run-manager

You can also install the in-development version with::

    pip install https://github.com/cbeiraod/LIP_PPS_Run_Manager/archive/main.zip


Documentation
=============


https://lip-pps-run-manager.readthedocs.io/en/latest/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
