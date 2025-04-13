import json

with open('../data/Wikihow_time.json', 'r') as f:
    times = json.load(f)

cnt = 0
save = {}
save_ = {}
for key, value in times.items():
    flag = 0
    tmp_dic = {}
    for v_key, v_value in value.items():
        value_list = v_value.split('\n')
        if flag == 1:
            save_[key] = value
            break
        tmp_list = []
        for line in value_list:
            # if 'Step' not in line:
            #     print(key, v_key)
            if 'None' in line:
                flag = 1
                cnt += 1
                break
            minutes = line.split(':')[1]
            seconds_string = ''
            minutes_string = ''
            if 'minutes' in minutes:
                minutes_string = minutes.replace('minutes', '')
            elif 'minute' in minutes:
                minutes_string = minutes.replace('minute', '')
            elif 'seconds' in minutes:
                seconds_string = minutes.replace('seconds', '')
            else:
                print(key, v_key, line)
            if len(seconds_string) == 0:
                minutes_string = minutes_string.strip(' ')
                minutes_number = 0
                try:
                    minutes_number = int(minutes_string)
                except:
                    try:
                        float(minutes_string)
                    except ValueError:
                        print(key, v_key, line)
                        # print("无法转换为int或float")
            else:
                seconds_string = seconds_string.strip(' ')
                seconds_number = 0
                try:
                    seconds_number = int(seconds_string)
                except:
                    print(key, v_key, line)
                minutes_number = seconds_number / 60
            if (minutes_number > 60):
                cnt += 1
                flag = 1
                break
            tmp_list.append(minutes_number)
        tmp_dic[v_key] = tmp_list
    if flag == 0:
        save[key] = tmp_dic
print(cnt)
print(len(save))
print(len(times))
with open('../data/Wikihow_time_None.json', 'w') as f:
    json.dump(save_, f, indent=4)
# with open('../data/Wikihow_time_appropriate.json', 'w') as f:
#     json.dump(save, f, indent=4)
