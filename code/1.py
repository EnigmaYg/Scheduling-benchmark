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


def run_llm(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o",
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

with open('../data/tmp/cars_prompt_1shot.json', 'r') as f:
    prompt_shot = json.load(f)

with open('../data/tmp/cars_removed_prompt.json', 'r') as f:
    removed_prompt = json.load(f)

with open('../data/tmp/cars_removed_prompt_1shot.json', 'r') as f:
    removed_prompt_shot = json.load(f)

with open('../data/tmp/cars_no_constraint_prompt.json', 'r') as f:
    constraint_prompt = json.load(f)

with open('../data/tmp/cars_no_constraint_prompt_1shot.json', 'r') as f:
    constraint_prompt_shot = json.load(f)

# cnt = 0
# save = {}
# for key, value in prompt_shot.items():
#     print(cnt)
#     cnt += 1
#     if cnt > 100:
#         break
#     if key in save:
#         continue
#     result = run_llm(value)
#     save[key] = result
#     with open('../data/schedule_results/GPT4o_cars_1shot.json', 'w') as f:
#         json.dump(save, f, indent=4)

# cnt = 0
# save = {}
# for key, value in removed_prompt.items():
#     print(cnt)
#     cnt += 1
#     if cnt > 100:
#         break
#     result = run_llm(value)
#     save[key] = result
#     with open('../data/schedule_results/GPT4o_cars_removed.json', 'w') as f:
#         json.dump(save, f, indent=4)
#
# cnt = 0
# save = {}
# for key, value in removed_prompt_shot.items():
#     print(cnt)
#     cnt += 1
#     if cnt > 100:
#         break
#     result = run_llm(value)
#     save[key] = result
#     with open('../data/schedule_results/GPT4o_cars_removed_1shot.json', 'w') as f:
#         json.dump(save, f, indent=4)
#
# cnt = 0
# save = {}
# for key, value in constraint_prompt.items():
#     print(cnt)
#     cnt += 1
#     if cnt > 100:
#         break
#     result = run_llm(value)
#     save[key] = result
#     with open('../data/schedule_results/GPT4o_cars_constraint.json', 'w') as f:
#         json.dump(save, f, indent=4)
#
cnt = 0
save = {}
for key, value in constraint_prompt_shot.items():
    print(cnt)
    cnt += 1
    if cnt > 100:
        break
    result = run_llm(value)
    save[key] = result
    with open('../data/schedule_results/GPT4o_cars_constraint_1shot.json', 'w') as f:
        json.dump(save, f, indent=4)