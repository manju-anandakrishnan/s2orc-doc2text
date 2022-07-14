# Convert scientific papers to S2ORC TEXT

This project is forked from allen ai - https://github.com/allenai/s2orc-doc2json, which converts PDFs to JSON using Grobid and a custom TEI.XML to JSON parser. The original project converts TEI.XML to JSON parser (`grobid2json`). 
In addition, this project converts the TEI.XML to text files, after it is being parsed to the Paper object in JSON format conversion ('doc2text'). It also invokes two versions of the Grobid service, the 0.6.1 version (for abstract, body text extracts) and the 0.7.1 sourced in the cloud.science-miner.com/grobid host for tables, figures and services. (This is done so, because of minor issues in raw text conversion in 0.7.1 version) 

## Setup your environment

NOTE: Conda is shown but any other python env manager should be fine

Go [here](https://docs.conda.io/en/latest/miniconda.html) to install the latest version of miniconda.

Then, create an environment:

```console
conda create -n doc2json python=3.8 pytest
conda activate doc2json
pip install -r requirements.txt
python setup.py develop
```

## PDF Processing

The current `grobid2json` tool uses Grobid to first process each PDF into XML, then extracts paper components from the XML.

### Install Grobid

You will need to have Java installed on your machine. Then, you can install your own version of Grobid and get it running, or you can run the following script:

```console
bash scripts/setup_grobid.sh
```

This will setup Grobid, currently hard-coded as version 0.6.1. Then run:

```console
bash scripts/run_grobid.sh
```

to start the Grobid server. Don't worry if it gets stuck at 87%; this is normal and means Grobid is ready to process PDFs.

The expected port for the Grobid service is 8070, but you can change this as well. Make sure to edit the port in both the Grobid config file as well as `grobid/grobid_client.py`.

### Process a PDF

Upload the pdf to be processed in the directory - doc2text/pdf_repo

```console
cd doc2text
python doc2text/process_pdf_text.py -i pdf_repo/ -t temp_dir/ -o text_repo/
```

This will generate a text file in the specified `text_repo`. 

## Citation

If you use this utility in your research, please cite:

```
@inproceedings{lo-wang-2020-s2orc,
    title = "{S}2{ORC}: The Semantic Scholar Open Research Corpus",
    author = "Lo, Kyle  and Wang, Lucy Lu  and Neumann, Mark  and Kinney, Rodney  and Weld, Daniel",
    booktitle = "Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics",
    month = jul,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.acl-main.447",
    doi = "10.18653/v1/2020.acl-main.447",
    pages = "4969--4983"
}
```

