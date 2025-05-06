import json
import os
from openai import OpenAI
import re

client = OpenAI(
    api_key="sk-rh8wi5OXclyhFu7spfK69E7UHU5BkOdIqRsl0xslPiFRgQg3",
    base_url="https://api.key77qiqi.cn/v1"
)

# client = OpenAI(api_key="sk-b102ebd6c4884ba7a6f745ee1d558d19", base_url="https://api.deepseek.com")
# sk-b102ebd6c4884ba7a6f745ee1d558d19, my: sk-36bb76d68d1d46e0b93de07e2b907546

def get_prompt(question, answer):
    Prompt = f'''You are an expert in solving procedural problems. You are tasked with analyzing the tools, and materials required for solving a procedural problem. For each step of the process, you need to output with the following rules: 
1. For each step, list the tools (minimum necessary tools to complete the task) and materials (expendables or consumables required for the step) separately.
2. For each step, also list the Carried-over Tools: the tool must have been used in the immediately preceding step only (not any earlier steps); the tool must remain uninterrupted in use between the two steps.
3. If a step does not require any tools, explicitly state None.
4. Prioritize reusing tools from previous steps to minimize the total number of tools required.
5. Only list the essential tools required to complete the task. Avoid mentioning unnecessary or redundant tools.
6. Finally, provide a complete list of all tools and their quantities used in all steps of the process(only one is needed if it can be reused).

Give two examples and clarify the definition of Carried-over Tools.
Example1:
[Procedural Question:]
How To Make Hunch Punch
[Instructional Answer:]
1. Mix a bottle of Everclear with a gallon of fruit punch in a large container.
2. Mix in a few cups of lemon lime soda, ginger ale, and your favorite fruit juices.
3. Add ice to chill the drink.

Your response:
[Tools:]
Step 1: Large container, Stirring spoon
Step 2: Large container(Carried-over Tools), Stirring spoon
Step 3: Large container(Carried-over Tools)

[Materials:]
Step 1: Everclear, Fruit punch
Step 2: Lemon lime soda, Ginger ale, Fruit juices
Step 3: Ice

[Tools list:]
Large container: 1
Stirring spoon: 1

* Explanation(You don't need to output this in your response): Because the Large container is a container shared by step 1, step 2, and step 3, if the Large container is used for other tasks before step 2 or step 3, it does not comply.

[Example2:]
[Procedural Question:]
How To Get Whites White
[Instructional Answer:]
1. Apply baking soda to the discolored area of the clothing.
2. Rub the cut side of a lemon onto the same spot.
3. Start the washer with detergent.
4. Wait 5 minutes.
5. Add bleach to the washer.
6. Add the clothes to the washer.

Your response:
[Tools:]
Step 1: Measuring spoon
Step 2: Knife
Step 3: Washing machine
Step 4: Washing machine(Carried-over Tools)
Step 5: Washing machine(Carried-over Tools), Measuring spoon
Step 6: Washing machine(Carried-over Tools)

[Materials:]
Step 1: Baking soda
Step 2: Lemon
Step 3: Laundry detergent
Step 4: None
Step 5: Bleach
Step 6: Clothes

[Tools list:]
Measuring spoon: 1
Knife: 1
Washing machine: 1

* Explanation(You don't need to output this in your response): Because step 3, step 4, step 5 and step 6 all require continuous processing of the washing machine, if the washing machine is used for other tasks before step 4, step 5 or step 6, it does not comply.


Given a question and its answer below. Please respond without any other explanation or irrelevant information.
[Procedural Question:]
{question}
[Instructional Answer:]
{answer}

Your response:
'''
    return Prompt


def get_prompt2(question, answer, tools):
    Prompt = f'''You are an expert in procedural task analysis. Given a step-by-step process for completing a task, where each step uses one or more tools, your job is to evaluate whether each tool can be replaced by one or more alternative tools from a provided list. For each original tool, if a suitable replacement exists that can still complete the step effectively, suggest it. If no viable replacement exists, return "None".

Output format:
Original tool : Replaced tool
Original tool : None
...


Given a question, its answer and tools list below. Please respond without any other explanation or irrelevant information.
[Procedural question:]
{question}
[Instructional answer:]
{answer}
[Tools list:]
{tools}

Your response:
'''
    return Prompt


def get_prompt3(question1, answer1, question2, answer2, tools, materials, examples):
    Prompt = f'''You are an expert in solving procedural problems. Now, you are presented with two procedural tasks, each accompanied by a list of steps, along with the time and tools required for each step. Although there are unlimited materials available to complete the tasks, the number of available tools is limited. Your task is to determine, based on the limited tools, whether it is possible to complete both tasks concurrently, and to propose the optimal plan.
Please note that your focus is on allocating tools and scheduling the completion plan — you do not need to consider human resource limitations or any tool transportation or movement issues.
{examples}
[Task A:] 
{question1}
[Instructions A:]
{answer1}

[Task B:] 
{question2}
[Instructions B:]
{answer2}


Now there are the following tools, the number of which is in brackets: {tools}
And unlimited materials, such as: {materials}
Please analyze whether you can complete this task and give the most efficient operation plan. If you can complete it, please output the results in the order of steps, indicating which step of the problem it is, and the tools used. Finally, calculate the total time to complete all tasks. The shortest time is required, that is, the most efficient operation. Please follow the following format:
A.1 (start at minutes x, end at minutes x) Tool X 
B.1 (start at minutes x, end at minutes x) Tool X 
A.1 (start at minutes x, end at minutes x) Tool X 
...
[Total time: x minutes]

If it cannot be completed, directly output FAIL

Your response:

'''
    return Prompt


def jssp_prompt(instruction1, instruction2, machine_num):
    Prompt = f'''Optimize schedule for 2 Jobs across {machine_num} Machines to minimize makespan. Each job involves a series of Operations needing specific machines and times. Operations are processed in order, without interruption, on a single Machine at a time.

Problem: 
Job 0 contains the following operations:
{instruction1}

Job 1 contains the following operations:
{instruction2}

Please use heuristic thinking to give potential conflicting constraints and final plan. Then answer the question with the following format:
plan: xxx
[Total time: x minutes]

Your response:
'''
    return Prompt


def graph_prompt(json_str):
    Prompt = f'''Your task is to generate an optimal plan that achieves the goal—completing all tasks in the shortest possible time. Each tool is available in only one unit, and you need to start from two different starting points to complete two final steps respectively. Tasks without tool conflicts can be performed in parallel to improve overall efficiency.
    
{json_str}

Output format:
[Total time: x minutes]

Please respond without any other explanation or irrelevant information.
Your response:
'''
    return Prompt


def run_llm(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        # model="deepseek-reasoner",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return completion.choices[0].message.content
    # return [completion.choices[0].message.content, completion.choices[0].message.reasoning_content]


def tool_analyse():
    with open('../data/tmp/Tools_Pets_and_Animals_pair.json', 'r') as f:
        pairs = json.load(f)

    with open('../data/filtered_instructions/Wikihow_filtered_instructions.json', 'r') as f:
        data = json.load(f)

    with open('../data/match_tools/tools_analyse_parse.json', 'r') as f:
        tools = json.load(f)

    with open('../data/match_tools/Pet_paired_tools.json', 'r') as f:
        save = json.load(f)

    # save = {}
    cnt = 0
    print(len(save))
    for key, value in pairs.items():
        if key in save:
            continue
        print(key)
        key_question = key.split('_')[0]
        key_idx = key.split('_')[1]
        tools_dic = tools[key_question][key_idx]["Tools"]
        tools_list = []
        tmp_dic = {}
        for tmp_key, tmp_value in tools_dic.items():
            tools_list.append(tmp_key)
        for paired in value:
            paired_question = paired.split('_')[0]
            paired_idx = paired.split('_')[1]
            instructions = data[paired_question][paired_idx]
            tools_dic = tools[paired_question][paired_idx]["Tool_steps"]
            tmp_tool_list = []
            for tmp_key, tmp_value in tools_dic.items():
                tmp_tool_list.append(tmp_value)
            answer = ''
            for instruction in instructions:
                answer += instruction + f' (Tool: {tmp_tool_list[instructions.index(instruction)]})' + '\n'
            prompt = get_prompt2(paired_question, answer, ', '.join(tools_list))
            response = run_llm(prompt)
            tmp_dic[paired] = response
        save[key] = tmp_dic
        with open('../data/match_tools/Pet_paired_tools.json', 'w') as f:
            json.dump(save, f, indent=4)



def schedule_analyse():
    with open('../data/filtered_instructions/Wikihow_filtered_instructions.json', 'r') as f:
        instructions = json.load(f)

    with open('../data/time_step/Wikihow_time_GT10.json', 'r') as f:
        times = json.load(f)

    with open('../data/match_tools/pair_tools_cars.json', 'r') as f:
        paired = json.load(f)

    with open('../data/match_tools/tools_analyse_parse.json', 'r') as f:
        tools = json.load(f)

    # with open('../data/schedule_results/R1_cars.json', 'r') as f:
    #     save = json.load(f)

    save = {}
    example = '''\n\nFor example:
[Task A:] 
To Remove Chewing Gum from a Car Seat
[Instructions A:]
1. Place 3 to 4 ice cubes in a sealed plastic bag. (Time: 1 minute(s)) (Tools: Ice, Sealed plastic bag)
2. Set the bag on top of the gum and let it sit for about 5 minutes. (Time: 5 minute(s)) (Tools: Ice, Sealed plastic bag)
3. Use a dull putty knife to separate the hardened gum from the car seat fabric, keeping the blade flat. (Time: 4 minute(s)) (Tools: Dull putty knife)

[Task B:] 
To Clean Frost Off Car Windows Quickly
[Instructions B:]
1. Turn on the car and crank up the heat as high as possible. (Time: 1 minute(s)) (Tools: None)
2. Scrape the frost off the windows using a window scraper or a plastic credit card. (Time: 4 minute(s)) (Tools: Dull putty knife)
3. Spray windshield wiper fluid and turn the wipers on to help dislodge the ice. (Time: 0.5 minute(s)) (Tools: None)
4. Wipe, spray, and scrape the frost off the windows until it's all gone. (Time: 6 minute(s)) (Tools: Dull putty knife)

Now there are the following tools, the number of which is in brackets: Ice (1), Sealed plastic bag (1), Dull putty knife (1)
And unlimited materials, such as: Ice cubes, Windshield wiper fluid

Your response:
A.1 (start at 0, end at 1) Ice, Sealed plastic bag  
B.1 (start at 0, end at 1) None  
B.2 (start at 1, end at 5) Dull putty knife  
A.2 (start at 1, end at 6) Ice, Sealed plastic bag  
B.3 (start at 5, end at 5.5) None  
A.3 (start at 11.5, end at 15.5) Dull putty knife  
B.4 (start at 5.5, end at 11.5) Dull putty knife  
[Total time: 15.5 minutes]\n\n
'''
    cnt = 0
    for key, value in paired.items():
        # if cnt > 10:
        #     break
        cnt += 1
        for v_key, v_value in value.items():
            if (key + '+' + v_key) in save:
                continue
            tool_list = []
            tool_dic = {}
            key_question = key.split('_')[0]
            key_question_idx = key.split('_')[1]
            key_time = times[key_question][key_question_idx]
            key_instruction = instructions[key_question][key_question_idx]
            key_answer = ''
            tmp_cnt = 0
            for tmp_key, tmp_value in v_value[0].items():
                key_answer += key_instruction[tmp_cnt]
                key_answer += f' (Time: {key_time[tmp_cnt]} minute(s)) (Tools: '
                # key_answer += f' (Time: {key_time[tmp_cnt]} minute(s))\n'
                for x in tmp_value.split(','):
                    key_answer += x.strip(' ') + ', '
                    if (x.strip(' ') not in tool_list) and (x.strip(' ') != 'None'):
                        tool_list.append(x.strip(' '))
                        tool_dic[x.strip(' ')] = 1
                    elif (x.strip(' ') != 'None'):
                        tool_dic[x.strip(' ')] += 1
                key_answer = key_answer.strip(' ').strip(',')
                key_answer += ')\n'
                tmp_cnt += 1

            pair_question = v_key.split('_')[0]
            pair_question_idx = v_key.split('_')[1]
            pair_time = times[pair_question][pair_question_idx]
            pair_instruction = instructions[pair_question][pair_question_idx]
            pair_answer = ''
            tmp_cnt = 0
            tmp_tool_list = tool_list
            removed_tool = ''
            for tmp_key, tmp_value in v_value[1].items():
                pair_answer += pair_instruction[tmp_cnt]
                pair_answer += f' (Time: {pair_time[tmp_cnt]} minute(s)) (Tools: '
                # pair_answer += f' (Time: {pair_time[tmp_cnt]} minute(s))\n'
                for x in tmp_value.split(','):
                    if x.strip(' ') in tmp_tool_list:
                        removed_tool = x.strip(' ')
                    pair_answer += x.strip(' ') + ', '
                    if (x.strip(' ') not in tool_list) and (x.strip(' ') != 'None'):
                        tool_list.append(x.strip(' '))
                        tool_dic[x.strip(' ')] = 1
                    elif (x.strip(' ') != 'None'):
                        tool_dic[x.strip(' ')] += 1
                pair_answer = pair_answer.strip(' ').strip(',')
                pair_answer += ')\n'
                tmp_cnt += 1

            tool_string = ''
            # try:
            #     tool_list.remove(removed_tool)
            # except:
            #     tool_list.remove(tool_list[0])
            # if tool_list == None:
            #     tool_string += 'None'
            # else:
            for tmp_tool in tool_list:
                # tool_string += tmp_tool + f' ({tool_dic[tmp_tool]})' + ', '
                tool_string += tmp_tool + f' (1)' + ', '
            tool_string = tool_string.strip(' ').strip(',')

            material_list = []
            for x in tools[key_question][key_question_idx]['Materials'].split(','):
                if x.strip(' ') not in material_list:
                    material_list.append(x.strip(' '))
            for x in tools[pair_question][pair_question_idx]['Materials'].split(','):
                if x.strip(' ') not in material_list:
                    material_list.append(x.strip(' '))
            material_string = ''
            for tmp_material in material_list:
                material_string += tmp_material + ', '
            tool_string = tool_string.strip(' ').strip(',')

            prompt = get_prompt3(key_question[4:], key_answer, pair_question[4:], pair_answer, tool_string, material_string, example)
            # print(prompt)
            # print('running!')
            # result = run_llm(prompt)
            # print(result)
            save[key + '+' + v_key] = prompt
        with open('../data/tmp/cars_prompt_1shot.json', 'w') as f:
            json.dump(save, f, indent=4)


def schedule_jssp_analyse():
    with open('../data/filtered_instructions/Wikihow_filtered_instructions.json', 'r') as f:
        instructions = json.load(f)

    with open('../data/time_step/Wikihow_time_GT10.json', 'r') as f:
        times = json.load(f)

    with open('../data/match_tools/pair_tools_cars.json', 'r') as f:
        paired = json.load(f)

    with open('../data/match_tools/tools_analyse_parse.json', 'r') as f:
        tools = json.load(f)

    with open('../data/schedule_results/GPT4o_jssp_cars.json', 'r') as f:
        save = json.load(f)

    # save = {}
    cnt = 0
    for key, value in paired.items():
        # if cnt > 10:
        #     break
        cnt += 1
        for v_key, v_value in value.items():
            if (key + '+' + v_key) in save:
                continue
            tool_list = []
            key_question = key.split('_')[0]
            key_question_idx = key.split('_')[1]
            key_time = times[key_question][key_question_idx]
            key_instruction = instructions[key_question][key_question_idx]
            tmp_cnt = 0
            for tmp_key, tmp_value in v_value[0].items():
                for x in tmp_value.split(','):
                    if (x.strip(' ') not in tool_list) and (x.strip(' ') != 'None'):
                        tool_list.append(x.strip(' '))

            pair_question = v_key.split('_')[0]
            pair_question_idx = v_key.split('_')[1]
            pair_time = times[pair_question][pair_question_idx]
            pair_instruction = instructions[pair_question][pair_question_idx]
            tmp_cnt = 0
            for tmp_key, tmp_value in v_value[1].items():
                for x in tmp_value.split(','):
                    if (x.strip(' ') not in tool_list) and (x.strip(' ') != 'None'):
                        tool_list.append(x.strip(' '))

            tool_dic = {}
            for tmp_tool in tool_list:
                tool_dic[tmp_tool] = tool_list.index(tmp_tool)

            key_instruction = ''
            tmp_cnt = 0
            for tmp_key, tmp_value in v_value[0].items():
                key_instruction += f'Operation {tmp_cnt} on'
                for x in tmp_value.split(','):
                    if x.strip(' ') == 'None':
                        key_instruction = key_instruction.strip('on')
                        key_instruction = key_instruction.strip(' ')
                        key_instruction += ','
                        continue
                    tmp_tool = tool_dic[x.strip(' ')]
                    key_instruction += f' machine {tmp_tool},'
                key_instruction += f' duration {key_time[tmp_cnt]} minute(s).\n'
                tmp_cnt += 1

            pair_instruction = ''
            tmp_cnt = 0
            for tmp_key, tmp_value in v_value[1].items():
                pair_instruction += f'Operation {tmp_cnt} on'
                for x in tmp_value.split(','):
                    if x.strip(' ') == 'None':
                        pair_instruction = pair_instruction.strip('on')
                        pair_instruction = pair_instruction.strip(' ')
                        pair_instruction += ','
                        continue
                    tmp_tool = tool_dic[x.strip(' ')]
                    pair_instruction += f' machine {tmp_tool},'
                pair_instruction += f' duration {pair_time[tmp_cnt]} minute(s).\n'
                tmp_cnt += 1

            prompt = jssp_prompt(key_instruction, pair_instruction, len(tool_list))
            # print(prompt)
            result = run_llm(prompt)
            print(result)
            save[key + '+' + v_key] = result
        with open('../data/schedule_results/GPT4o_jssp_cars.json', 'w') as f:
            json.dump(save, f, indent=4)


def schedule_graph_analyse():
    with open('../data/filtered_instructions/Wikihow_filtered_instructions.json', 'r') as f:
        instructions = json.load(f)

    with open('../data/time_step/Wikihow_time_GT10.json', 'r') as f:
        times = json.load(f)

    with open('../data/match_tools/pair_tools_cars.json', 'r') as f:
        paired = json.load(f)

    with open('../data/match_tools/tools_analyse_parse.json', 'r') as f:
        tools = json.load(f)

    with open('../data/schedule_results/GPT4o_graph_cars.json', 'r') as f:
        save = json.load(f)

    # save = {}
    cnt = 0
    for key, value in paired.items():
        # if cnt > 10:
        #     break
        cnt += 1
        for v_key, v_value in value.items():
            if (key + '+' + v_key) in save:
                continue
            graph_json = {'task1': {}, 'task2': {}}
            key_question = key.split('_')[0]
            key_question_idx = key.split('_')[1]
            key_time = times[key_question][key_question_idx]
            key_instruction = instructions[key_question][key_question_idx]
            tmp_cnt = 0
            tmp_list = []
            for tmp_key, tmp_value in v_value[0].items():
                if tmp_cnt == (len(v_value[0]) - 1):
                    tmp_dic = {}
                    graph_json['task1']['final_step'] = key_instruction[tmp_cnt]
                    tmp_dic['source_step'] = key_instruction[tmp_cnt]
                    tmp_dic['target_step'] = key_instruction[tmp_cnt]
                    tmp_dic['time'] = key_time[tmp_cnt]
                    tmp_tool_list = []
                    for x in tmp_value.split(','):
                        tmp_tool_list.append(x.strip(' '))
                    tmp_dic['tools'] = tmp_tool_list
                    tmp_list.append(tmp_dic)
                    break
                if tmp_cnt == 0:
                    graph_json['task1']['initial_source_step'] = key_instruction[tmp_cnt]
                tmp_dic = {}
                tmp_dic['source_step'] = key_instruction[tmp_cnt]
                tmp_dic['target_step'] = key_instruction[tmp_cnt + 1]
                tmp_dic['time'] = key_time[tmp_cnt]
                tmp_tool_list = []
                for x in tmp_value.split(','):
                    tmp_tool_list.append(x.strip(' '))
                tmp_dic['tools'] = tmp_tool_list
                tmp_cnt += 1
                tmp_list.append(tmp_dic)
            graph_json['task1']['steps'] = tmp_list

            pair_question = v_key.split('_')[0]
            pair_question_idx = v_key.split('_')[1]
            pair_time = times[pair_question][pair_question_idx]
            pair_instruction = instructions[pair_question][pair_question_idx]
            tmp_cnt = 0
            tmp_list = []
            for tmp_key, tmp_value in v_value[1].items():
                if tmp_cnt == (len(v_value[1]) - 1):
                    tmp_dic = {}
                    graph_json['task2']['final_step'] = pair_instruction[tmp_cnt]
                    tmp_dic['source_step'] = pair_instruction[tmp_cnt]
                    tmp_dic['target_step'] = pair_instruction[tmp_cnt]
                    tmp_dic['time'] = pair_time[tmp_cnt]
                    tmp_tool_list = []
                    for x in tmp_value.split(','):
                        tmp_tool_list.append(x.strip(' '))
                    tmp_dic['tools'] = tmp_tool_list
                    tmp_list.append(tmp_dic)
                    break
                if tmp_cnt == 0:
                    graph_json['task2']['initial_source_step'] = pair_instruction[tmp_cnt]
                tmp_dic = {}
                tmp_dic['source_step'] = pair_instruction[tmp_cnt]
                tmp_dic['target_step'] = pair_instruction[tmp_cnt + 1]
                tmp_dic['time'] = pair_time[tmp_cnt]
                tmp_tool_list = []
                for x in tmp_value.split(','):
                    tmp_tool_list.append(x.strip(' '))
                tmp_dic['tools'] = tmp_tool_list
                tmp_cnt += 1
                tmp_list.append(tmp_dic)
            graph_json['task2']['steps'] = tmp_list

            prompt = graph_prompt(json.dumps(graph_json, indent=4))
            # print(prompt)
            result = run_llm(prompt)
            print(result)
            save[key + '+' + v_key] = result
        with open('../data/schedule_results/GPT4o_graph_cars.json', 'w') as f:
            json.dump(save, f, indent=4)


schedule_analyse()
# with open('../data/schedule_results/Zhipuz1_cars.json', 'r') as f:
#     result = json.load(f)
#
# save = {}
# for key, value in result.items():
#     flag = 0
#     if value == 'FAIL':
#         save[key] = 'FAIL'
#         continue
#     for x in value.split('\n'):
#         if '[Total time:' in x:
#             flag = 1
#             match = re.search(r'\d+', x)
#             if match:
#                 number = match.group()
#                 save[key] = number
#                 # print(number)
#             else:
#                 print(key)
#     if flag == 0:
#         print(key)
# #
# with open('../data/schedule_results/Zhipuz1_cars_result.json', 'w') as f:
#     json.dump(save, f, indent=4)
#
# with open('../data/schedule_results/Zhipuz1_cars_result.json', 'r') as f:
#     results = json.load(f)
#
# with open('../data/schedule_results/R1_cars.json', 'r') as f:
#     result = json.load(f)
#
# with open('../data/schedule_results/Schedule_grd_cars.json', 'r') as f:
#     grd = json.load(f)
#
# ground_truth = {}
# for x in grd['Conflict']:
#     for key, value in x.items():
#         ground_truth[key] = value['makespan'] / 100
# for x in grd['Parallel']:
#     for key, value in x.items():
#         ground_truth[key] = value['makespan'] / 100
#
# cnt_correct = 0
# cnt_wrong = 0
# cnt_fail = 0
# for key, value in results.items():
#     if value == 'FAIL':
#         cnt_fail += 1
#         continue
#     if int(value) == ground_truth[key]:
#         cnt_correct += 1
#     elif int(value) > ground_truth[key]:
#         print(key)
#         cnt_wrong += 1
# print(cnt_fail, cnt_correct, cnt_wrong)
# print(result['How To Repair Car Paint Chips_1+How To Powder Coat_0'][0])
with open('../data/schedule_results/Zhipuz1_cars.json', 'r') as f:
    result = json.load(f)
with open('../data/critic/Zhipuz1_cars_GPT4o_critic.json', 'r') as f:
    critics = json.load(f)

prompt = '''Please analyze the following heuristic reasoning, extract the correct plan that meets the tool conflict, and provide the conflict design and tool verification of these plans.
Note that you do not need to solve the problem directly.

For example:
A.1 and B.1, B.2 conflict in tool x
Plan 1
Correct plan: start A.1 first, then B.1, B.2
Tool verification: tool x continues to execute B.1, B.2 after A.1 is completed
...

'''
rules = '\nNow given the reasoning content:\n\nYour response:'
save_list1 = []
save_list2 = []
cnt = 0
for key, value in result.items():
    if value == 'FAILED':
        continue
    tmp_dic = {}
    tmp_dic['instruction'] = prompt + value[0] + rules
    tmp_dic['input'] = ''
    tmp_dic['rejected'] = critics[key]
    tmp_dic['chosen'] = value[1]
    if cnt > 300:
        save_list1.append(tmp_dic)
    else:
        save_list2.append(tmp_dic)
    cnt += 1
    # tmp_result = run_llm()
    # save[key] = tmp_result
with open('../data/tmp/DPO_critic_dataset_cars_test.json', 'w') as f:
    json.dump(save_list1, f, indent=4)

with open('../data/tmp/DPO_critic_dataset_cars_train.json', 'w') as f:
    json.dump(save_list2, f, indent=4)
# with open('../data/tmp/SFT_critic_dataset_cars_test.jsonl', 'w', encoding='utf-8') as file:
#     for data in save_list1:
#         json.dump(data, file, ensure_ascii=False)
#         file.write('\n')
# with open('../data/tmp/SFT_critic_dataset_cars_train.jsonl', 'w', encoding='utf-8') as file:
#     for data in save_list2:
#         json.dump(data, file, ensure_ascii=False)
#         file.write('\n')