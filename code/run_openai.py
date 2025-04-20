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
2. If a step does not require any tools, explicitly state None.
3. Prioritize reusing tools from previous steps to minimize the total number of tools required.
4. Only list the essential tools required to complete the task. Avoid mentioning unnecessary or redundant tools.
5. Finally, provide a complete list of all tools and their quantities used in all steps of the process(only one is needed if it can be reused).

For example:
[Procedural Question:]
How To Make a Volcano Erupt
[Instructional Answer:]
1. Secure a bottle of soda to a cardboard tray.
2. Spray insulating foam around the soda bottle to create a mountain.
3. Wait for the insulating foam to harden.
4. Paint the dried insulating foam to resemble a volcano.
5. Attach a paper cylinder to the top of the volcano.
6. Drop Mentos into the paper cylinder to trigger the eruption.

Your response:
[Tools:]
Step 1: Scissors
Step 2: None
Step 3: None
Step 4: Paintbrush
Step 5: Scissors
Step 6: None

[Materials:]
Step 1: Soda bottle, Cardboard tray, Tape
Step 2: Insulating foam
Step 3: None
Step 4: Acrylic paint
Step 5: Paper, Tape
Step 6: Mentos candies

[Tools list:]
Scissors: 1
Paintbrush: 1

Given a question and its answer below. Please respond without any other explanation or irrelevant information.
[Procedural Question:]
{question}
[Instructional Answer:]
{answer}

Your response:
'''
    return Prompt


def get_prompt2(question, answer, tools):
    tools = ' '.join(tools)
    Prompt = f'''You are an expert in solving procedural problems. Your task is to analyze the additional tools and materials required to solve procedural problems. For each step of the process, you need to output with the following rules: 
1. For each step, list the tools (minimum necessary tools to complete the task) and materials (expendables or consumables required for the step) separately.
2. If a step does not require any tools, explicitly state None.
3. Prioritize known tools and tools from previous steps to minimize the total number of tools required.
4. Only list the essential tools required to complete the task. Avoid mentioning unnecessary or redundant tools.
5. Finally, provide a complete list of all tools and their quantities used in all steps of the process(only one is needed if it can be reused).

For example:
[Procedural Question:]
How To Make a Volcano Erupt
[Instructional Answer:]
1. Secure a bottle of soda to a cardboard tray.
2. Spray insulating foam around the soda bottle to create a mountain.
3. Wait for the insulating foam to harden.
4. Paint the dried insulating foam to resemble a volcano.
5. Attach a paper cylinder to the top of the volcano.
6. Drop Mentos into the paper cylinder to trigger the eruption.
[Know Tools:]
None

Your response:
[Tools:]
Step 1: Scissors
Step 2: None
Step 3: None
Step 4: Paintbrush
Step 5: Scissors
Step 6: None

[Materials:]
Step 1: Soda bottle, Cardboard tray, Tape
Step 2: Insulating foam
Step 3: None
Step 4: Acrylic paint
Step 5: Paper, Tape
Step 6: Mentos candies

[Tools list:]
Scissors: 1
Paintbrush: 1

Given a question and its answer below. Please respond without any other explanation or irrelevant information.
[Procedural Question:]
{question}
[Instructional Answer:]
{answer}
[Know Tools:]
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
    with open('../data/tmp/Wikihow_sample_retrieve.json', 'r') as f:
        rt = json.load(f)

    with open('../data/filtered_instructions/Wikihow_filtered_instructions.json', 'r') as f:
        data = json.load(f)

    with open('../data/tmp/Wikihow_sample_tools_parse.json', 'r') as f:
        tools = json.load(f)


    save = {}
    flag = 0
    for key, value in rt.items():
        # if flag == 1:
        #     break
        # if key == 'How To Make Chicken Cutlets':
        #     flag = 1
        question = key.split('_')[0]
        idx = key.split('_')[1]
        tool_list = list(tools[key]["Tools"].keys())
        # answers = '\n'.join(data[question][idx])
        # prompt = get_prompt(question, answers)
        # response = run_llm(prompt)
        # print(response)
        # save[key] = response
        for v_value in value:
            question = v_value[0].split('_')[0]
            idx = v_value[0].split('_')[1]
            answers = '\n'.join(data[question][idx])
            # prompt = get_prompt(question, answers)
            prompt = get_prompt2(question, answers, tool_list)
            print(prompt)
            response = run_llm(prompt)
            save[v_value[0]] = response
        with open('../data/tmp/Wikihow_sample_tools_.json', 'w') as f:
            json.dump(save, f, indent=4)
        # with open('../data/tmp/Wikihow_time_reanalyse.json', 'w') as f:
        #     json.dump(save, f, indent=4)


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

schedule_analyse()