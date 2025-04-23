import json

with open('../data/match_tools/tmp_tools_analyse.json', 'r') as f:
    data = json.load(f)

with open('../data/match_tools/tmp_tools_analyse_parse.json', 'r') as f:
    save = json.load(f)

# save = {}
for key, value in data.items():
    tmp_dic_dic = {}
    for v_key, value in value.items():
        flag = 0
        tmp_dic = {}
        for line in value.split('\n'):
            if len(line) == 0:
                continue
            if '[Tools:]' in line:
                tmp = {}
                flag = 1
                continue
            elif '[Materials:]' in line:
                tmp_dic['Tool_steps'] = tmp
                tmp = ''
                flag = 2
                continue
            elif '[Tools list:]' in line:
                tmp_dic['Materials'] = tmp
                tmp = {}
                flag = 3
                continue

            if flag == 1:
                if 'Step' in line:
                    step_id = line.split(':')[0]
                    step_id = step_id.replace('Step', '').strip(' ')
                    step_id = int(step_id)
                    tool = line.split(':')[1]
                    tool = tool.strip(' ')
                    tmp[step_id] = tool
            elif flag == 2:
                material = line.split(':')[1]
                material = material.strip(' ')
                if material == 'None':
                    continue
                tmp += material + ', '
            elif flag == 3:
                tool = line.split(':')[0]
                tool = tool.strip(' ')
                try:
                    amount = line.split(':')[1]
                    amount = int(amount.strip(' '))
                    tmp[tool] = amount
                except:
                    tmp_dic['Tools'] = 'None'
                    print(line)
                    print(key)
        if 'Tools' not in tmp_dic:
            tmp_dic['Tools'] = tmp
        tmp_dic_dic[v_key] = tmp_dic
    save[key] = tmp_dic_dic
    with open('../data/match_tools/tools_analyse_parse.json', 'w') as f:
        json.dump(save, f, indent=4)