from make_index import VectorStore
people = ["motoso",  "nishio",   "mtane0412", "qualia-san", "tkgshn",
          "blu3mo-public"]
input_str = "Scrapboxとは？"

rest_samples = []
tops = []
for person in people:
    vs = VectorStore(f"{person}.pickle")
    samples = [(sim, body, f"[/{person}/{title}]")
               for sim, body, title in vs.get_sorted(input_str)]
    tops.append(samples.pop(0))
    rest_samples.extend(samples)

rest_samples.sort(reverse=True)
rest_samples = rest_samples[:10 - len(people)]
all_samples = tops + rest_samples
all_samples.sort(reverse=True)
for sim, body, title in all_samples:
    print(title)
    # print(body)
    # print()
