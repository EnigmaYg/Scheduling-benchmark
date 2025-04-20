import json

# with open('WikiHow_Resource_Assumption_Simplification.json', 'r') as f:
#     result = json.load(f)
#
# with open('WikiHow_Resource_Assumption_Simplification2.json', 'r') as f:
#     result2 = json.load(f)
#
# save = {}
# for key, value in result.items():
#     save[key] = value
# for key, value in result2.items():
#     if key in save:
#         continue
#     save[key] = value
#
# print(len(save))
# cnt = 0
# tmp_save = {}
# all_cnt = 0
# for key, value in save.items():
#     if cnt > len(save) / 4:
#         with open(f'WikiHow_Resource_Assumption_Simplification_{all_cnt}.json', 'w') as f:
#             json.dump(tmp_save, f, indent=4)
#         all_cnt += 1
#         cnt = 0
#         tmp_save = {}
#     tmp_save[key] = value
#     cnt += 1
# with open(f'WikiHow_Resource_Assumption_Simplification_3.json', 'w') as f:
#     json.dump(tmp_save, f, indent=4)
# with open('WikiHow_Resource_Assumption_Simplification_all.json', 'w') as f:
#     json.dump(save, f, indent=4)

# cnt = 0
# save = {}
#
# with open(f'Wikihow_time_estimation1.json', 'r') as f:
#     result = json.load(f)
# with open(f'Wikihow_time_estimation2.json', 'r') as f:
#     result2 = json.load(f)
# for key, value in result.items():
#     save[key] = value
# for key, value in result2.items():
#     save[key] = value
# print(len(save))
# with open('Wikihow_time_estimation.json', 'w') as f:
#     json.dump(save, f, indent=4)
# with open('WikiHow_Immediate_Scope_Focus_all.json', 'w') as f:
#     json.dump(save, f, indent=4)

with open('filtered_instructions/WikiHow_Immediate_Scope_Focus_all.json', 'r') as f:
    instructions = json.load(f)

with open('time_step/Wikihow_time_filtered.json', 'r') as f:
    times = json.load(f)

with open('setting_setup/Wikihow_filtered_settings.json', 'r') as f:
    settings = json.load(f)

data = {}
cnt = 0
for key, value in times.items():
    tmp_dic = {}
    for v_key, v_value in value.items():
        if len(v_value) != len(instructions[key][v_key].split('\n')):
            print(key, v_key)
        tmp_dic[v_key] = instructions[key][v_key].split('\n')
    if len(tmp_dic) != 0:
        data[key] = tmp_dic
print(cnt)
with open('filtered_instructions/Wikihow_filtered_instructions.json', 'w') as f:
    json.dump(data, f, indent=4)
