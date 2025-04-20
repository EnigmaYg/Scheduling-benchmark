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


