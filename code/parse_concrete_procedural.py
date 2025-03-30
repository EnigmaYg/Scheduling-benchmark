import json

# data = []
# with open('../data/WikiHowNFQA.jsonl', 'r', encoding='utf-8') as f:
#     for line in f:
#         data.append(json.loads(line))
# print(len(data))
#
# with open('../data/WikiHow_ProceduralQ.json', 'r') as f:
#     proceduralQ = json.load(f)
#
with open('../data/WikiHow_question2id.json', 'r') as f:
    question2id = json.load(f)
with open('../data/WikiHow_procedural_question.json', 'r') as f:
    procedural_question = json.load(f)
#
# save = {}
# cnt = 0
# for item in data:
#     if item['question'] in proceduralQ:
#         if proceduralQ[item['question']] != 'No':
#             save[id2question[item['question']]] = proceduralQ[item['question']]
#         else:
#             cnt += 1
#
# with open('../data/WikiHow_ProceduralQ2.json', 'r') as f:
#     proceduralQ2 = json.load(f)
# for item in data:
#     if item['question'] in proceduralQ2:
#         if proceduralQ2[item['question']] != 'No':
#             save[id2question[item['question']]] = proceduralQ2[item['question']]
#         else:
#             cnt += 1
# with open('../data/WikiHow_procedural_question.json', 'w') as f:
#     json.dump(save, f, indent=4)
with open('../data/WikiHow_Concrete.json', 'r') as f:
    concrete1 = json.load(f)

with open('../data/WikiHow_Concrete2.json', 'r') as f:
    concrete2 = json.load(f)

with open('../data/WikiHow_Concrete3.json', 'r') as f:
    concrete3 = json.load(f)

cnt_yes = 0
cnt_no = 0
concrete = {}
for key, value in concrete1.items():
    concrete[key] = value

for key, value in concrete2.items():
    concrete[key] = value

for key, value in concrete3.items():
    if key in concrete:
        continue
    concrete[key] = value

save = {}
for key, value in concrete.items():
    if value == 'Yes':
        id = question2id[key]
        save[id] = procedural_question[id]
print(len(save))
with open('../data/WikiHow_procedural_concrete_question.json', 'w') as f:
    json.dump(save, f, indent=4)
