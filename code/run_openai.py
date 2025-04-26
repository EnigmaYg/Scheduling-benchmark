import json
import os
from openai import OpenAI

client = OpenAI(
    api_key="sk-rh8wi5OXclyhFu7spfK69E7UHU5BkOdIqRsl0xslPiFRgQg3",
    base_url="https://api.key77qiqi.cn/v1"
)


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


def get_prompt3(question1, answer1, question2, answer2, tools, materials):
    Prompt = f'''You are an expert in solving procedural problems. I now have two procedural problems and give the steps to solve them and the time and tools required for each step. However, I only have valid tools, but unlimited materials. I need you to plan whether it is possible to complete these two tasks at the same time based on these valid tools, and give the best method.
[Question A:] 
{question1}
[Answer A:]
{answer1}

[Question B:] 
{question2}
 [Answer B:]
{answer2}


Now there are the following tools, the number of which is in brackets: {tools}
And unlimited materials, such as: {materials}
Please analyze whether you can complete this task and give the most efficient operation plan. If you can complete it, please output the results in the order of steps, indicating which step of the problem it is, and the tools used. Finally, calculate the total time to complete all tasks. The shortest time is required, that is, the most efficient operation. Please follow the following format:
A.1 (start at minutes x, end at minutes x) Tool X 
B.1 (start at minutes x, end at minutes x) Tool X 
A.1 (start at minutes x, end at minutes x) Tool X 

If it cannot be completed, directly output FAIL

Please respond without any other explanation or irrelevant information.
Your response:

'''
    return Prompt


def run_llm(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return completion.choices[0].message.content


def tool_analyse():
    with open('../data/match_tools/Pets_and_Animals_pair.json', 'r') as f:
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
        question1 = key.split('_')[0]
        idx = key.split('_')[1]
        instruction_answer = instructions[question1][idx]
        time_list = times[question1][idx]
        tmp_tool_dic = tools[key]['Tool_steps']
        answer1 = ''
        for instruction in instruction_answer:
            answer1 += instruction + '(Time: '
            answer1 += str(time_list[instruction_answer.index(instruction)]) + ' minutes) '
            answer1 += '(Tools: ' + str(tmp_tool_dic[str(instruction_answer.index(instruction) + 1)]) + ')\n'
        materials = tools[key]['Materials']
        tool_dic = tools[key]['Tools']

        tmp_dic = {}
        for pair_question in value:
            question2 = pair_question.split('_')[0]
            idx2 = pair_question.split('_')[1]
            instruction_answer = instructions[question2][idx2]
            time_list = times[question2][idx2]
            tmp_tool_dic = other_tools[pair_question]['Tool_steps']
            answer2 = ''
            for instruction in instruction_answer:
                answer2 += instruction + '(Time: '
                answer2 += str(time_list[instruction_answer.index(instruction)]) + ' minutes)'
                answer2 += '(Tools: ' + str(tmp_tool_dic[str(instruction_answer.index(instruction) + 1)]) + ')\n'
            materials += other_tools[pair_question]['Materials']
            materials = materials[:-2]
            for tool_key, tool_value in other_tools[pair_question]['Tools'].items():
                if tool_key in tool_dic:
                    tool_dic[tool_key] = max(tool_dic[tool_key], tool_value)
                else:
                    tool_dic[tool_key] = tool_value
            tools_string = ''
            for tool_key, tool_value in tool_dic.items():
                tools_string += tool_key + f'({tool_value}), '
            prompt = get_prompt3(question1, answer1, question2, answer2, tools_string, materials)
            print(prompt)
            # response = run_llm(prompt)
            # print(response)
            # tmp_dic[pair_question] = response
        save[key] = tmp_dic
        with open('../data/tmp/GPT4o_sample_results_with_tools.json', 'w') as f:
            json.dump(save, f, indent=4)

tool_analyse()