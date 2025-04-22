import json


def parse_results():
    with open('../data/time_step/Wikihow_time_estimation.json', 'r') as f:
        times = json.load(f)

    cnt = 0
    all_cnt = 0
    save = {}
    # save_ = {}
    for key, value in times.items():
        tmp_dic = {}
        for v_key, v_value in value.items():
            all_cnt += 1
            value_list = v_value.split('\n')
            tmp_list = []
            for line in value_list:
                # if 'Step' not in line:
                #     print(key, v_key)
                if 'None' in line:
                    tmp_list.append('None')
                    continue
                if len(line) == 0:
                    continue
                minutes = line.split(':')[1]
                seconds_string = ''
                minutes_string = ''
                hours_string = ''
                if 'minutes' in minutes:
                    minutes_string = minutes.replace('minutes', '')
                elif 'minute' in minutes:
                    minutes_string = minutes.replace('minute', '')
                elif 'seconds' in minutes:
                    seconds_string = minutes.replace('seconds', '')
                elif 'second' in minutes:
                    seconds_string = minutes.replace('second', '')
                elif 'hours' in minutes:
                    seconds_string = minutes.replace('hours', '')
                elif 'hour' in minutes:
                    seconds_string = minutes.replace('hour', '')
                else:
                    print(key, v_key, line)
                minutes_number = 0
                if len(minutes_string) != 0:
                    minutes_string = minutes_string.strip(' ')
                    minutes_number = 0
                    try:
                        minutes_number = int(minutes_string)
                    except:
                        try:
                            float(minutes_string)
                        except ValueError:
                            print('minutes FAIL', key, v_key, line)
                            # print("无法转换为int或float")
                elif len(seconds_string) != 0:
                    seconds_string = seconds_string.strip(' ')
                    seconds_number = 0
                    try:
                        seconds_number = float(seconds_string)
                    except:
                        print('seconds FAIL', key, v_key, line)
                    minutes_number = round(seconds_number / 60, 2)
                else:
                    hours_string = hours_string.strip(' ')
                    hours_number = 0
                    try:
                        hours_number = int(hours_number)
                    except:
                        print('hours FAIL', key, v_key, line)
                    minutes_number = hours_number * 60
                tmp_list.append(minutes_number)
            tmp_dic[v_key] = tmp_list
        if len(tmp_dic) != 0:
            save[key] = tmp_dic

    print(all_cnt)
    cnt = 0
    save_ = {}
    for key, value in save.items():
        tmp_dic = {}
        for v_key, v_value in value.items():
            flag = 0
            if 'None' in v_value:
                cnt += 1
                flag = 1
            else:
                for x in v_value:
                    if x > 60:
                        cnt += 1
                        flag = 1
                        break
            if flag == 0:
                tmp_dic[v_key] = v_value
        if len(tmp_dic) != 0:
            save_[key] = tmp_dic
    print(cnt)
    cnt = 0
    for key, value in save_.items():
        cnt += len(value)
    print(cnt)

    with open('../data/time_step/Wikihow_time_filtered.json', 'w') as f:
        json.dump(save_, f, indent=4)


def split_time_range():
    with open('../data/time_step/Wikihow_time_filtered.json', 'r') as f:
        data = json.load(f)

    number_list = []
    save = {'part1': {}, 'part2': {}, 'part3': {}, 'part4': {}}
    for key, value in data.items():
        for v_key, v_value in value.items():
            total_time = 0
            for x in v_value:
                total_time += x
            number_list.append(total_time)
    sorted_numbers = sorted(number_list)
    # print(len(sorted_numbers))
    part1 = sorted_numbers[:1632]
    part2 = sorted_numbers[1632:3265]
    part3 = sorted_numbers[3265:4897]
    part4 = sorted_numbers[4897:]
    boundary1 = (part1[0], part1[-1])
    boundary2 = (part2[0], part2[-1])
    boundary3 = (part3[0], part3[-1])
    boundary4 = (part4[0], part4[-1])
    # print(part1[0], part1[-1])
    # print(part2[0], part2[-1])
    # print(part3[0], part3[-1])
    # print(part4[0], part4[-1])

    for key, value in data.items():
        for v_key, v_value in value.items():
            total_time = 0
            for x in v_value:
                total_time += x
            if total_time in boundary1:
                if key not in save['part1']:
                    save['part1'][key] = [v_key]
                else:
                    save['part1'][key].append(v_key)
            elif total_time in boundary2:
                if key not in save['part2']:
                    save['part2'][key] = [v_key]
                else:
                    save['part2'][key].append(v_key)
            elif total_time in boundary3:
                if key not in save['part3']:
                    save['part3'][key] = [v_key]
                else:
                    save['part3'][key].append(v_key)
            else:
                if key not in save['part4']:
                    save['part4'][key] = [v_key]
                else:
                    save['part4'][key].append(v_key)

    with open('../data/time_step/Wikihow_time_cluster.json', 'w') as f:
        json.dump(save, f, indent=4)


with open('../data/time_step/Wikihow_time_filtered.json', 'r') as f:
    data = json.load(f)

save = {}
cnt = 0
for key, value in data.items():
    tmp_dic = {}
    for v_key, v_value in value.items():
        if (sum(v_value) >= 10) and (sum(v_value) <= 180):
            tmp_dic[v_key] = v_value
            cnt += 1
        if sum(v_value) > 180:
            print(key)
    if len(tmp_dic) != 0:
        save[key] = tmp_dic
print(cnt)
print(len(save))
# with open('../data/time_step/Wikihow_time_GT10.json', 'w') as f:
#     json.dump(save, f, indent=4)