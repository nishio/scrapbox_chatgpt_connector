# default args for update_from_scrapbox() as sample
import os
import dotenv
import openai
import tiktoken
from make_index import VectorStore


INDEX_FILE = "qualia-san.pickle"

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
enc = tiktoken.get_encoding("cl100k_base")


def get_size(text):
    return len(enc.encode(text))


def embed(text):
    return openai.Embedding.create(
        input=[text], model="text-embedding-ada-002")["data"][0]["embedding"]


PROMPT = """
Read the following text and answer the question. Your reply should be shorter than 250 characters.

## Text
{text}

## Question
{input}
""".strip()


input_str = """
もっとも大事な問いとは何だろう？
""".strip()


MAX_PROMPT_SIZE = 4096
RETURN_SIZE = 250
PROMPT_SIZE = get_size(PROMPT)
rest = MAX_PROMPT_SIZE - RETURN_SIZE - PROMPT_SIZE
input_size = get_size(input_str)
print("input size:", input_size)
if rest < input_size:
    raise RuntimeError("too large input!")

rest -= input_size


vs = VectorStore(INDEX_FILE)
samples = vs.get_sorted(input_str)

to_use = []
used_title = []
for _sim, body, title in samples:
    if title in used_title:
        continue
    size = get_size(body)
    if rest < size:
        break
    to_use.append(body)
    used_title.append(title)
    print("\nUSE:", title, body)
    rest -= size

text = "\n\n".join(to_use)
prompt = PROMPT.format(input=input_str, text=text)


print("\nPROMPT:")
print(prompt)

print("\nTHINKING...")
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": prompt}
    ],
    max_tokens=RETURN_SIZE,
    temperature=0.0,
)

print("\nRESPONSE:")
print(response)
content = response['choices'][0]['message']['content']

print("\nANSWER:")
print(f">>>> {input_str}")
print(">", content)
print("\nref.", *[f"[{s}]" for s in used_title])
