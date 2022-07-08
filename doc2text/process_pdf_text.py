import os
import argparse
import time
import glob

from typing import Optional, Dict
from io import StringIO
from doc2json.grobid2json.grobid.grobid_client import GrobidClient
from doc2json.grobid2json.tei_to_json import convert_tei_xml_file_to_s2orc_json

BASE_TEMP_DIR = 'temp'
BASE_OUTPUT_DIR = 'text_repo'
BASE_LOG_DIR = 'log'
GROBID_VERSION_6_1 = 'v_0.6.1'
GROBID_VERSION_7_1 = 'v_0.7.1'
GROBID_CONFIG_V_7_1 = {
    "protocol":"https",
    "grobid_server": "cloud.science-miner.com/grobid",
    "grobid_port":None,
    "batch_size": 1000,
    "sleep_time": 5,
    "generateIDs": False,
    "consolidate_header": False,
    "consolidate_citations": False,
    "include_raw_citations": True,
    "include_raw_affiliations": False,
    "max_workers": 2,
}

class PaperAsText:

    def __init__(self,paper,version):
        self.paper = paper
        self.grobid_version = version

    def _append_text(self,value) -> None:
        if value is not None:
            self.text.write(value+'\n')

    def _para_as_text(self,para,prev_section=None) -> str:
        para_text = StringIO()
        section = '::'.join([sec[1] for sec in para.section]) if para.section else ""
        if prev_section != section: para_text.write('\n'+section+'\n')
        para_text.write(para.text+'\n')
        return para_text.getvalue(), section

    def _ref_entry_as_text(self,ref_entry) -> str:
        ref_text = StringIO()
        ref_text.write('\n'+ref_entry.type_str.upper())
        ref_text.write('\n'+ref_entry.text)
        ref_text.write('\n'+ref_entry.content)
        return ref_text.getvalue()
    
    def _get_metadata(self) -> None:
        metadata = self.paper.metadata
        self._append_text(metadata.title)
        self._append_text(metadata.year)
        self._append_text(metadata.venue)

    def _get_abstract(self) -> None:
        for para in self.paper.abstract:
            value,section = self._para_as_text(para)
            self.text.write(value)

    def _get_body_text(self) -> None:
        section=None
        for para in self.paper.body_text:
            value,section = self._para_as_text(para,prev_section=section)
            self.text.write(value)
    
    def _get_back_matter(self) -> None:
        for para in self.paper.back_matter:
            value,section = self._para_as_text(para)
            self.text.write(value)
    
    def _get_references(self) -> None:
        for ref in self.paper.ref_entries:
            self.text.write(self._ref_entry_as_text(ref))

    def as_text(self) -> str:
        self.text = StringIO()
        if self.grobid_version == GROBID_VERSION_6_1:
            self._get_metadata()
            self._get_abstract()
            self._get_body_text()
            self._get_back_matter()            
        if self.grobid_version == GROBID_VERSION_7_1:
            self._get_references()
        return self.text.getvalue()


def call_grobid_service(grobid_config,input_file,temp_dir,tei_file):
    client = GrobidClient(grobid_config)
    client.process_pdf(input_file, temp_dir, "processFulltextDocument")
    # process TEI.XML -> JSON
    assert os.path.exists(tei_file)
    paper = convert_tei_xml_file_to_s2orc_json(tei_file)
    return paper


def convert_paper_text(paper,grobid_version):
    paper_text = PaperAsText(paper,grobid_version)
    return paper_text.as_text()

def process_pdf_file(
        input_file: str,
        temp_dir: str = BASE_TEMP_DIR,
        output_dir: str = BASE_OUTPUT_DIR,
        grobid_config: Optional[Dict] = None
) -> str:
    """
    Process a PDF file and get JSON representation
    :param input_file:
    :param temp_dir:
    :param output_dir:
    :return:
    """
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # get paper id as the name of the file
    paper_id = '.'.join(input_file.split('/')[-1].split('.')[:-1])
    tei_file = os.path.join(temp_dir, f'{paper_id}.tei.xml')
    output_file = os.path.join(output_dir, f'{paper_id}.txt')
    
    # check if input file exists and output file doesn't
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"{input_file} doesn't exist")
    if os.path.exists(output_file):
        print(f'{output_file} already exists!')

    # process PDF through Grobid version 0.6.1 -> TEI.XML
    paper = call_grobid_service(grobid_config,input_file, temp_dir,tei_file)
    text_1 = convert_paper_text(paper,GROBID_VERSION_6_1)
    os.remove(tei_file)
    # process PDF through Grobid version 0.7.1 which is deployed in the URL -https://cloud.science-miner.com/grobid/api -> TEI.XML
    paper = call_grobid_service(GROBID_CONFIG_V_7_1,input_file, temp_dir,tei_file)
    text_2 = convert_paper_text(paper,GROBID_VERSION_7_1)
    os.remove(tei_file)
    paper_text = '\n'.join([text_1,text_2])
    
    # Write to the output text file
    with open(output_file, 'w') as outf:
        outf.write(paper_text)
    outf.close()

    #Delete the TEI.XML in the temp directory
    return output_file

'''
This python script process converts all the pdf files in the -i argument
to text files and loads them in the -o argument
-i - pdf_repo/
-t temp/
-o text_repo/
'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run S2ORC PDF2JSON")
    parser.add_argument("-i", "--input", default=None, help="path to the PDF files directory")
    parser.add_argument("-t", "--temp", default=BASE_TEMP_DIR, help="path to the temp dir for putting tei xml files")
    parser.add_argument("-o", "--output", default=BASE_OUTPUT_DIR, help="path to the output dir for putting json files")
    parser.add_argument("-k", "--keep", action='store_true')

    args = parser.parse_args()

    input_dir = args.input
    temp_path = args.temp
    output_path = args.output
    keep_temp = args.keep

    start_time = time.time()

    os.makedirs(temp_path, exist_ok=True)
    os.makedirs(output_path, exist_ok=True)

    glob_path = input_dir + "/*.pdf"
    input_files = glob.glob(glob_path)
    for input_file in input_files:
        process_pdf_file(input_file, temp_path, output_path)
    
    runtime = round(time.time() - start_time, 3)
    print("runtime: %s seconds " % (runtime))
    print('done.')