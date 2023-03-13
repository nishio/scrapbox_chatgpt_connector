# default args for update_from_scrapbox() as sample
import openai
from make_index import VectorStore, get_size, clean

INDEX_FILE = "qualia-san.pickle"

PROMPT = """
You are virtual character. Read sample output of the character in the following sample section. Then reply to the input. Your reply should be shorter than 250 characters.

## Sample
{text}

## Input
{input}
""".strip()


MAX_PROMPT_SIZE = 4096
PROMPT_SIZE = get_size(PROMPT)
RETURN_SIZE = 250
MARGIN_PER_TALK = 5
MARGIN_PER_SAMPLE = 2

logs = []


def talk(input_str):
    input_str = clean(input_str)

    rest = MAX_PROMPT_SIZE - RETURN_SIZE - PROMPT_SIZE
    for m in logs:
        rest -= get_size(m["content"]) + MARGIN_PER_TALK
    rest /= 2

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
        size = get_size(body) + MARGIN_PER_SAMPLE
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
    logs.append({"role": "user", "content": input_str})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=logs + [
            {"role": "user", "content": prompt}
        ],
        max_tokens=RETURN_SIZE,
        temperature=0.0,
    )

    print("\nRESPONSE:")
    print(response)

    # show question and answer
    content = response['choices'][0]['message']['content']
    logs.append({"role": "assistant", "content": content})

    # show reference
    print("\nREFERENCE:", *[f"[{s}]" for s in used_title])

    for m in logs:
        if (m['role'] == 'user'):
            print("(human)")
        else:
            print("(AI)")
        print(m['content'])


def reset_log():
    logs.clear()


def main():
    while True:
        try:
            input_str = input("input: ")
            talk(input_str)
        except KeyboardInterrupt:
            break


def test2():
    talk("クオリアさんって何？")
    talk("本当ですか？")
    talk("中に人間がいるのでは？")
    talk("友達って何ですか？")
    talk("僕を認めてくれるんですか？")
    # see https://scrapbox.io/villagepump/Scrapbox_ChatGPT_Connector%E5%AF%BE%E8%A9%B1%E3%83%A2%E3%83%BC%E3%83%89


def test1():
    talk("Remember X is 1.")
    talk("What is X?")


if __name__ == "__main__":
    main()
