import json

# with open('../data/match_tools/tools_analyse.json', 'r') as f:
#     data = json.load(f)
#
# with open('../data/match_tools/tmp_tools_analyse_parse_del_tool_in_material.json', 'r') as f:
#     save = json.load(f)
#
# print(len(save))
# # save = {}
# for key, value in data.items():
#     if key in save:
#         continue
#     tmp_dic_dic = {}
#     for v_key, value in value.items():
#         flag = 0
#         tmp_dic = {}
#         for line in value.split('\n'):
#             if len(line) == 0:
#                 continue
#             if '[Tools:]' in line:
#                 tmp = {}
#                 flag = 1
#                 continue
#             elif '[Materials:]' in line:
#                 tmp_dic['Tool_steps'] = tmp
#                 tmp = ''
#                 flag = 2
#                 continue
#             elif '[Tools list:]' in line:
#                 tmp_dic['Materials'] = tmp
#                 tmp = {}
#                 flag = 3
#                 continue
#
#             if flag == 1:
#                 if 'Step' in line:
#                     step_id = line.split(':')[0]
#                     step_id = step_id.replace('Step', '').strip(' ')
#                     step_id = int(step_id)
#                     tool = line.split(':')[1]
#                     tool = tool.strip(' ')
#                     tmp[step_id] = tool
#             elif flag == 2:
#                 material = line.split(':')[1]
#                 material = material.strip(' ')
#                 if material == 'None':
#                     continue
#                 tmp += material + ', '
#             elif flag == 3:
#                 tool = line.split(':')[0]
#                 tool = tool.strip(' ')
#                 try:
#                     amount = line.split(':')[1]
#                     amount = int(amount.strip(' '))
#                     tmp[tool] = amount
#                 except:
#                     tmp_dic['Tools'] = 'None'
#                     print(line)
#                     print(key)
#         if 'Tools' not in tmp_dic:
#             tmp_dic['Tools'] = tmp
#         tmp_dic_dic[v_key] = tmp_dic
#     save[key] = tmp_dic_dic
#     with open('../data/match_tools/tools_analyse_parse.json', 'w') as f:
#         json.dump(save, f, indent=4)


with open('../data/tmp/tmp_tools_analyse_parse_match_tool_step_with_tools.json', 'r') as f:
    data = json.load(f)

save = {}
for key, value in data.items():
    save_dic = {}
    for v_key, v_value in value.items():
        if v_value["Tools"] == 'None':
            continue
        tmp_list = v_value["Materials"].split(',')
        material_list = []
        for material in tmp_list:
            material = material.strip(' ')
            if len(material) > 0:
                material_list.append(material)
        tmp_dic = v_value['Tool_steps']
        tools_list = list(v_value['Tools'].keys())
        replace_dic = {}
        for tool in tools_list:
            if ' or ' in tool:
                replace_dic[tool] = tool.split('or')[0].strip(' ')
        new_tools = {}
        for tmp_key, tmp_value in v_value['Tools'].items():
            if tmp_key in replace_dic:
                new_tools[replace_dic[tmp_key]] = tmp_value
            else:
                new_tools[tmp_key] = tmp_value
        v_value['Tools'] = new_tools
        new_tools_step = {}
        for tmp_key, tmp_value in tmp_dic.items():
            tmp_tool_list = tmp_value.split(',')
            # delet_list = []
            new_tool_list = []
            for tmp_tool in tmp_tool_list:
                tmp_tool = tmp_tool.split('(')[0].strip(' ')
                if tmp_tool in replace_dic:
                    new_tool_list.append(replace_dic[tmp_tool])
                else:
                    new_tool_list.append(tmp_tool)

            #     origin_tool = tmp_tool
            #     if '(' in tmp_tool:
            #         tmp_tool = tmp_tool.split('(')[0]
            #     tmp_tool = tmp_tool.strip(' ')
            #     if tmp_tool not in tools_list:
            #         delet_list.append(origin_tool)
            # for tmp_tool in delet_list:
            #     tmp_tool_list.remove(tmp_tool)
            # if len(tmp_tool_list) == 0:
            #     tmp_tool_list.append('None')
            new_tools_step[tmp_key] = ','.join(new_tool_list)
        v_value['Tool_steps'] = new_tools_step
        save_dic[v_key] = v_value
    save[key] = save_dic


with open('../data/tmp/tmp_tools_analyse_parse_move_or_tools.json', 'w') as f:
    json.dump(save, f, indent=4)