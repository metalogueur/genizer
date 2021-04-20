"""
parser.py

File containing classes related to command-line argument parsing.
"""

# Imports
import argparse
import os


class GenizerParser(argparse.ArgumentParser):
    """
    Class for parsing command-line arguments from Nadia Genest's scripts.
    """

    parser_description = "Extracts text from a directory's .pdf files and parses their sentences."

    def __init__(self, script_name: str, script_version: str):
        """
        Class constructor

        :param script_name:     The name of the script called
        :type script_name:      str
        :param script_version:  The version of the script called
        :type script_version:   str
        """
        if not isinstance(script_name, str):
            raise TypeError("script_name must be a string.")
        if not isinstance(script_version, str):
            raise TypeError("script_version must be a string.")

        super(GenizerParser, self).__init__(description=self.parser_description)
        self.script_name = script_name
        self.script_version = script_version
        self.add_all_arguments()

    def add_all_arguments(self):
        """Adds all parser arguments in one call."""
        self.add_argument('-V', '--version', help='show script version and exit', action='version',
                          version=f"{self.script_name} version {self.script_version}")
        self.add_argument('path_to_dir', help='a valid directory or file path', type=get_path)
        self.add_argument('-c', '--clean', help='clean Excel file by grouping sentences', action='store_true')
        self.add_argument('-s', '--spacy', help='use Spacy to parse sentences', action='store_true')
        self.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')


def get_path(path_to_dir: str) -> str:
    """Returns the directory path string if it is a valid path. Raises an error otherwise.

        :param path_to_dir: A valid path to a directory or file.
        :type path_to_dir: str
        :returns: the directory or file path string
        :rtype: str
        """
    if not isinstance(path_to_dir, str):
        raise TypeError("path_to_dir must be a string.")
    if not (os.path.isdir(path_to_dir) or os.path.isfile(path_to_dir)):
        raise FileNotFoundError("path_to_dir must be a valid path to a directory or file.")

    return path_to_dir
