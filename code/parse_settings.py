import json

with open('../data/WikiHow_settings.json', 'r') as f:
    setting1 = json.load(f)

with open('../data/WikiHow_settings2.json', 'r') as f:
    setting2 = json.load(f)

settings = {}

for key, value in setting1.items():
    settings[key] = value

for key, value in setting2.items():
    settings[key] = value

save = {}
cnt = 0
all_cnt = 0
for key, value in settings.items():
    tmp_dic = {}
    all_flag = 0
    for v_key, v_value in value.items():
        value_list = v_value.split('\n')
        flag = 0
        for line in value_list:
            if '[Tools:]' in line:
                if 'None' in line:
                    tmp_dic[v_key] = 'None'
                    flag = 1
                else:
                    all_flag = 1
                    tmp_dic[v_key] = [line.split('[Tools:]')[1].strip(' ')]
            if flag == 1:
                break
            elif '[Scenario Description:]' in line:
                all_flag = 1
                tmp_dic[v_key].append(line.split('[Scenario Description:]')[1].strip(' '))
    if all_flag == 0:
        cnt += 1
    all_cnt += len(tmp_dic)
    save[key] = tmp_dic
print(len(save))
print(cnt)
print(all_cnt)

# with open('../data/WikiHow_setting.json', 'w') as f:
#     json.dump(save, f, indent=4)