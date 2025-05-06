import hashlib
import time
from glob import glob
from tqdm import tqdm
from zhipuai import ZhipuAI
import pandas as pd
from tqdm import tqdm
import json
import re

client = ZhipuAI(api_key="eb0109b67e804079afbb341d52817924.3ukrbKqXRe2yDHAU")  # 填写您自己的APIKey


# 875, 1734, 2582, 3424

def get_prompt(question, answer):
    Prompt = f'''You are an expert in wikiHow's categorization system. Your task is to determine which of wikiHow's 19 main categories a question best fits. Use your deep understanding of these categories to make an informed decision.

Choose one category from the list below:
1. Health: Articles related to physical and mental health, personal hygiene, medical conditions, and wellness.
2. Home and Garden: Covers topics like home maintenance, cleaning, interior decorating, and gardening.
3. Personal Care and Style: Focuses on skincare, makeup, hairstyling, personal grooming, and dressing tips.
4. Hobbies and Crafts: Encompasses creative activities, crafting, hands-on projects, and building things.
5. Food and Entertaining: Includes cooking recipes, food preparation, hosting gatherings, and etiquette.
6. Relationships: Involves romantic relationships, friendships, family dynamics, and interpersonal communication.
7. Computers and Electronics: Covers using computers, mobile devices, software, and solving tech-related issues.
8. Education and Communication: Topics related to studying, learning techniques, teaching, and effective communication.
9. Youth: Tailored for teenage audiences with content about school life, self-image, peer relationships, and personal growth.
10. Pets and Animals: Involves pet care, animal behavior, training, and general animal knowledge.
11. Arts and Entertainment: Covers music, film, television, games, and other forms of artistic or leisure expression.
12. Sports and Fitness: Topics include exercise routines, sports techniques, physical fitness, and staying active.
13. Family Life: Focuses on parenting, child development, household dynamics, and family bonding.
14. Finance and Business: Articles related to entrepreneurship, managing money, budgeting, and financial planning.
15. Work World: Involves career advice, job searching, workplace skills, and professional development.
16. Cars and Other Vehicles: Covers car maintenance, driving, buying vehicles, and transportation tips.
17. Philosophy and Religion: Encompasses belief systems, religious practices, ethics, and philosophical questions.
18. Travel: Topics about planning trips, travel hacks, cultural awareness, and navigating new places.
19. Holidays and Traditions: Focuses on celebrating holidays, cultural customs, and seasonal events.


Output format:
Category: [Chosen category name]

Given a question and its answer below. Please respond without any other explanation or irrelevant information.
[Procedural Question:]
{question}
[Instructional Answer:]
{answer}

Your response:
    '''
    return Prompt


def get_response(prompt):
    response = client.chat.asyncCompletions.create(
        model="GLM-Z1-Flash",
        messages=[
            {"role": "user", "content": prompt}
        ],
        top_p=0.2,
        temperature=0.1
    )
    return response


def submit(prompt_list):
    res_list = []
    tmp_dic = {}
    for prompts in prompt_list:
        try:
            res = get_response(prompts[0])
            res_list.append([res, prompts[1]])
        except:
            tmp_dic[prompts[1]] = 'Danger'
            print('Danger')
            continue

    for one_res_list in res_list:
        one_res = one_res_list[0]
        task_id = one_res.id
        task_status = ''
        get_cnt = 0
        danger_flag = 0
        while task_status != 'SUCCESS' and task_status != 'FAILED' and get_cnt <= 40:
            try:
                result_response = client.chat.asyncCompletions.retrieve_completion_result(id=task_id)
            except:
                print('Danger!')
                danger_flag = 1
                break
            print(result_response.task_status)
            task_status = result_response.task_status
            time.sleep(2)
            get_cnt += 1
        if danger_flag == 1:
            tmp_dic[one_res_list[1]] = 'Danger'
            continue
        try:
            tmp_dic[one_res_list[1]] = [result_response.choices[0].message.content.split('</think>')[0], result_response.choices[0].message.content.split('</think>')[1]]
        except:
            tmp_dic[one_res_list[1]] = 'FAILED'
    return tmp_dic


def run():
    # with open('../data/time_step/Wikihow_time_GT10.json', 'r') as f:
    #     times = json.load(f)

    # with open('../data/filtered_instructions/Wikihow_filtered_instructions.json', 'r') as f:
    #     instructions = json.load(f)

    with open('../data/schedule_results/Zhipuz1_cars.json', 'r') as f:
        save = json.load(f)

    with open('../data/tmp/cars_prompt.json', 'r') as f:
        prompts = json.load(f)

    prompt_list = []
    cnt = 0
    all_cnt = 0
    print(len(save))
    # save = {}
    for key, value in prompts.items():
        # if all_cnt < 400:
        #     all_cnt += 1
        #     continue
        if key in save:
            continue
        # if all_cnt > 399:
        #     break
        # all_cnt += 1
        # for v_key, v_value in value.items():
        #     instruction_list = instructions[key][v_key]
        #     break
        # prompt = get_prompt(key, '\n'.join(instruction_list))
        prompt_list.append([value, key])
        cnt += 1
        if cnt > 19:
            tmp_dic = submit(prompt_list)
            for tmp_key, tmp_value in tmp_dic.items():
                save[tmp_key] = tmp_value
            cnt = 0
            prompt_list = []
        with open('../data/schedule_results/Zhipuz1_cars.json', 'w') as f:
            json.dump(save, f, indent=4)
    tmp_dic = submit(prompt_list)
    for tmp_key, tmp_value in tmp_dic.items():
        save[tmp_key] = tmp_value
    with open('../data/schedule_results/Zhipuz1_cars.json', 'w') as f:
        json.dump(save, f, indent=4)


run()