import json
import os
from openai import OpenAI

client = OpenAI(
    api_key="sk-rh8wi5OXclyhFu7spfK69E7UHU5BkOdIqRsl0xslPiFRgQg3",
    base_url="https://api.key77qiqi.cn/v1"
)


def get_prompt(question, answer, step):
    steps = '\n'.join(step)
    Prompt = f'''You are a procedural task analyst. Your job is to analyze how long it takes to complete certain steps in a procedural problem. Do not give a time range, but an exact number of minutes. If this is not a stateful step (e.g., "Keep temperature constant.") or an incremental step (e.g., "Offer baby bottle before each feeding."), use common sense to reason. Otherwise, output 'None'.

For example:
[Procedural question:]
How To Make Chicken Cutlets
[Instructional answer:]
1. Slice the chicken breasts horizontally to 1/4 inch thickness.
2. Combine bread crumbs, Parmesan cheese, parsley, salt, and pepper in a bowl.
3. Beat the egg and milk together in a separate bowl.
4. Spread flour onto a plate.
5. Dredge each cutlet in flour, then the egg mixture, and then the bread crumb mixture.
6. Fry the breaded chicken cutlets.
[Specific step:]
6. Fry the breaded chicken cutlets.

Your response:
10 minutes


Below is the question and its corresponding answer, as well as the specific step to be analyzed. Please only output the time for the specific step. Do not add any other explanation or irrelevant information.
[Procedural question:]
{question}
[Instructional answer:]
{answer}
[Specific step:]
{steps}

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




with open('../data/Wikihow_time_None.json', 'r') as f:
    times = json.load(f)

with open('../data/WikiHow_filtered_data.json', 'r') as f:
    data = json.load(f)


save = {}
flag = 0
for key, value in times.items():
    # if flag == 1:
    #     break
    # if key == 'How To Make Chicken Cutlets':
    #     flag = 1
    tmp_dic = {}
    for v_key, v_value in value.items():
        if 'None' in v_value:
            v_list = v_value.split('\n')
            step_list = []
            instruction_list = data[key][v_key]
            for line in v_list:
                if 'None' in line:
                    step_list.append(instruction_list[v_list.index(line)])
            prompt = get_prompt(key, '\n'.join(data[key][v_key]), step_list)
            response = run_llm(prompt)
            tmp_dic[v_key] = response
    save[key] = tmp_dic
    with open('../data/Wikihow_time_reanalyse.json', 'w') as f:
        json.dump(save, f, indent=4)