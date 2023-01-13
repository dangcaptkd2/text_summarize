#!/usr/bin/env python
# -*- coding: utf-8 -*-
import conf
import logging.config
import argparse

from flask import Flask, request
from flask_restful import Api
from servers.handles.ping import Ping
from servers.handles.summarization import Summarization, SummarizationDocument
from servers.infer import run_inference, preprocess_document, summarize
from flask import jsonify, render_template, Flask, jsonify
from utils.get_logger import setup_logger

from request_form import RequestForm

app = Flask(__name__, static_folder='./static',
            static_url_path='/podcast/static/')
api = Api(app)


@app.route("/")
def start():
    data = dict(error=0, message="server start")
    return jsonify(data)

@app.route("/podcast/test")
def similar_page():
    return render_template(
        "views/index/test.html",
    )
@app.route('/podcast/testv2', methods=['GET','POST'])
def demo_page():
    if request.method.lower() == 'post':
        try:
            req: RequestForm = RequestForm(request)
            input = req.get_str("input", None, method=request.method)
            min_length = req.get_str("min_length", None, method=request.method)
            max_length = req.get_str("max_length", None, method=request.method)

            if input is None:
                return jsonify(dict(error=1,message="Input is None"))
            if input.startswith("https://vnexpress.net/"):
                _, generated_sentence_constant, min_constant, max_constant = run_inference(input, min_length=min_length, max_length=max_length)
                _, generated_sentence_dynamic, min_dynamic, max_dynamic = run_inference(input)
            else:
                document = preprocess_document(input)
                generated_sentence_constant, min_constant, max_constant = summarize(document, min_length=min_length, max_length=max_length)
                generated_sentence_dynamic, min_dynamic, max_dynamic = summarize(document)
     
            return jsonify(dict(error=0, data={'summary_constant': generated_sentence_constant, 
                                                'summary_dynamic': generated_sentence_dynamic,
                                                'min_constant': min_constant, 
                                                'max_constant': max_constant,
                                                'min_dynamic': min_dynamic, 
                                                'max_dynamic': max_dynamic, 

                                                }))
        except Exception as err:
            
            return jsonify(dict(error=1,message=str(err)))
    return render_template('views/index/testv2.html')

if __name__ == "__main__":
    my_logger = setup_logger(file='./logs/logs.log')
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["JSON_AS_ASCII"] = False

    api.add_resource(Ping, '/podcast/ping')
    api.add_resource(Summarization, '/podcast/summarization_by_url')
    api.add_resource(SummarizationDocument, '/podcast/summarization_by_document')

    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=conf.port,
                        help=f'port(default: {conf.port})')
    args = parser.parse_args()
    port = int(args.port)
    my_logger.info(f"Server start: {port}")
    app.debug = False
    app.run(conf.host, port=port, threaded=False)
