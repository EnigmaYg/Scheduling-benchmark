import json

with open('../data/WikiHow_procedural_concrete_question.json', 'r') as f:
    concrete_question = json.load(f)

with open('../data/WikiHow_id2question.json', 'r') as f:
    id2question = json.load(f)

with open('../data/WikiHow_question2id.json', 'r') as f:
    question2id = json.load(f)

data = []
with open('../data/WikiHowNFQA.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data.append(json.loads(line))

save = {}
for line in data:
    if question2id[line['question']] in concrete_question:
        if line['cluster'] in save:
            save[line['cluster']].append(line['question'])
        else:
            save[line['cluster']] = [line['question']]
print(len(save[-1]))

with open('../data/WikiHow_concrete_cluster.json', 'w') as f:
    json.dump(save, f, indent=4)