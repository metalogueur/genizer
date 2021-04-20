# extractor.py
#
# Copyright (C) 2021 Benoit Hamel, Bibliothèque, HEC Montréal
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# This script is used to go through a directory's .pdf files, extract their text and parse every sentence.

# Imports
import os.path
import numpy as np
import pandas as pd
import re
import spacy
from classes.parser import GenizerParser
from classes.pdffile import PDFFileList, PDFPage
from progress.bar import Bar
from spacy.tokens import Doc

# Globals
EXCEL_FILE_NAME = 'tax_information.xlsx'
EXCEL_MAX_ROWS = 1048574    # Two less than reality to include header row
SCRIPT_NAME = 'PDF Text Extractor and Parser, aka The Genizer'
SCRIPT_VERSION = '0.1'
TABLE_DATA_PATTERN = r'(\(?(\d{1,3},)*\d{1,3}(\.\d+)?\)?)(\n(\(?(\d{1,3},)*\d{1,3}(\.\d+)?\)?))+'


def main():
    """ The main function of the script """
    parser = GenizerParser(SCRIPT_NAME, SCRIPT_VERSION)

    try:
        args = parser.parse_args()
        excel_file = os.path.join(args.path_to_dir, EXCEL_FILE_NAME)

        if args.verbose:
            print("Starting script...")
        if not args.clean:
            data = extract_text(args.path_to_dir, args.spacy, args.verbose)
        else:
            data, excel_file = clean_excel_file(args.path_to_dir, args.verbose)
        save_to_excel(data, excel_file, args.verbose)

        if args.verbose:
            print("End of script.")

    except (TypeError, FileNotFoundError) as e:
        print(e.strerror)
        return
    except Exception as e:
        print("Unexpected Error:", e)
        return


def extract_text(path_to_dir: str, use_spacy: bool = False, verbose: bool = False) -> pd.DataFrame:
    """
    Extracts text from .pdf files, stores it in a dict with file data and returns it.

    :param path_to_dir: The path to the directory containing the .pdf files
    :type path_to_dir:  str
    :param use_spacy:   Flag for using Spacy in sentence parsing
    :type use_spacy:    bool
    :param verbose:     The level of output verbosity
    :type verbose:      bool
    :returns:           All extracted text and file data in a DataFrame
    """
    if not isinstance(path_to_dir, str):
        raise TypeError("path_to_dir must be in string format.")
    if not os.path.isdir(path_to_dir):
        raise FileNotFoundError("path_to_dir must be a valid directory")
    if not isinstance(verbose, bool):
        raise TypeError("verbose must be a boolean.")

    # DataFrame / Excel file columns
    file_data = {
        'source': [],
        'year': [],
        'page': [],
        'group': [],
        'disclosure': [],
        'table_data': []
    }

    file_list = PDFFileList(path_to_dir)

    if verbose:
        print(f"Found {len(file_list)} files in {path_to_dir}.")
        print("Starting text extraction...")
        if use_spacy:
            print("Using Spacy to parse text. This may take a while...")

    if use_spacy:
        nlp = spacy.load("en_core_web_sm")
    else:
        nlp = None

    bar = Bar('Extracting', max=len(file_list))

    # For each .pdf file in the files' directory, we extract the file's pages and parse the text
    for file in file_list.files:

        for page in file.pages:
            the_page = PDFPage(page)
            if use_spacy:
                sentence_list, table_data = parse_text(nlp(the_page.text))
            else:
                sentence_list = [sentence for sentence in the_page.text.split('\n') if sentence and sentence != ' ']
                table_data = [np.nan] * len(sentence_list)
            file_data['source'] += [file.name] * len(sentence_list)
            file_data['year'] += [file.year] * len(sentence_list)
            file_data['page'] += [the_page.number] * len(sentence_list)
            file_data['group'] += [np.nan] * len(sentence_list)
            file_data['disclosure'] += sentence_list
            file_data['table_data'] += table_data

        bar.next()

    bar.finish()

    if verbose:
        print("Finished extraction...")

    return pd.DataFrame(file_data)


def parse_text(doc: Doc) -> [list, list]:
    """
    Parses text using Spacy and returns a list of sentences and rows of table data.

    :param doc:    The text to parse
    :type doc:     Doc
    :returns:      The list of sentences and table data rows in a tuple
    """
    if not isinstance(doc, Doc):
        raise TypeError("text must be in Spacy Doc format.")

    table_data_rows = []
    sentence_list = []

    for sentence in doc.sents:
        table_data = re.finditer(TABLE_DATA_PATTERN, sentence.text)
        sentence_without_data = re.sub(r'\s+', ' ', re.subn(TABLE_DATA_PATTERN, '', sentence.text)[0])
        if sentence_without_data != ' ':
            sentence_list.append(sentence_without_data)
            table_data_rows.append(np.nan)

        for data in table_data:
            dataset = data.group(0).split('\n')
            sentence_list += [np.nan] * len(dataset)
            table_data_rows += dataset

    return sentence_list, table_data_rows


def save_to_excel(data: pd.DataFrame, excel_file: str, verbose: bool = False) -> None:
    """
    Saves a DataFrame in Excel.

    :param data:        The data from the .pdf files
    :type data:         DataFrame
    :param excel_file:  The full path to the Excel file
    :type excel_file:   str
    :param verbose:     The level of output verbosity
    :type verbose:      bool
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a Pandas DataFrame.")
    if not isinstance(excel_file, str):
        raise TypeError("excel_file must be passed as a string.")
    if not isinstance(verbose, bool):
        raise TypeError("verbose must be a boolean.")

    if verbose:
        print("Saving data to Excel...")

    if data.size > EXCEL_MAX_ROWS:
        if verbose:
            print(f"Data contains {data.size} rows. This may take a while to save...")
        sheet_name = 'Coding_'
        sheet_nbr = 0
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            while data.size > 0:
                sub_df = data[:EXCEL_MAX_ROWS]
                sub_df.to_excel(writer, sheet_name=f"{sheet_name}{sheet_nbr}", index=False)
                data.drop(sub_df.index, inplace=True)
                data.reset_index(drop=True, inplace=True)
                sheet_nbr += 1
    else:
        data.to_excel(excel_file, sheet_name='Coding', index=False)
    if verbose:
        print(f"Data saved in {excel_file}.")


def clean_excel_file(path: str, verbose: bool = False) -> [pd.DataFrame, str]:
    """
    Extracts data from an Excel file and concatenates sentences manually grouped by end user.

    :param path:    The full path to the Excel file or its directory.
    :type path:     str
    :param verbose: The level of output verbosity
    :param verbose: bool
    :returns:       The cleaned-up dataframe and the path to the file
    """
    if not isinstance(path, str):
        raise TypeError("path must be in string format.")
    if not (os.path.isdir(path) or os.path.isfile(path)):
        raise FileNotFoundError("path must be a valid directory or file.")
    if not isinstance(verbose, bool):
        raise TypeError("verbose must be a boolean.")

    if os.path.isdir(path):
        excel_file = os.path.join(path, 'tax_information.xlsx')
    else:
        excel_file = path

    if verbose:
        print("Getting data from Excel file...")
    raw_data = pd.read_excel(excel_file, sheet_name=None, engine='openpyxl')
    df_from_xl = pd.DataFrame()
    df_from_xl = df_from_xl.append([raw_data[key] for key in list(raw_data) if key.startswith('Coding')])

    df_without_na = df_from_xl.dropna(subset=['group']).copy()
    df_from_xl.drop(df_without_na.index, inplace=True)

    if verbose:
        print("Grouping sentences...")
    disclosures = df_without_na[['group', 'disclosure']]
    disclosures = disclosures.groupby('group').transform(''.join)
    df_without_na.drop(columns='disclosure', inplace=True)
    df_without_na['disclosure'] = disclosures['disclosure']
    df_without_na.drop_duplicates(subset=['group'], inplace=True)

    if verbose:
        print("Merging data...")
    df_from_xl = df_from_xl.append(df_without_na)
    df_from_xl.sort_index(inplace=True)
    df_from_xl['group'] = np.nan
    df_from_xl.reset_index(drop=True, inplace=True)

    return df_from_xl, excel_file


if __name__ == '__main__':
    main()
