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


import json
from openai import OpenAI

client = OpenAI(
    api_key="sk-rh8wi5OXclyhFu7spfK69E7UHU5BkOdIqRsl0xslPiFRgQg3",
    base_url="https://api.key77qiqi.cn/v1"
)

with open('../data/match_tools/tools_analyse_parse.json', 'r') as f:
    data = json.load(f)

with open('../data/setting_setup/WikiHow_categories.json', 'r') as f:
    categories = json.load(f)

with open('../data/filtered_instructions/Wikihow_filtered_instructions.json', 'r') as f:
    instructions = json.load(f)

key_list = []
for key, value in data.items():
    try:
        if (categories[key] == 'Danger') or (categories[key] == 'FAILED'):
            key_list.append(key)
    except:
        key_list.append(key)

save = {}
for keys in key_list:
    print(keys)
    prompt = get_prompt(keys, '\n'.join(instructions[keys]))
    results = run_llm(prompt)
    save[keys] = results

with open('../data/setting_setup/WikiHow_categories1.json', 'w') as f:
    json.dump(save, f, indent=4)