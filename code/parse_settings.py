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
for key, value in settings.items():
    tmp_dic = {}
    for v_key, v_value in value.items():
        value_list = v_value.split('\n')
        flag = 0
        for line in value_list:
            if '[Tools:]' in line:
                if 'None' in line:
                    tmp_dic[v_key] = 'None'
                    flag = 1
                else:
                    tmp_dic[v_key] = [line.split('[Tools:]')[1].strip(' ')]
            if flag == 1:
                break
            elif '[Scenario Description:]' in line:
                tmp_dic[v_key].append(line.split('[Scenario Description:]')[1].strip(' '))
    save[key] = tmp_dic
print(len(save))

# with open('../data/WikiHow_setting.json', 'w') as f:
#     json.dump(save, f, indent=4)