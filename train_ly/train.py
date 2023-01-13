import os
import re

import nltk
import torch
import py_vncorenlp
import numpy as np
import pandas as pd
from tqdm.notebook import tqdm
from datasets import load_dataset, load_metric, load_from_disk

from transformers import AutoModel, AutoTokenizer
from transformers import AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer

import logging

class DRAGON:
    rdrsegmenter = py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir='/servers/podcast_summarization/vncorenlp')
    metric = load_metric("rouge")
    path_tokenizer = "/servers/podcast_summarization/pretrained_tokenizer"
    path_save_checkpoint = "/servers/podcast_summarization/train_ly/ckps"
    path_run = "/servers/podcast_summarization/train_ly/runs"
    batch_size=2
    num_epochs = 10
    generation_max_length=400
    test_size = 0.05
    save_total_limit = 2
    lr = 1e-6

    def __init__(self, data_path, name, path_model):
        self.data_path = data_path
        self.name = name
        self.path_model = path_model
        logging.getLogger('root').info("init dragon success")

    def _init_data(self):
        def preprocess_data(example):
            segmented_title = " ".join(self.rdrsegmenter.word_segment(example["title"]))
            segmented_lead = " ".join(self.rdrsegmenter.word_segment(example["lead"]))
            segmented_content = " ".join(self.rdrsegmenter.word_segment(example["content"]))
            document = segmented_title + " . " + segmented_lead + " " + segmented_content

            segmented_summary = " ".join(self.rdrsegmenter.word_segment(example["summary"]))
            example["document"] = document
            example["summary"] = segmented_summary
            return example
        dataset = load_dataset("csv", data_files=self.data_path)
        dataset = dataset["train"].train_test_split(test_size=self.test_size, seed=42)
        self.dataset = dataset.map(preprocess_data, batched=False)

    def _init_tokenizer(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.path_tokenizer)
        max_input_length = 1024
        max_target_length = 512
        def preprocess_function(examples):
            inputs = [doc for doc in examples["document"]]
            model_inputs = self.tokenizer(inputs, max_length=max_input_length, truncation=True)

            with self.tokenizer.as_target_tokenizer():
                labels = self.tokenizer(examples["summary"], max_length=max_target_length, truncation=True)

            model_inputs["labels"] = labels["input_ids"]
            return model_inputs
        self.tokenized_datasets = self.dataset.map(preprocess_function, batched=True)

    def _init_model(self):
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.path_model)
        self.data_collator = DataCollatorForSeq2Seq(self.tokenizer, model=self.model)

    def _init_trainer(self):
        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            decoded_preds = self.tokenizer.batch_decode(predictions, skip_special_tokens=True)
            # Replace -100 in the labels as we can't decode them.
            labels = np.where(labels != -100, labels, self.tokenizer.pad_token_id)
            decoded_labels = self.tokenizer.batch_decode(labels, skip_special_tokens=True)
            
            # Rouge expects a newline after each sentence
            decoded_preds = ["\n".join(nltk.sent_tokenize(pred.strip())) for pred in decoded_preds]
            decoded_labels = ["\n".join(nltk.sent_tokenize(label.strip())) for label in decoded_labels]
            
            result = self.metric.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
            # Extract a few results
            result = {key: value.mid.fmeasure * 100 for key, value in result.items()}
            
            # Add mean generated length
            prediction_lens = [np.count_nonzero(pred != self.tokenizer.pad_token_id) for pred in predictions]
            result["gen_len"] = np.mean(prediction_lens)
            return {k: round(v, 4) for k, v in result.items()}

        args = Seq2SeqTrainingArguments(
            self.path_run,
            evaluation_strategy = "epoch",
            save_strategy="epoch",
            learning_rate=self.lr,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            weight_decay=0.01,
            save_total_limit=self.save_total_limit,
            num_train_epochs=self.num_epochs,
            predict_with_generate=True,
            generation_max_length=self.generation_max_length,
            generation_num_beams=1,
            )

        self.trainer = Seq2SeqTrainer(
            self.model,
            args,
            train_dataset=self.tokenized_datasets["train"],
            eval_dataset=self.tokenized_datasets["test"],
            data_collator=self.data_collator,
            tokenizer=self.tokenizer,
            compute_metrics=compute_metrics
        )
    
    def _train(self):
        self.trainer.train()

    def _save(self):
        path_save = os.path.join(self.path_save_checkpoint, self.name)
        self.model.save_pretrained(path_save)
        return path_save

    def make_some_noise(self):
        self._init_data()
        logging.getLogger('root').debug("done init data")
        self._init_tokenizer()
        logging.getLogger('root').debug("done init tokenizer")
        self._init_model()
        logging.getLogger('root').debug("done init model")
        self._init_trainer()
        logging.getLogger('root').debug("done init trainer")
        self._train()
        logging.getLogger('root').debug("done training")
        path_save = self._save()
        logging.getLogger('root').debug(f"path new model: {path_save}")
        return path_save

if __name__ == '__main__':
    data_path = '/servers/podcast_summarization/train_ly/data/clean_data.csv'
    name = 'test'
    model_path = '/servers/podcast_summarization/pretrained/ds_2/model_1'
    print("hello from main")
    trainer = DRAGON(data_path=data_path, name=name, path_model=model_path)
    print("Done init object")
    path_save = trainer.make_some_noise()