"""
File containing all tests related to the pdffile.py classes and functions.
"""
# Imports
import os
import pytest
from .pdffile import PDFFileList, PDFFile, PDFPage
from collections.abc import Generator
from pdfminer.layout import LTPage

TEST_DIR = os.path.join(os.getcwd(), 'test_files')


class TestPDFFileList:
    """
    Class for testing PDFFileList instances
    """
    def test_instantiation(self):
        """
        Tests PDFFileList object instantiation including property testing
        """
        pdf_list = PDFFileList(TEST_DIR)
        assert isinstance(pdf_list, PDFFileList)
        assert pdf_list.directory == TEST_DIR
        assert len(pdf_list) == 6
        assert isinstance(pdf_list.files, Generator)
        for file in pdf_list.files:
            assert isinstance(file, PDFFile)

    def test_init_raise_error(self):
        """
        Tests error raising in __init__.
        """
        with pytest.raises(TypeError):
            PDFFileList(2)
        with pytest.raises(ValueError):
            PDFFileList('boom')


class TestPDFFile:
    """
    Class for testing PDFFile instances
    """
    def test_instantiation(self):
        """
        Tests object instantiation including property testing
        """
        file_list = [file for file in os.listdir(TEST_DIR)]
        for file in file_list:
            if not file.endswith('.pdf'):
                with pytest.raises(ValueError):
                    PDFFile(TEST_DIR, file)
            else:
                pdf_file = PDFFile(TEST_DIR, file)
                assert isinstance(pdf_file, PDFFile)
                assert pdf_file.directory == TEST_DIR
                assert pdf_file.name == file
                assert pdf_file.full_path == os.path.join(TEST_DIR, file)
                assert isinstance(pdf_file.pages, Generator)

    def test_file_year(self):
        """
        Tests year property.
        """
        file_name = 'BHP 2016 TTC.pdf'
        pdf_file = PDFFile(TEST_DIR, file_name)
        assert pdf_file.year == 2016


class TestPDFPage:
    """
    Class for testing PDFPage objects
    """
    file_name = 'BHP 2016 TTC.pdf'

    def test_instantiation(self):
        """
        Tests object instantiation including property testing.
        """
        file = PDFFile(TEST_DIR, self.file_name)
        page = PDFPage(next(file.pages))
        assert isinstance(page, PDFPage)
        assert isinstance(page.page, LTPage)
        assert isinstance(page.text, str)
        assert page.number == 1

    def test_init_raise_error(self):
        """
        Tests if passing an invalid parameter in class constructor raises an error
        """
        with pytest.raises(TypeError):
            PDFPage(self.file_name)
