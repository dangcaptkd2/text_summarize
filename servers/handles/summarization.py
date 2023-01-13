import logging
import time
from servers.infer import run_inference, preprocess_document, summarize
from flask_restful import Resource, reqparse


class Summarization(Resource):
    _parser = None

    def __init__(self) -> None:
        parser = reqparse.RequestParser()
        parser.add_argument('url', type=str, location=['form', 'args'])
        self._parser = parser

    def processing(self):
        try:
            args = self._parser.parse_args()
            url = args['url']
            if url is None:
                return dict(error=1, message="data input invalid [url]")
            start_time = time.time()
            logging.info(f"raw url: {url}")
            input_text, summarize_text, _, _ = run_inference(url)
            logging.info(f"raw input: {input_text}")
            process_time = time.time()-start_time
            return dict(error=0,
                        process_time=process_time,
                        input_text=input_text,
                        summarize_text=summarize_text)
        except Exception as e:
            logging.error(str(e), exc_info=True)
            return dict(error=1, message=str(e))
    #

    def post(self):
        return self.processing()

    def get(self):
        return self.processing()
        # return dict(error=0, message=f"{__class__}.GET not support")


class SummarizationDocument(Resource):
    _parser = None

    def __init__(self) -> None:
        parser = reqparse.RequestParser()
        parser.add_argument('content', type=str, location=['form', 'args'])
        self._parser = parser

    def processing(self):
        try:
            args = self._parser.parse_args()
            content = args['content']
            if content is None:
                return dict(error=1, message="data input invalid [content]")
            start_time = time.time()
            logging.info(f"raw input: {content}")
            document = preprocess_document(content)

            #if len(document.split()) > 200:
            summarize_text, _, _ = summarize(document)
            #else:
            #summarize_text = content                
                
            process_time = time.time()-start_time
            
            return dict(error=0,
                        process_time=process_time,
                        input_text=document,
                        summarize_text=summarize_text)
        except Exception as e:
            logging.error(str(e), exc_info=True)
            return dict(error=1, message=str(e))
    #

    def post(self):
        return self.processing()

    def get(self):
        return self.processing()
        # return dict(error=0, message=f"{__class__}.GET not support")
