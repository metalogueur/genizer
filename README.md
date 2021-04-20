# The Genizer : PDF Text Extractor and Sentence Parser

This one-off script is used to extract text from a directory's PDF files
and parse it in order to have individual sentences listed in an Excel spreadsheet
with other file data.

## Installation
Python 3.8 and over is required to run this script. It has not been tested with older
distributions.

Once Python is installed, simply download the `master.zip` archive and extract its contents
in a working directory.

Open a Terminal of PowerShell window in the `genizer/` directory and run the
following command to install the script's dependencies:

`$ pip install -r requirements.txt`

To make sure everything is installed properly, run the following command. You should see
this output:

```
$ python extractor.py -V
> PDF Text Extractor and Parser, aka The Genizer version 0.1
```

## Usage

To run this script, you must write the following command from the Terminal or PowerShell 
window inside the `pdf_ocr_inspector/` directory:

`$ python extractor.py path_to_directory [-c] [-s] [-v]`

- `path_to_directory` must be a valid path enclosed in quotes;
- `-c` is an optional parameter to clean (regroup) sentences when Spacy is not used
  as the sentence parser;
- `-s` is an optional parameter to use Spacy as the default sentence parser;  
- `-v` is an optional parameter to increase verbosity in the Terminal output.

The script will go through each .pdf file, extracting text, and will parse it to isolate individual sentences and
link them to their original file and page in that file. The user can choose between using Spacy to parse sentences or
just extracting plain text from the files and group sentences manually in the resulting Excel file.

### Spacy as default parser

When using Spacy, the script will use the module's [Sentence Segmentation](https://spacy.io/usage/linguistic-features#sbd)
feature to isolate individual sentences. Accuracy and order are not guaranteed as PDF files are not as structured as HTML
or plain text, for example (IMHO), but Spacy does an excellent job nonetheless in segmenting sentences.

Please note that Spacy is used _out-of-the-box_ in this Script, i.e. no further training models are pushed in the
pipeline, so results may vary.

Also, when using this option, the script extracts numeric table data from sentences (as Spacy often regroups data in individual
sentences) and regroups it in another column.

### Plain text extraction

When using Spacy results in too many inaccuracies, you can run the script without the `-s` option to extract text.
Sentences will be replaced by lines of text. In the resulting Excel file, you will then be able to regroup sentences
manually by indicating a unique id in the `group` column for each line that represents a sentence.

Once that job is done, all you have to do is rerun the `python extractor.py` command in the Terminal, replacing
the `path_to_directory` argument with the full path to the Excel file and using the `-c` option. The script will
concatenate lines using the unique ids and delete unnecessary lines, leaving ungrouped lines unchanged.
