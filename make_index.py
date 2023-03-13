import signal
import time
import json
import tiktoken
import openai
import pickle
import numpy as np
from tqdm import tqdm
import re
import dotenv
import os

# default args for update_from_scrapbox() as sample
# input json data from https://scrapbox.io/qualia-san/
JSON_FILE = "from_scrapbox/qualia-san.json"
# output file name
INDEX_FILE = "qualia-san.pickle"

BLOCK_SIZE = 500

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
enc = tiktoken.get_encoding("cl100k_base")


def get_size(text):
    return len(enc.encode(text))


def embed(text, sleep_after_sucess=1):
    EMBED_MAX_SIZE = 8150  # actual limit is 8191
    text = text.replace("\n", " ")
    tokens = enc.encode(text)
    if len(tokens) > EMBED_MAX_SIZE:
        text = enc.decode(tokens[:EMBED_MAX_SIZE])

    while True:
        try:
            res = openai.Embedding.create(
                input=[text],
                model="text-embedding-ada-002")
            time.sleep(sleep_after_sucess)
        except Exception as e:
            print(e)
            time.sleep(1)
            continue
        break

    return res["data"][0]["embedding"]


def clean(line):
    line = line.strip()
    line = re.sub(r"https?://[^\s]+", "URL", line)
    line = re.sub(r"[\s]+", " ", line)
    return line


def update_from_scrapbox(out_index=INDEX_FILE, jsonfile=JSON_FILE, in_index=None):
    """
    out_index: output index file name
    jsonfile: input json file name (from scrapbox)
    in_index: input index file name (it is not modified, but used as cache)
    """
    cache = None
    if in_index is not None:
        cache = VectorStore(in_index, create_if_not_exist=False).cache
    vs = VectorStore(out_index)
    data = json.load(open(jsonfile, encoding="utf8"))
    for p in tqdm(data["pages"]):
        buf = []
        title = p["title"]
        for line in p["lines"]:
            buf.append(clean(line))
            body = " ".join(buf)
            if get_size(body) > BLOCK_SIZE:
                vs.get_or_make(body, title, cache)
                buf = buf[len(buf) // 2:]
        body = " ".join(buf).strip()
        if body:
            vs.get_or_make(body, title, cache)


def safe_write(obj, name):
    to_exit = False

    def change_state(signum, frame):
        nonlocal to_exit
        to_exit = True

    signal.signal(signal.SIGINT, change_state)
    pickle.dump(obj, open(name, "wb"))
    signal.signal(signal.SIGINT, signal.signal.SIG_DFL)
    if to_exit:
        raise KeyboardInterrupt


class VectorStore:
    def __init__(self, name=INDEX_FILE, create_if_not_exist=True):
        self.name = name
        try:
            self.cache = pickle.load(open(self.name, "rb"))
        except FileNotFoundError as e:
            if create_if_not_exist:
                self.cache = {}
            else:
                raise

    def get_or_make(self, body, title, cache=None):
        if cache is None:
            cache = self.cache
        if body not in cache:
            print("not in cache")
            print(title, body[:20])
            self.cache[body] = (embed(body), title)
            safe_write(self.cache, self.name)
        elif body not in self.cache:
            # print("in cache")
            self.cache[body] = cache[body]
            safe_write(self.cache, self.name)
        else:
            print("already have")

        return self.cache[body]

    def get_sorted(self, query):
        q = np.array(embed(query, sleep_after_sucess=0))
        buf = []
        for body, (v, title) in tqdm(self.cache.items()):
            buf.append((q.dot(v), body, title))
        buf.sort(reverse=True)
        return buf


if __name__ == "__main__":
    # update_from_scrapbox()
    update_from_scrapbox(
        "nishio.pickle", "from_scrapbox/nishio.json", "nishio-20230309.pickle")
