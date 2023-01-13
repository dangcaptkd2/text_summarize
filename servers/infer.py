import logging
import requests
import re
import torch
from bs4 import BeautifulSoup
from transformers import AutoModel, AutoTokenizer
from transformers import AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer
import py_vncorenlp
from werkzeug.local import Local
from utils.get_logger import setup_logger

torch.manual_seed(0)

import json
default_config = json.load(open('/servers/podcast_summarization/default_config.json'))

logger = setup_logger(file='./logs/logs.log', name='infer')

class Manager(object):
    #
    tokenizer_pretrained = "/servers/podcast_summarization/pretrained_tokenizer"
    model_pretrained = default_config['current_model']
    nlp_vncore = '/servers/podcast_summarization/vncorenlp'
    #

    def __init__(self) -> None:
        #
        self._device = 'cuda'
        self._VnCoreNLP = None
        self._SumaryModelPretrained = None
        self._Tokenizer = None
        #
        self.get_SumaryModelPretrained()
     
    def get_VnCoreNLP(self):
        if self._VnCoreNLP is not None:
            return self._VnCoreNLP
        logger.info(
            "=== Start VnCoreNLP() ===")
        rdrsegmenter = py_vncorenlp.VnCoreNLP(
            annotators=["wseg"], save_dir=self.nlp_vncore)
        self._VnCoreNLP = rdrsegmenter
        logger.info(f"VnCoreNLP loaded...")
        return self._VnCoreNLP

    def get_SumaryModelPretrained(self):
        if self._SumaryModelPretrained is not None:
            return self._SumaryModelPretrained
        logger.info(
            "=== Start VnCoreNLP() ===")
        model = AutoModelForSeq2SeqLM.from_pretrained(self.model_pretrained)
        model.to(self._device).eval()
        self._SumaryModelPretrained = model
        logger.info(f"VnCoreNLP loaded...")
        return self._SumaryModelPretrained

    def get_Tokenizer(self):
        if self._Tokenizer is not None:
            return self._Tokenizer
        logger.info(
            "=== Start AutoTokenizer() ===")
        self._Tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_pretrained)
        logger.info(f"AutoTokenizer loaded...")
        return self._Tokenizer

    def getDevice(self):
        return self._device


instances = Local()
instances.manager: Manager = Manager()

normalized_map = {
    "òa": "oà",
    "Òa": "Oà",
    "ÒA": "OÀ",
    "óa": "oá",
    "Óa": "Oá",
    "ÓA": "OÁ",
    "ỏa": "oả",
    "Ỏa": "Oả",
    "ỎA": "OẢ",
    "õa": "oã",
    "Õa": "Oã",
    "ÕA": "OÃ",
    "ọa": "oạ",
    "Ọa": "Oạ",
    "ỌA": "OẠ",
    "òe": "oè",
    "Òe": "Oè",
    "ÒE": "OÈ",
    "óe": "oé",
    "Óe": "Oé",
    "ÓE": "OÉ",
    "ỏe": "oẻ",
    "Ỏe": "Oẻ",
    "ỎE": "OẺ",
    "õe": "oẽ",
    "Õe": "Oẽ",
    "ÕE": "OẼ",
    "ọe": "oẹ",
    "Ọe": "Oẹ",
    "ỌE": "OẸ",
    "ùy": "uỳ",
    "Ùy": "Uỳ",
    "ÙY": "UỲ",
    "úy": "uý",
    "Úy": "Uý",
    "ÚY": "UÝ",
    "ủy": "uỷ",
    "Ủy": "Uỷ",
    "ỦY": "UỶ",
    "ũy": "uỹ",
    "Ũy": "Uỹ",
    "ŨY": "UỸ",
    "ụy": "uỵ",
    "Ụy": "Uỵ",
    "ỤY": "UỴ",
}


def tone_normalization(text):
    for i, j in normalized_map.items():
        text = text.replace(i, j)
    return text


def extract_html(url):
    matchObj = re.match(r'(.*)-(\d+)\.html$', url, re.M | re.I)
    if matchObj:
        id = matchObj.group(2)
        link = "https://gw.vnexpress.net/ar/get_full?article_id="+id + \
            "&data_select=article_id%2Ccontent%2Ctitle%2Clead%2Cshare_url&page_content=1"
        response = requests.get(link).json()
        title = response["data"]["title"]
        lead = response["data"]["lead"]
        content = response["data"]["content"]
        return title, lead, content
    else:
        return None,None,None

def preprocess_content(text):
    # remove html tag
    soup = BeautifulSoup(text, "html.parser")
    text = ""
    for a in soup.find_all("p"):
        if a.text.endswith("."):
            text += a.text + " "
        else:
            text += a.text + ". "
    # remove author of image "Ảnh: . ABC. "
    text = re.sub(r"Ảnh: .+\.", "", text)

    text = tone_normalization(text)

    # remove punctuation
    # text = text.translate(str.maketrans('', '', string.punctuation.replace(".", "")))

    text = text.strip("\n")
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\.+", ".", text)
    return text

def preprocess_title_and_lead(text):
    text = tone_normalization(text)

    # remove punctuation
    # text = text.translate(str.maketrans('', '', string.punctuation.replace(".", "")))

    text = text.strip("\n")
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text)

    text = re.sub(r"\.+", ".", text)
    return text

def preprocess_data(title, lead, content):
    manager: Manager = instances.manager
    rdrsegmenter = manager.get_VnCoreNLP()
    segmented_title = " ".join(rdrsegmenter.word_segment(title))
    segmented_lead = " ".join(rdrsegmenter.word_segment(lead))
    segmented_content = " ".join(rdrsegmenter.word_segment(content))
    document = segmented_title + " . " + segmented_lead + " " + segmented_content
    return document

def preprocess_document(document):
    manager: Manager = instances.manager
    rdrsegmenter = manager.get_VnCoreNLP()
    document = " ".join(rdrsegmenter.word_segment(document))
    return document

def summarize(input_sentence, min_length=None, max_length=None):
    
    def choose_max_length(doc):
        length_doc = len(doc.split())
        return int(0.2*length_doc)+300
    
    def choose_min_length(doc):
        length_doc = len(doc.split())
        if length_doc > 1000:
            return 150
        return 100

    logger.info(f"input: {input_sentence}")

    if min_length is None or len(min_length)==0:
        min_length=choose_min_length(input_sentence)
    else:
        min_length  = int(min_length)

    if max_length is None or len(max_length)==0:
        max_length = choose_max_length(input_sentence)
    else: 
        max_length = int(max_length)
    
    if min_length >= max_length:
        max_length = min_length+100

    logger.info(f"min_length: {min_length}, max_length: {max_length}")

    manager: Manager = instances.manager
    tokenizer = manager.get_Tokenizer()
    device = manager.getDevice()
    model = manager.get_SumaryModelPretrained()    
    model.eval()
    batch = tokenizer(input_sentence, max_length=1024,
                      truncation=True, return_tensors='pt')
    with torch.no_grad():
        input_ids = batch['input_ids'].to(device)
        generated_ids = model.generate(input_ids, max_length=max_length,
                                       min_length=min_length, num_beams=10,
                                       early_stopping=True, no_repeat_ngram_size=3)
    generated_sentence = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    a = generated_sentence.replace("_", " ")
    logger.info(f"output: {a}")
  
    return a, min_length, max_length

def url2content(url):  
    title, lead, content = extract_html(url)   
    title = preprocess_title_and_lead(title)
    lead = preprocess_title_and_lead(lead)
    content = preprocess_content(content)
    document = preprocess_data(title, lead, content)
    return document
    
def run_inference(url, min_length=None, max_length=None):
    document  = url2content(url)
    with torch.no_grad():
   
        generated_sentence, min_, max_ = summarize(document, min_length=min_length, max_length=max_length)
    return document, generated_sentence, min_, max_


if __name__ == '__main__':

    url = 'https://vnexpress.net/ong-tap-mo-ky-nguyen-moi-trong-quan-he-trung-quoc-arab-4547437.html'

    generated_sentence = run_inference(url)
    # print(len(document))
    print(generated_sentence)
