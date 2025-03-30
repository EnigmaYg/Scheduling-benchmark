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
# with open('../data/WikiHow_question2id.json', 'r') as f:
#     id2question = json.load(f)
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
    concrete = json.load(f)

with open('../data/WikiHow_Concrete2.json', 'r') as f:
    concrete2 = json.load(f)

cnt_yes = 0
cnt_no = 0
for key, value in concrete.items():
    if value == 'Yes':
        cnt_yes += 1
    else:
        cnt_no += 1
for key, value in concrete2.items():
    if value == 'Yes':
        cnt_yes += 1
    else:
        cnt_no += 1
print(cnt_yes)
print(cnt_no+cnt_yes)