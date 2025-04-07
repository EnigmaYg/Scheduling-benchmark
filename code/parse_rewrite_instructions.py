import json

with open('../data/WikiHow_instructions_5874.json', 'r') as f:
    instruct1 = json.load(f)

with open('../data/WikiHow_instructions_11746.json', 'r') as f:
    instruct2 = json.load(f)

instruct = {}
for key, value in instruct2.items():
    instruct[key] = value

for key, value in instruct1.items():
    instruct[key] = value

save = {}
number_list = [str(i) for i in range(10)]
for key, value in instruct.items():
    value_list = value.split('\n')
    tmp_id = '1'
    tmp_list = []
    tmp_dic = {}
    cnt = 0
    for line in value_list:
        if len(line.strip(' ')) == 0:
            continue
        if line[0] not in number_list:
            continue
        if line[0] != tmp_id:
            tmp_dic[cnt] = tmp_list
            cnt += 1
            tmp_id = line[0]
            line = line[2:]
            tmp_list = [line]
        else:
            line = line[2:]
            tmp_list.append(line)
    tmp_dic[cnt] = tmp_list
    # for x in tmp_list_list:
    #     if len(x) == 0:
    #         print(tmp_list_list)
    save[key] = tmp_dic

print('\n'.join(save['How To Get a Copy of Your Medical Records'][0]))
# with open('../data/WikiHow_instructions_rewrite.json', 'w') as f:
#     json.dump(save, f, indent=4)