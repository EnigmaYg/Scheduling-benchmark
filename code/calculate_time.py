import json
from ortools.sat.python import cp_model


def schedule_tasks(tasks: dict, conflicts: list, time_limit: int = 10):
    model = cp_model.CpModel()
    step_vars = {}

    # 1. 创建变量并添加顺序约束
    for job_name, steps in tasks.items():
        previous_step = None
        for i, duration in enumerate(steps):
            step_id = (job_name, i)
            start_var = model.NewIntVar(0, 10000, f'{job_name}_{i}_start')
            step_vars[step_id] = (start_var, duration)

            if previous_step:
                prev_start, prev_duration = previous_step
                model.Add(start_var >= prev_start + prev_duration)
            previous_step = (start_var, duration)

    # 2. 添加冲突约束（使用 IntervalVar + AddNoOverlap）
    for j1, j2 in conflicts:
        s1, d1 = step_vars[j1]
        s2, d2 = step_vars[j2]
        interval1 = model.NewIntervalVar(s1, d1, s1 + d1, f'{j1}')
        interval2 = model.NewIntervalVar(s2, d2, s2 + d2, f'{j2}')
        model.AddNoOverlap([interval1, interval2])

    # 3. 定义目标函数：makespan 最小
    end_times = [step_vars[(job, len(steps) - 1)][0] + step_vars[(job, len(steps) - 1)][1]
                 for job, steps in tasks.items()]
    makespan = model.NewIntVar(0, 10000, 'makespan')
    model.AddMaxEquality(makespan, end_times)
    model.Minimize(makespan)

    # 4. 求解
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(model)

    # 5. 输出结果
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result = {
            'makespan': solver.Value(makespan),
            'schedule': {}
        }
        for job in tasks:
            result['schedule'][job] = []
            for i in range(len(tasks[job])):
                var, dur = step_vars[(job, i)]
                result['schedule'][job].append({
                    'step': i + 1,
                    'start': solver.Value(var),
                    'duration': dur
                })
        return result
    else:
        return None


def main():
    with open('../data/filtered_instructions/Wikihow_filtered_instructions.json', 'r') as f:
        instruct_answers = json.load(f)

    with open('../data/time_step/Wikihow_time_filtered.json', 'r') as f:
        times = json.load(f)

    with open('../data/tmp/Wikihow_sample_paired.json', 'r') as f:
        paired = json.load(f)

    with open('../data/tmp/Wikihow_sample_tools_parse.json', 'r') as f:
        tools = json.load(f)

    with open('../data/tmp/Wikihow_sample_tools_retrieved_parse.json', 'r') as f:
        other_tools = json.load(f)

    save = {}
    for key, value in paired.items():
        question = key.split('_')[0]
        idx = key.split('_')[1]
        time_list = times[question][idx]
        step_dic = tools[key]['Tool_steps']
        tool2step_dic = {}
        for s_key, s_value in step_dic.items():
            if ',' in s_value:
                s_value_list = s_value.split(',')
                for x in s_value_list:
                    if x.strip(' ') in tool2step_dic:
                        tool2step_dic[x.strip(' ')].append(s_key)
                    else:
                        tool2step_dic[x.strip(' ')] = [s_key]
            else:
                if s_value in tool2step_dic:
                    tool2step_dic[s_value].append(s_key)
                else:
                    tool2step_dic[s_value] = [s_key]
        tool_list = list(tools[key]['Tools'])
        time_sum = sum(time_list)
        tmp_dic = {}
        # parse each pair question
        for pair_question in value:
            question = pair_question.split('_')[0]
            idx = pair_question.split('_')[1]
            tmp_time_list = times[question][idx]
            tmp_step_dic = other_tools[pair_question]['Tool_steps']
            tmp_tool2step_dic = {}
            for s_key, s_value in tmp_step_dic.items():
                if ',' in s_value:
                    s_value_list = s_value.split(',')
                    for x in s_value_list:
                        if x.strip(' ') in tmp_tool2step_dic:
                            tmp_tool2step_dic[x.strip(' ')].append(s_key)
                        else:
                            tmp_tool2step_dic[x.strip(' ')] = [s_key]
                else:
                    if s_value in tmp_tool2step_dic:
                        tmp_tool2step_dic[s_value].append(s_key)
                    else:
                        tmp_tool2step_dic[s_value] = [s_key]
            tmp_tool_list = list(other_tools[pair_question]['Tools'])
            # get the conflict steps
            conflict_steps_list = []
            for tool in tmp_tool_list:
                if tool in tool_list:
                    for x in tool2step_dic[tool]:
                        for y in tmp_tool2step_dic[tool]:
                            conflict_steps_list.append((('A', int(x)-1), ('B', int(y)-1)))
            # get the tasks time
            scale = 100
            tasks = {'A': [int(t * scale) for t in time_list], 'B': [int(t * scale) for t in tmp_time_list]}
            # print(conflict_steps_list)
            # print(tasks)
            # print(schedule_tasks(tasks, conflict_steps_list))
            tmp_dic[pair_question] = schedule_tasks(tasks, conflict_steps_list)
        save[key] = tmp_dic
    with open('../data/tmp/Wikihow_sample_best_scheduling.json', 'w') as f:
        json.dump(save, f, indent=4)


from ortools.sat.python import cp_model


def schedule_tasks_with_explicit_tool_lock(tasks, tool_usage, continuous_tool_usage, time_limit=10):
    model = cp_model.CpModel()
    step_vars = {}         # 保存每一步的变量: (start_time, duration, end_time)
    interval_vars = {}     # 保存每一步对应的 interval
    tool_intervals = {}    # 每个工具对应的 interval 列表，用于 AddNoOverlap

    # 获取所有用到的工具
    all_tools = set(
        tool for steps in tool_usage.values() for tools in steps for tool in tools if tool
    )
    for tool in all_tools:
        tool_intervals[tool] = []

    # 步骤1：创建每个任务的 step 的变量和 interval
    for job_name, steps in tasks.items():
        previous_step = None
        for i, duration in enumerate(steps):
            step_id = (job_name, i)
            start = model.NewIntVar(0, 36000, f'{job_name}_{i}_start')
            end = model.NewIntVar(0, 36000, f'{job_name}_{i}_end')
            interval = model.NewIntervalVar(start, duration, end, f'{job_name}_{i}_interval')

            step_vars[step_id] = (start, duration, end)
            interval_vars[step_id] = interval

            # 添加到工具的 interval 列表中
            for tool in tool_usage[job_name][i]:
                if tool:
                    tool_intervals[tool].append(interval)

            # 顺序约束：step i+1 开始时间 ≥ step i 结束时间
            if previous_step:
                model.Add(start >= previous_step[2])
            previous_step = (start, duration, end)

    # 步骤2：为每个工具添加 AddNoOverlap（工具不能被同时使用）
    # for tool, intervals in tool_intervals.items():
    #     model.AddNoOverlap(intervals)

    # 步骤3：添加显式定义的“连续占用”工具约束
    for job_name, i, j, tool in continuous_tool_usage:
        if (job_name, i) not in step_vars or (job_name, j) not in step_vars:
            continue  # 防御性检查

        s_i, d_i, e_i = step_vars[(job_name, i)]
        s_j, d_j, e_j = step_vars[(job_name, j)]

        # dummy_interval: 工具 b 从 step i 结束 到 step j 开始期间保持占用
        gap_start = e_i
        gap_end = s_j
        gap_size = model.NewIntVar(0, 36000, f'{job_name}_{i}_{j}_gap_dur')
        model.Add(gap_size == gap_end - gap_start)

        dummy_interval = model.NewIntervalVar(gap_start, gap_size, gap_end, f'{job_name}_{i}_{j}_gap_{tool}')
        tool_intervals[tool].append(dummy_interval)

    for tool, intervals in tool_intervals.items():
        model.AddNoOverlap(intervals)
    # 步骤4：makespan 最小化
    all_ends = [step_vars[(job, len(steps) - 1)][2] for job, steps in tasks.items()]
    makespan = model.NewIntVar(0, 36000, 'makespan')
    model.AddMaxEquality(makespan, all_ends)
    model.Minimize(makespan)

    # 步骤5：求解模型
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(model)

    # 步骤6：输出结果
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result = {'makespan': solver.Value(makespan), 'schedule': {}}
        for job in tasks:
            result['schedule'][job] = []
            for i in range(len(tasks[job])):
                start, dur, _ = step_vars[(job, i)]
                result['schedule'][job].append({
                    'step': i + 1,
                    'start': solver.Value(start),
                    'duration': dur
                })
        return result
    else:
        print("❌ No feasible solution found.")
        return "None"


# tasks = {
#     'taskA': [10, 10, 5, 10],
#     'taskB': [10, 10, 10, 10, 12, 6]
# }
#
# tool_usage = {
#     'taskA': [['a'], ['b'], ['b', 'a'], ['a']],
#     'taskB': [['a'], ['c'], ['b'], ['c'], ['b'], ['a, c']]
# }

with open('../data/match_tools/pair_tools_cars.json', 'r') as f:
    tools = json.load(f)

with open('../data/time_step/Wikihow_time_GT10.json', 'r') as f:
    times = json.load(f)

save = {'Conflict': [], 'Parallel': []}
cnt1 = 0
cnt2 = 0
for key, value in tools.items():
    for v_key, v_value in value.items():
        tmp_dic = {}
        tmp_time1 = times[key.split('_')[0]][key.split('_')[1]]
        time1 = []
        for x in tmp_time1:
            time1.append(int(x * 100))
        tmp_time2 = times[v_key.split('_')[0]][v_key.split('_')[1]]
        time2 = []
        for x in tmp_time2:
            time2.append(int(x * 100))

        max_time = max(sum(time1), sum(time2))

        tool_list1 = []
        for tmp_key, tmp_value in v_value[0].items():
            tmp_tool_list = []
            for x in tmp_value.split(','):
                if x.strip(' ') not in tmp_tool_list:
                    tmp_tool_list.append(x.strip(' '))
            if tmp_tool_list[0] == 'None':
                tmp_tool_list = []
            tool_list1.append(tmp_tool_list)
        tool_list2 = []
        for tmp_key, tmp_value in v_value[1].items():
            tmp_tool_list = []
            for x in tmp_value.split(','):
                if x.strip(' ') not in tmp_tool_list:
                    tmp_tool_list.append(x.strip(' '))
            if tmp_tool_list[0] == 'None':
                tmp_tool_list = []
            tool_list2.append(tmp_tool_list)
        tasks = {
            'taskA': time1,
            'taskB': time2
        }

        tool_usage = {
            'taskA': tool_list1,
            'taskB': tool_list2
        }

        continuous_tool_usage = []

        result = schedule_tasks_with_explicit_tool_lock(tasks, tool_usage, continuous_tool_usage)
        result['max_time'] = max_time
        tmp_dic[key + '+' + v_key] = result
        if result == 'None':
            continue
        if result['makespan'] > max_time:
            cnt1 += 1
            save['Conflict'].append(tmp_dic)
        elif result['makespan'] == max_time:
            cnt2 += 1
            save['Parallel'].append(tmp_dic)
        else:
            print(key, v_key)
print(cnt1, cnt2)
with open('../data/schedule_results/Schedule_grd_cars.json', 'w') as f:
    json.dump(save, f, indent=4)
# tasks = {
#     'taskA': [10, 80],
#     'taskB': [10, 10, 10, 10]
# }
#
# tool_usage = {
#     'taskA': [['b'], ['b', 'a']],
#     'taskB': [['a'], ['b'], ['c'], ['c']]
# }
#
# continuous_tool_usage = [
#     ('taskA', 0, 1, 'b'),  # 表示 taskA 的第1步 和 第2步之间，tool b 要连续占用（注意从0开始计数）
# ]

# schedule_tasks_with_explicit_tool_lock(tasks, tool_usage, continuous_tool_usage)