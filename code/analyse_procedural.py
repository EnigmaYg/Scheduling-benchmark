
import unicodedata
import os
import json
import torch
import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(lineno)d - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO,
)

from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import os

HF_HOME = "/pool001/spangher/huggingface_home/hub"
proj_dir = '/pool001/spangher/alex/video_scripts'
# TODO: Get myself Token
os.environ['HF_TOKEN'] = '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'
os.environ['HF_HOME'] = HF_HOME
os.environ['VLLM_WORKER_MULTIPROC_METHOD'] = 'spawn'
os.environ['VLLM_ALLOW_LONG_MAX_MODEL_LEN'] = '1'


def get_prompt(question, answer):
    PROMPT = f'''You are an expert in solving non-factual questions (NFQs). Your task is to determine whether an NFQ is a procedural question, and if so, extract its unique, concise, and non-redundant answer.

Task Instructions:
(1)Determine Procedurality:
A procedural question is one that asks for a step-by-step process to achieve a specific outcome.
If the given question is not procedural, output only: “No”
(2)Extract the Only Accurate Answer:
Remove any non-instructional content (such as explanations, reasoning, or justifications).
Eliminate redundant or alternative steps that serve the same purpose, keeping only one necessary step.
Integrate closely related steps into a single concise instruction where appropriate.
Number each step clearly, ensuring the process remains sequential and logical.

For example:
Example 1 (Non-Procedural Question):
[Question:]
How To Convince Someone to Give You Something
[Answer:]
If you need to convince someone to give you something, explain to them why you need it and act confident when you talk to them. For example, if you need to borrow gas money from your sister, honestly tell her that you overspent this month, but that you're working on improving your budgeting skills. This way, you’ll appear trustworthy, which will encourage her to help you out. Be polite with your request by using language like “May I please” and “Thank you,” which will make the other person more likely to respond positively.

Your response:
No


Example 2 (Procedural Question):
[Question:]
How To Raise Gardenias in Pots
[Answer:]
You can easily raise gardenias in pots by making sure they have a large enough container, the right soil, and the proper amount of water and sunlight. When you’re choosing a pot or container, pick one that is at least 4 inches taller than the container your gardenia came in so it has more room to grow. Fill the pot with soil that drains well such as one that includes peat moss or sand to help with drainage. Place your gardenias in a location that gets at least 6 hours of sunlight each day, but is out of direct sunlight, such as a windowsill or near a shady tree in your yard. Water your gardenias about once or twice a week, when the soil is dry below the surface.

Your response:
1. Choose a pot at least 4 inches taller than the original container.
2. Fill it with well-draining soil, such as one containing peat moss or sand.
3. Place the plant where it gets at least 6 hours of indirect sunlight daily.
4. Water once or twice a week when the soil is dry below the surface.


Example 3 (Procedural Question):
[Question:]
How To Prevent Fainting
[Answer:]
When you feel yourself starting to get faint, boost your blood salt and sugar levels by snacking on some pretzels or crackers and drinking a little juice. If you feel overheated, try to stave off fainting by taking off some layers or splashing cool water on your face. You can also drink some water, which will both cool you down and hydrate you. Additionally, you may find it helpful to lie down, breathe deeply, and relax until you feel a little better. Finally, do your best to avoid things that might trigger fainting spells, such as alcohol, certain medications, or phobias.

Your response:
1. Eat a salty or sugary snack and drink water or juice.
2. Cool yourself down by removing excess layers or splashing water on your face.
3. Lie down, breathe deeply, and relax until you feel better.
4. Avoid triggers such as alcohol, medications, or phobias.


Now, analyze the following question and answer:
[Question:]
{question}
[Answer:]
{answer}

Your response:
    '''
    return PROMPT
#
# (3) Information: Restate the informational content they provide to the article.  Be specific about the facts provided. Make sure you includ to include all the information attributable to that source. (3-4 sentences).

def format_prompt(prompt, tokenizer):
    message = [
        {
            "role": "user",
            "content": prompt,
        },
    ]
    formatted_prompt = tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
    return formatted_prompt


def load_model(model_name: str):
    torch.cuda.memory_summary(device=None, abbreviated=False)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = LLM(
        model_name,
        dtype=torch.float16,
        tensor_parallel_size=torch.cuda.device_count(),
        gpu_memory_utilization=0.95,
        download_dir=HF_HOME,  # sometimes the distributed model doesn't pay attention to the
        enforce_eager=True,
        max_model_len=30_000
    )
    return tokenizer, model

def write_to_file(fname, urls, outputs):
    with open(fname, 'wb') as file:
        for url, output in zip(urls, outputs):
            response = output.outputs[0].text
            response = unicodedata.normalize('NFKC', response)
            if response and url:
                output = {}
                output['url'] = str(url)
                output['response'] = str(response)
                file.write(json.dumps(output).encode('utf-8'))
                file.write(b'\n')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="meta-llama/Meta-Llama-3.1-70B-Instruct")
    parser.add_argument('--output_file', type=str, default='vllm_generate.txt')
    parser.add_argument('--source_data_file', type=str, default='outlines_filter.json')
    parser.add_argument('--data_dir', type=str, default=f'{proj_dir}/data')
    args = parser.parse_args()

    tokenizer, model = load_model(args.model)

    sampling_params = SamplingParams(temperature=0.1, max_tokens=2048)

    # dirname = os.path.dirname(f'{args.data_dir}/{args.output_file}')
    # if not os.path.exists(dirname):
    #     os.makedirs(dirname)

    data = []
    with open('WikiHowNFQA.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))

    save = {}
    cnt = 0
    for item in data:
        prompt_ = get_prompt(item['question'], item['answer'])
        messages = format_prompt(prompt_, tokenizer)
        outputs = model.generate(messages, sampling_params)
        response = outputs[0].outputs[0].text
        save[item['question']] = response
        with open('WikiHow_ProceduralQ.json', 'w') as f:
            json.dump(save, f, indent=4)