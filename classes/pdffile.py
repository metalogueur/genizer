"""
pdffile.py

File containing all classes related to PDF files.
"""

# Imports
import os
import re

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTPage, LTTextContainer


class PDFFileList:
    """ Class PDFFileList

    Creates a list of PDF files contained in a valid directory.
    """

    def __init__(self, path_to_files: str):
        """
        Class constructor

        :param path_to_files:   The directory path to the PDF files
        :type path_to_files:    str
        """
        self.directory = path_to_files

    def __str__(self) -> str:
        """
        :return: The string representation of the PDFFileList object.
        """
        return f"'{self.directory}' contains {len(self)} PDF files."

    def __repr__(self) -> str:
        """
        :return: The string representation of the object's instantiation.
        """
        return f"PDFFileList(path_to_files='{self.directory}')"

    def __len__(self) -> int:
        """
        :return: The number of .pdf files in self.directory
        """
        return len([pdf_file for pdf_file in os.listdir(self.directory) if pdf_file.endswith('.pdf')])

    @property
    def directory(self) -> str:
        """
        :return: The directory path to the PDF files
        """
        return self._directory

    @directory.setter
    def directory(self, path_to_files: str) -> None:
        """
        Sets the directory after making verifications as to whether or not the path is a valid directory.
        
        :param path_to_files:   The directory path
        :type path_to_files:    str
        """
        if not isinstance(path_to_files, str):
            raise TypeError("path_to_files must be a valid string.")
        if not os.path.isdir(path_to_files):
            raise ValueError("path_to_files must be a valid directory.")

        self._directory = path_to_files

    @property
    def files(self):
        """
        Generator property that yields .pdf file names from self.directory

        :return:    The generator
        """
        for file in os.listdir(self.directory):
            if file.endswith('.pdf'):
                yield PDFFile(self.directory, file)


class PDFFile:
    """
    Class PDFFile
    """

    def __init__(self, directory: str, file_name: str):
        """
        Class constructor

        :param directory:   The directory containing the file
        :type directory:    str
        :param file_name:   The name of the file and its extension
        :type file_name:    str
        """
        self.directory = directory
        self.name = file_name

    def __str__(self) -> str:
        """
        :return: The string representation of the PDF file
        """
        return self.full_path

    def __repr__(self) -> str:
        """
        :return: The string representation of the object's instantiation
        """
        return f"PDFFile(directory='{self.directory}', file_name='{self.name}')"

    @property
    def directory(self) -> str:
        """
        :return: The directory path to the PDF files
        """
        return self._directory

    @directory.setter
    def directory(self, path_to_file: str) -> None:
        """
        Sets the directory after making verifications as to whether or not the path is a valid directory.

        :param path_to_file:   The directory path
        :type path_to_file:    str
        """
        if not isinstance(path_to_file, str):
            raise TypeError("path_to_files must be a valid string.")
        if not os.path.isdir(path_to_file):
            raise ValueError("path_to_files must be a valid directory.")

        self._directory = path_to_file

    @property
    def name(self) -> str:
        """
        :return: The file name with its extension.
        """
        return self._name

    @name.setter
    def name(self, file_name) -> None:
        """
        Sets the name after making verifications as to whether or not the name leads to a valid file.

        :param file_name:   The name of the file
        :type file_name:    str
        """
        if not isinstance(file_name, str):
            raise TypeError("file_name must be a valid string.")
        if os.path.isfile(file_name):
            raise ValueError(f"File {file_name} doesn't exist.")
        if not file_name.endswith('.pdf'):
            raise ValueError(f"File {file_name} must be a PDF file.")

        self._name = file_name

    @property
    def full_path(self) -> str:
        """
        :return: The full path to the PDF file.
        """
        return os.path.join(self.directory, self.name)

    @property
    def year(self) -> int:
        """
        :return: Returns the year written in the file name or 0 (zero) if not present
        """
        year_pattern = '[0-9]{4}'
        match = re.search(year_pattern, self.name)
        if match:
            return int(match.string[match.start():match.end()])

        return 0

    @property
    def full_text(self) -> str:
        """
        :return: Returns the whole text contained in the file in str format.
        """
        full_text = []
        for page in self.pages:
            the_page = PDFPage(page)
            full_text.append(the_page.text)

        return ''.join(full_text)

    @property
    def pages(self):
        """
        :return: The generator object yielding LTPages
        """
        return extract_pages(self.full_path)


class PDFPage:
    """
    Class PDFPage
    """
    def __init__(self, page: LTPage):
        """
        Class constructor

        :param page:    A page extracted from a PDF file
        :type page:     LTPage
        """
        self.page = page

    @property
    def page(self) -> LTPage:
        """
        :return: The LTPage object provided at instantiation.
        """
        return self._page

    @page.setter
    def page(self, page: LTPage) -> None:
        """
        Sets the page property after verifying that the parameter is an LTPage

        :param page:    A page extracted from a PDF file
        :type page:     LTPage
        """
        if not isinstance(page, LTPage):
            raise TypeError("page argument must be a valid LTPage object.")

        self._page = page

    @property
    def number(self):
        """
        :return: The page number in the pdf file.
        """
        return self.page.pageid

    @property
    def text(self) -> str:
        """
        :return: The text extracted from the page.
        """
        page_text = []
        for part in self.page:
            if isinstance(part, LTTextContainer):
                page_text.append(part.get_text())

        return ''.join(page_text)
