# -*- coding: utf-8 -*-
"""The Run Manager module

Contains classes and functions used to manage the runs and their tasks.

Routine Listings
----------------

See Also
--------

RunManager : Class to manage runs

Notes
-----

References
----------

Examples
--------

"""

from pathlib import Path


class RunManager:
    """Class to manage PPS Runs

    This Class initializes the on disk structures if necessary.

    Parameters
    ----------
    path_to_run_storage
        The path to the directory where all the run related information
        is stored. Typically, there will be multiple processing
        steps/tasks applied to a single run and each will have its data
        stored in a single subdirectory.

    Attributes
    ----------
    path_storage

    Raises
    ------
    ValueError
        If the parameter has the incorrect type

    Examples
    --------
    >>> import lip_pps_run_manager as RM
    >>> John = RM.RunManager("Run0001")

    """

    _path_storage = Path(".")
    """Internal copy of the directory for the run related information

    Do not use this attribute, use the associated property
    """

    @property
    def path_storage(self):
        """The path storage property getter method

        This method fetches the path_storage internal attribute

        Returns
        -------
        Path
            The path to the directory where the run information
            is stored.
        """
        return self._path_storage

    # @path_storage.setter
    # def path_storage(self, value):
    #    """
    #    This is the setter method
    #    where I can check it's not assigned a value < 0
    #    """
    #    self._path_storage = value

    def __init__(self, path_to_run_storage: Path):
        if type(path_to_run_storage) != Path:
            raise ValueError("The path_to_run_storage must be a Path type object")
        self.path_storage = path_to_run_storage
