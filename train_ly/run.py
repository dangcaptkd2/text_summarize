import logging
from logging.handlers import RotatingFileHandler

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

logFile = '/servers/podcast_summarization/train_ly/logs/log.log'

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=50*1024, 
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.DEBUG)

app_log = logging.getLogger('root')
app_log.setLevel(logging.DEBUG)

app_log.addHandler(my_handler)

import os 
import json
from train import DRAGON
from data import process_data
from utils.telegram_notify import telegram_bot_sendtext

_PATH_CONFIG = "/servers/podcast_summarization/default_config.json"

def update_new_model(path, path_config=_PATH_CONFIG):
    default_config = json.load(open(path_config))
    default_config["current_model"] = path
    with open(path_config, 'w') as outfile:
        json.dump(default_config, outfile)
    app_log.info("update new model success")

if __name__ == '__main__':
    app_log.info("== START TRAINING ==")
    telegram_bot_sendtext("START TRAINING")
    attempts = 0
    while attempts<3:
        try:
            default_config = json.load(open(_PATH_CONFIG))
            path_pretrain_model = default_config['pretrain_model']
            app_log.debug(f"pretrain model: {path_pretrain_model}")
            app_log.debug(f"n days: {default_config['n_days']}")
            data_path, name, len_data = process_data(n_days=default_config['n_days'])
            telegram_bot_sendtext(f"num train articles: {len_data}")
            trainer = DRAGON(data_path=data_path, name=name, path_model=path_pretrain_model)
            print("Done init object")
            path_save = trainer.make_some_noise()
            update_new_model(path_save)
            app_log.info(f"== path model save at: {path_save} ==")
            telegram_bot_sendtext(f"path model save at: {path_save}")
            app_log.info("== DONE TRAINING ==")
            telegram_bot_sendtext("DONE TRAINING")
            break
        except:
            attempts+=1
            app_log.error(f"Can not finish training, something is wrong, attemps: {attempts}/3")
            telegram_bot_sendtext(f"Can not finish training, something is wrong, attemps: {attempts}/3")
            