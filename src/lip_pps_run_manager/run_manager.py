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

import datetime
from pathlib import Path

from lip_pps_run_manager import __version__


def clean_path(path_to_clean: Path) -> Path:
    """Clean a path from dangerous characters

    Some characters are not recommended/supported by a given filesystem.
    To make matters worse, the set of supported characters varies from
    operating system to operating system. In order to make sure this
    code is portable and that things remain compatible, we choose a
    subset of characters on which to limit the paths used. The subset is
    essentially all letters (lower and upper case), all numbers
    augmented with the dot, underscore and dash.

    Parameters
    ----------
    path_to_clean
        The path to the directory to clean

    Raises
    ------
    TypeError
        If the parameter has the wrong type

    Returns
    -------
    Path
        The `path_to_clean` path cleaned of all characters not part of
        the reduced set

    Examples
    --------
    >>> import lip_pps_run_manager.run_manager as RM
    >>> print(RM.clean_path(Path("/tmp/2@#_run")))
    """

    if not isinstance(path_to_clean, Path):
        raise TypeError("The `path_to_clean` must be a Path type object, received object of type {}".format(type(path_to_clean)))

    # SafeCharacters = {
    # 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
    # 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
    # 'W', 'X', 'Y', 'Z',
    # 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
    # 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
    # 'w', 'x', 'y', 'z',
    # '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.',
    # '_', '-'
    # }

    return Path(".")


def run_exists(path_to_directory: Path, run_name: str) -> bool:
    """Check if a given run already exists in a given directory

    Parameters
    ----------
    path_to_directory
        The path to the directory where to check if the run exists

    run_name
        The name of the run to check for

    Raises
    ------
    TypeError
        If either of the parameters has the wrong type

    Returns
    -------
    bool
        `True` if the run already exists, `False` if it does not exist.

    Examples
    --------
    >>> import lip_pps_run_manager.run_manager as RM
    >>> print(RM.run_exists(Path("."), "Run0001"))
    """

    if not isinstance(path_to_directory, Path):
        raise TypeError("The `path_to_directory` must be a Path " "type object, received object of type {}".format(type(path_to_directory)))
    if not isinstance(run_name, str):
        raise TypeError("The `run_name` must be a str " "type object, received object of type {}".format(type(run_name)))

    run_path = path_to_directory / run_name

    # TODO: Add check for invalid characters

    return (run_path / 'run_info.txt').is_file()


def create_run(path_to_directory: Path, run_name: str) -> Path:
    """Create a new run in a given directory

    Parameters
    ----------
    path_to_directory
        The path to the directory where to create the run

    run_name
        The name of the run to create

    Raises
    ------
    TypeError
        If either of the parameters has the wrong type

    RuntimeError
        If the run directory already exists

    Returns
    -------
    Path
        The path to the creaated run.

    Examples
    --------
    >>> import lip_pps_run_manager.run_manager as RM
    >>> print(RM.create_run(Path("."), "Run0001"))
    """

    if not isinstance(path_to_directory, Path):
        raise TypeError("The `path_to_directory` must be a Path " "type object, received object of type {}".format(type(path_to_directory)))
    if not isinstance(run_name, str):
        raise TypeError("The `run_name` must be a str " "type object, received object of type {}".format(type(run_name)))

    run_path = path_to_directory / run_name

    # TODO: Add check for invalid characters

    if run_path.is_dir():
        raise RuntimeError(
            "Unable to create the run '{}' in '{}' because a directory with that name already exists.".format(run_name, path_to_directory)
        )

    run_path.mkdir(parents=True)

    with open(run_path / "run_info.txt", "w") as out_file:
        out_file.write(
            "This directory contains data for the run '{}', created by the RunManager v{} on {}".format(
                run_name, __version__, datetime.datetime.now()
            )
        )

    return run_path


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
    path_directory

    Raises
    ------
    TypeError
        If the parameter has the incorrect type

    Examples
    --------
    >>> import lip_pps_run_manager as RM
    >>> John = RM.RunManager("Run0001")

    """

    _path_directory = Path(".")

    def __init__(self, path_to_run_directory: Path):
        if not isinstance(path_to_run_directory, Path):
            raise TypeError(
                "The `path_to_run_directory` must be a Path " "type object, received object of type {}".format(type(path_to_run_directory))
            )
        self._path_directory = path_to_run_directory

    @property
    def path_directory(self) -> Path:
        """The path directory property getter method

        This method fetches the path_directory internal attribute,
        which contains the path to the directory containing the run
        information for this run.

        Returns
        -------
        Path
            The path to the directory where the run information
            is stored.
        """
        return self._path_directory

    # @path_directory.setter
    # def path_directory(self, value):
    #    """
    #    This is the setter method
    #    where I can check it's not assigned a value < 0
    #    """
    #    self._path_directory = value

    @property
    def run_name(self) -> str:
        """The name of the run"""
        return self._path_directory.parts[-1]
