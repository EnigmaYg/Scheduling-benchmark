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


def solve_custom_jssp():
    model = cp_model.CpModel()

    # 定义工具集合
    tools = ['tool_a', 'tool_b', 'tool_c']
    all_tools = {tool: [] for tool in tools}

    horizon = 360  # 总时间范围，需根据实际任务总和估计

    # ========== TASK A ==========
    durations_a = [10, 2, 5, 1]
    uses_a = [['tool_a'], ['tool_b'], ['tool_b', 'tool_c'], ['tool_a']]
    task_a = []
    for i in range(4):
        start = model.NewIntVar(0, horizon, f'task_a_step{i}_start')
        end = model.NewIntVar(0, horizon, f'task_a_step{i}_end')
        interval = model.NewIntervalVar(start, durations_a[i], end, f'task_a_step{i}_interval')
        task_a.append((start, end, interval))

        for tool in uses_a[i]:
            all_tools[tool].append(interval)

    # tool_b 连续使用：step1 是 index=1，step2 是 index=2
    b_hold_start = task_a[1][0]
    b_hold_end = task_a[2][1]
    tool_b_hold_interval = model.NewIntervalVar(b_hold_start,
                                                model.NewIntVarFromDomain(
                                                    cp_model.Domain.FromIntervals([[durations_a[1] + 1, durations_a[1] + durations_a[2] + 10]]),
                                                    'tool_b_hold_len'),
                                                b_hold_end,
                                                'tool_b_hold_interval')
    all_tools['tool_b'].append(tool_b_hold_interval)

    # 定义 tool_b 锁定 interval（step2 到 step3 的最早可能结束）
    step2_end = task_a[1][1]
    step3_end = task_a[2][1]

    lock_b_interval = model.NewIntervalVar(step2_end,
                                           durations_a[2],
                                           step3_end,
                                           'tool_b_lock_during_gap')

    # 把这个 interval 也加到 tool_b 中
    all_tools['tool_b'].append(lock_b_interval)

    # 任务内顺序约束
    for i in range(3):
        model.Add(task_a[i+1][0] >= task_a[i][1])

    # ========== TASK B ==========
    durations_b = [10, 2, 3, 4, 80, 6]
    uses_b = [[], ['tool_a'], ['tool_b', 'tool_c'], ['tool_c'], ['tool_a'], ['tool_b', 'tool_c']]
    task_b = []
    for i in range(6):
        start = model.NewIntVar(0, horizon, f'task_b_step{i}_start')
        end = model.NewIntVar(0, horizon, f'task_b_step{i}_end')
        interval = model.NewIntervalVar(start, durations_b[i], end, f'task_b_step{i}_interval')
        task_b.append((start, end, interval))

        for tool in uses_b[i]:
            all_tools[tool].append(interval)

    # 顺序约束
    for i in range(5):
        model.Add(task_b[i+1][0] >= task_b[i][1])

    # ========== 工具资源约束 ==========
    for tool, intervals in all_tools.items():
        model.AddNoOverlap(intervals)

    # ========== 目标函数：最短完成时间 ==========
    makespan = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(makespan, [task_a[-1][1], task_b[-1][1]])
    model.Minimize(makespan)

    # ========== 求解 ==========
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f'Minimum total time (makespan): {solver.Value(makespan)} minutes\n')

        for i, step in enumerate(task_a):
            print(f'Task A - Step {i+1}: start at {solver.Value(step[0])}, end at {solver.Value(step[1])}')
        for i, step in enumerate(task_b):
            print(f'Task B - Step {i+1}: start at {solver.Value(step[0])}, end at {solver.Value(step[1])}')
    else:
        print('No solution found.')


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
            start = model.NewIntVar(0, 10000, f'{job_name}_{i}_start')
            end = model.NewIntVar(0, 10000, f'{job_name}_{i}_end')
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
        gap_size = model.NewIntVar(0, 10000, f'{job_name}_{i}_{j}_gap_dur')
        model.Add(gap_size == gap_end - gap_start)

        dummy_interval = model.NewIntervalVar(gap_start, gap_size, gap_end, f'{job_name}_{i}_{j}_gap_{tool}')
        tool_intervals[tool].append(dummy_interval)

    for tool, intervals in tool_intervals.items():
        model.AddNoOverlap(intervals)
    # 步骤4：makespan 最小化
    all_ends = [step_vars[(job, len(steps) - 1)][2] for job, steps in tasks.items()]
    makespan = model.NewIntVar(0, 10000, 'makespan')
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
        print(result)
        return result
    else:
        print("❌ No feasible solution found.")
        return None


# tasks = {
#     'taskA': [10, 10, 5, 10],
#     'taskB': [10, 10, 10, 10, 12, 6]
# }
#
# tool_usage = {
#     'taskA': [['a'], ['b'], ['b', 'a'], ['a']],
#     'taskB': [['a'], ['c'], ['b'], ['c'], ['b'], ['a, c']]
# }

tasks = {
    'taskA': [10, 80],
    'taskB': [10, 10, 10, 10]
}

tool_usage = {
    'taskA': [['b'], ['b', 'a']],
    'taskB': [['a'], ['b'], ['c'], ['c']]
}

continuous_tool_usage = [
    ('taskA', 0, 1, 'b'),  # 表示 taskA 的第1步 和 第2步之间，tool b 要连续占用（注意从0开始计数）
]

schedule_tasks_with_explicit_tool_lock(tasks, tool_usage, continuous_tool_usage)