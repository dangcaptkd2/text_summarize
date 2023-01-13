import requests
from datetime import date
import datetime
from collections import defaultdict
from tqdm import tqdm 
import pandas as pd
import re
import os 
os.chdir('/servers/podcast_summarization')
print(os.getcwd())
import sys
sys.path.append('./')
from servers.infer import extract_html, preprocess_title_and_lead, preprocess_content, tone_normalization

import logging

def get_current_day(do_slice=False):
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")
    d1 = d1.split('/')
    if do_slice:
        return d1, today
    return d1

def get_back_n_days(n=14, to_=None, do_slice=False):
    if to_ is None:
        tod = datetime.datetime.now()
    else:
        tod = to_
    d = datetime.timedelta(days = n)
    t = tod - d
    a = t.strftime("%d/%m/%Y")
    a = a.split('/')
    if do_slice:
        return a, t
    return a

def slice_day(today, today_raw, n_days, slice=7):
    n_slice = n_days//slice
    mod_slice = n_days%slice
    fr_ = None 
    to_ = today
    raw_to = today_raw
    result = []
    for _ in range(n_slice):
        fr_, raw_fr = get_back_n_days(n=slice, to_=raw_to, do_slice=True)
        result.append([fr_, to_])
        to_, raw_to = get_back_n_days(n=1, to_=raw_fr, do_slice=True)
        
    if mod_slice != 0:
        fr_, raw_fr = get_back_n_days(n=mod_slice, to_=raw_to, do_slice=True)
        result.append([fr_, to_])
    return result

def get_data(from_, to_):
    link = f"https://ss.vnexpress.net/api/list?from_date={from_[0]}%2F{from_[1]}%2F{from_[2]}&to_date={to_[0]}%2F{to_[1]}%2F{to_[2]}"
    print(link)
    # link = "https://ss.vnexpress.net/api/list?from_date=19%2F12%2F2022&to_date=19%2F12%2F2022"
    data = requests.get(link).json()

    if data['status'] == 200:
        data = data['data']
        return data
    else:
        return None

def preprocess_summary(text):
    text = tone_normalization(text)

    text = text.strip("\n")
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\.+", ".", text)
    return text

def process_data(n_days=14):
    to, raw_to = get_current_day(do_slice=True)
    fr = get_back_n_days(n_days)
    logging.getLogger('root').debug(f"from day: {'/'.join(fr)}")
    logging.getLogger('root').debug(f"to day: {'/'.join(to)}")
    lst_slice_day = slice_day(today=to, today_raw=raw_to, n_days=n_days)
    for i in lst_slice_day:
        logging.getLogger('root').debug(f"pair day: {i}")
    data = []
    for fr, to in lst_slice_day:
        data0 = get_data(fr,to)
        data.extend(data0)
    result = defaultdict(list)
    logging.getLogger('root').debug(f"num raw articles: {len(data)}")
    for dic in tqdm(data):
        try:
            summary = dic['content_btv']
            url = dic['new_url']
            title, lead, content = extract_html(url)
            if title is None or lead is None or content is None:
                continue
            title = preprocess_title_and_lead(title)
            lead = preprocess_title_and_lead(lead)
            content = preprocess_content(content)
            summary = preprocess_summary(summary)

            result['summary'].append(summary)
            result['title'].append(summary)
            result['lead'].append(lead)
            result['content'].append(content)
        except:
            print(dic)
    
    df = pd.DataFrame(result)
    logging.getLogger('root').debug(f"num raw articles: {len(df)}")
    path_ = f"train_ly/data/{''.join(to)}.csv"
    df.to_csv(path_, index=False)
    return path_, ''.join(to), len(df)
      

if __name__ == '__main__':
    path, name, length = process_data(n_days=5)