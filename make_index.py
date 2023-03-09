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


def embed(text):
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
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)
            continue
        break

    return res["data"][0]["embedding"]


def update_from_scrapbox(name=INDEX_FILE, jsonfile=JSON_FILE):
    vs = VectorStore(name)
    data = json.load(open(jsonfile, encoding="utf8"))
    for p in tqdm(data["pages"]):
        buf = []
        title = p["title"]
        for line in p["lines"]:
            line = line.strip()
            line = re.sub(r"https?://[^\s]+", "URL", line)
            line = re.sub(r"[\s]+", " ", line)
            buf.append(line)
            body = " ".join(buf)
            if get_size(body) > BLOCK_SIZE:
                vs.get_or_make(body, title)
                buf = buf[len(buf) // 2:]
        body = " ".join(buf).strip()
        if body:
            vs.get_or_make(body, title)


class VectorStore:
    def __init__(self, name=INDEX_FILE):
        self.name = name
        try:
            self.cache = pickle.load(open(self.name, "rb"))
        except FileNotFoundError as e:
            self.cache = {}

    def get_or_make(self, body, title):
        if body not in self.cache:
            self.cache[body] = (embed(body), title)
            pickle.dump(self.cache, open(self.name, "wb"))
        return self.cache[body]

    def get_sorted(self, query):
        q = np.array(embed(query))
        buf = []
        for body, (v, title) in tqdm(self.cache.items()):
            buf.append((q.dot(v), body, title))
        buf.sort(reverse=True)
        return buf


if __name__ == "__main__":
    update_from_scrapbox()
