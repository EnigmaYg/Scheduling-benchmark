import json


with open('../data/filtered_instructions/WikiHow_SPQ.json', 'r') as f:
    SPQ = json.load(f)

cnt_yes = 0
cnt_no = 0
cnt = 0
for key, value in SPQ.items():
    if value == 'yes':
        cnt_yes += 1
    elif value == 'no':
        cnt_no += 1
    else:
        print(value)
    cnt += 1
print(cnt)
print(cnt_yes)
print(cnt_no)


with open('../data/filtered_instructions/WikiHow_humanity.json', 'r') as f:
    human = json.load(f)

cnt = 0
for key, value in human.items():
    if value == 'yes':
        cnt += 1
print(cnt)