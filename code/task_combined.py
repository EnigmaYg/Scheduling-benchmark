import json

with open('../data/tmp/Wikihow_sample_tools_parse.json', 'r') as f:
    main_tools = json.load(f)

with open('../data/tmp/Wikihow_sample_tools_retrieved_parse.json', 'r') as f:
    rt_tools = json.load(f)

with open('../data/tmp/Wikihow_sample_retrieve.json', 'r') as f:
    pairs = json.load(f)

save = {}
for key, value in pairs.items():
    tools = main_tools[key]['Tools']
    if tools == 'None':
        continue
    tools_list = list(tools.keys())
    tmp_list = []
    for v_value in value:
        tmp_tools = rt_tools[v_value[0]]['Tools']
        for x in tools_list:
            if x in tmp_tools:
                tmp_list.append(v_value[0])
                break
    save[key] = tmp_list

with open('../data/tmp/Wikihow_sample_paired.json', 'w') as f:
    json.dump(save, f, indent=4)