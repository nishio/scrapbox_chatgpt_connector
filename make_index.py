import time
import json
import tiktoken
import openai
import pickle
import numpy as np
from tqdm import tqdm
import dotenv
import os

BLOCK_SIZE = 500
EMBED_MAX_SIZE = 8150

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
enc = tiktoken.get_encoding("cl100k_base")


def get_size(text):
    "take text, return number of tokens"
    return len(enc.encode(text))


def embed_text(text, sleep_after_success=1):
    "take text, return embedding vector"
    text = text.replace("\n", " ")
    tokens = enc.encode(text)
    if len(tokens) > EMBED_MAX_SIZE:
        text = enc.decode(tokens[:EMBED_MAX_SIZE])

    while True:
        try:
            res = openai.Embedding.create(
                input=[text],
                model="text-embedding-ada-002")
            time.sleep(sleep_after_success)
        except Exception as e:
            print(e)
            time.sleep(1)
            continue
        break

    return res["data"][0]["embedding"]


def update_from_scrapbox(json_file, out_index, in_index=None):
    """
    out_index: Output index file name
    json_file: Input JSON file name (from scrapbox)
    in_index: Optional input index file name. It is not modified and is used as cache to reduce API calls.
    out_index: 出力インデックスファイル名
    json_file: 入力JSONファイル名 (scrapboxからの)
    in_index: オプショナルな入力インデックスファイル名。変更されず、APIコールを減らすためのキャッシュとして使用されます。

    # usage
    ## create new index
    update_from_scrapbox(
        "from_scrapbox/nishio.json",
        "nishio.pickle")

    ## update index
    update_from_scrapbox(
        "from_scrapbox/nishio-0314.json", "nishio-0314.pickle", "nishio-0310.pickle")
    """
    if in_index is not None:
        cache = pickle.load(open(in_index, "rb"))
    else:
        cache = None

    vs = VectorStore(out_index)
    data = json.load(open(json_file, encoding="utf8"))

    for p in tqdm(data["pages"]):
        buf = []
        title = p["title"]
        for line in p["lines"]:
            buf.append(line)
            body = " ".join(buf)
            if get_size(body) > BLOCK_SIZE:
                vs.add_record(body, title, cache)
                buf = buf[len(buf) // 2:]
        body = " ".join(buf).strip()
        if body:
            vs.add_record(body, title, cache)

    vs.save()


class VectorStore:
    def __init__(self, name, create_if_not_exist=True):
        self.name = name
        try:
            self.cache = pickle.load(open(self.name, "rb"))
        except FileNotFoundError as e:
            if create_if_not_exist:
                self.cache = {}
            else:
                raise

    def add_record(self, body, title, cache=None):
        if cache is None:
            cache = self.cache
        if body not in cache:
            # call embedding API
            self.cache[body] = (embed_text(body), title)
        elif body not in self.cache:
            # in cache and not in self.cache: use cached item
            self.cache[body] = cache[body]

        return self.cache[body]

    def get_sorted(self, query):
        q = np.array(embed_text(query, sleep_after_success=0))
        buf = []
        for body, (v, title) in tqdm(self.cache.items()):
            buf.append((q.dot(v), body, title))
        buf.sort(reverse=True)
        return buf

    def save(self):
        pickle.dump(self.cache, open(self.name, "wb"))


if __name__ == "__main__":
    # Sample default arguments for update_from_scrapbox()
    JSON_FILE = "from_scrapbox/tiny_sample.json"
    INDEX_FILE = "tiny_sample.pickle"

    update_from_scrapbox(JSON_FILE, INDEX_FILE)
