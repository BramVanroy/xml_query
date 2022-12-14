# Query Alpino XML with XPath

A basic script to query Alpino XML files for a given XPath construction. It looks for the XPath query
in all the XML files of the given input directory and writes the matching sentences to the output
directory. One output file per input file. 

Installation:

```shell
python -m pip install -r requirements.txt
```

Usage:

```
usage: main.py [-h] din dout xpath

Extract all sentences from given Alpino files that match with a given XPath query and write them to output files.

positional arguments:
  din         Directory that contains XML files with Alpino parses in them. All XML files in this directory will be queried against.
  dout        Output directory to write results to, one per input file.
  xpath       XPath query to use. Can be a string or a path to a file. In case of a file, its contents will be used as an XPath query

optional arguments:
  -h, --help  show this help message and exit
```

Example:

```shell
python main.py dir/with/alpino/xml output/dir file_with_xpath_query.txt
```

