import conf
from datetime import datetime
from os import path, remove

import urllib.request
import functools
import socket
import requests
from hashlib import md5
from os import makedirs, path
import logging
from datetime import datetime
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image

socket.setdefaulttimeout(60)
#
if conf.using_proxy:
    proxy_support = urllib.request.ProxyHandler(conf.proxies)
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)



@functools.lru_cache(maxsize=20)
def download(store_path: str):
    _dir = path.join(conf.download_path, store_path)
    if not path.isdir(_dir):
        makedirs(_dir, mode=0x777)
        logging.info("%s created" % _dir)

    def check_allow():
        return True

    def __download(url: str):
        if url is None:
            return None
        try:
            start = datetime.now().timestamp()
            uparse = urlparse(url)
            basename = path.basename(uparse.path)
            name, ext = tuple(basename.rsplit(".", 1))
            name = md5(name.encode("utf-8")).hexdigest()
            download_to = "%s/%s.%s" % (_dir, name, ext)
            if not path.isfile(download_to):
                # urllib.request.urlretrieve(url, download_to)
                if conf.using_proxy:
                    r = requests.get(url, allow_redirects=False,
                                     proxies=conf.proxies)
                else:
                    r = requests.get(url, allow_redirects=False)
                img = Image.open(BytesIO(r.content))
                img.save(download_to)
                if conf.is_logging:
                    logging.info(
                        "Download : {} --> {} ({:.3f} second)".format(
                            url, download_to, datetime.now().timestamp() - start
                        )
                    )
            return "%s/%s.%s" % (store_path, name, ext)
        except Exception as e:
            logging.error(url, exc_info=True)
            return None

    return __download


def test_download(url):
    download_to = "%s/me.webp" % (conf.download_path)
    r = requests.get(url, allow_redirects=True, proxies=conf.proxies)
    f = open(download_to, "wb")
    f.write(r.content)
    f.close()


def download_image(url):
    try:
        store_path = datetime.today().strftime("%Y/%m/%d")
        to_image_path = download(store_path)(url)
        return path.join(conf.download_path, to_image_path)
    except Exception as e:
        logging.error("Download : %s (%s)" % (url, str(e)))
        return None


def build_name(_dir, url):
    uparse = urlparse(url)
    basename = path.basename(uparse.path)
    name, ext = tuple(basename.rsplit(".", 1))
    name = md5(name.encode("utf-8")).hexdigest()
    download_to = "%s/%s.%s" % (_dir, name, ext)
    return path.join(conf.download_path, download_to)


@functools.lru_cache(maxsize=20)
def download_image_block(block_no):
    store_path = f'block_{block_no}'
    _dir = path.join(conf.download_path, store_path)
    if not path.isdir(_dir):
        makedirs(_dir, mode=0x777)
        logging.info("%s created" % _dir)

    def __download(url: str):
        try:
            start = datetime.now().timestamp()
            uparse = urlparse(url)
            basename = path.basename(uparse.path)
            name, ext = tuple(basename.rsplit(".", 1))
            name = md5(name.encode("utf-8")).hexdigest()
            filename = "%s.%s" % (name, ext)
            download_to = path.join(conf.download_path, store_path, filename)
            # if not path.isfile(download_to):
            # urllib.request.urlretrieve(url, download_to)
            if conf.using_proxy:
                r = requests.get(url, allow_redirects=False,
                                 proxies=conf.proxies)
            else:
                r = requests.get(url, allow_redirects=False)
            img = Image.open(BytesIO(r.content))
            # img.save(download_to)
            if conf.is_logging:
                logging.info(
                    "Download : {} --> {} ({:.3f} second)".format(
                        url, download_to, datetime.now().timestamp() - start
                    )
                )
            return img
        except Exception as e:
            logging.error("Download : %s (%s)" % (url, str(e)))
            return None
    return __download


def url_to_pillow_image(url: str):
    try:
        if conf.using_proxy:
            r = requests.get(url, allow_redirects=False,
                             proxies=conf.proxies)
        else:
            r = requests.get(url, allow_redirects=False)
        img = Image.open(BytesIO(r.content))
        return img
    except Exception as e:
        logging.error("Download : %s (%s)" % (url, str(e)))
        return None


if __name__ == "__main__":
    from datetime import datetime

    store_path = datetime.today().strftime("%Y/%m/%d")
    image_url = "https://media.doisongphapluat.com/699/2020/10/1/ky-la-toc-nguoi-hiem-hoi-so-huu-mau-mat-xanh-nhu-bien-ca-dspl-3.png"
    print(download_image_block(1)(image_url))
    # img = Image.open(local_file)
    # test_download(
    #     "https://img.vietnamfinance.vn/webp-jpg/upload/news/ngocluu/2020/10/1/LAMTHANH_0063.webp"
    # )
