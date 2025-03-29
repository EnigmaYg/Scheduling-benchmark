
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
    PROMPT = f'''You are an expert in solving procedural non-factual problems. Your task is to determine whether a procedural problem is concrete. You need to comprehensively analyze whether a procedural problem is concrete from the following perspectives:
(1)Entity Operability:
Does the task involve clear objects, tools, or materials?
Are there necessary physical steps and definable state changes?
(2)Divisibility of Steps:
Can the task be divided into independent, parallel, or interdependent subtasks?
(3)Objectivity of Evaluation Criteria:
Does the task have clear, measurable success criteria?

For example:
Problem 1: How To Raise Gardenias in Pots
Answer:
Choose a pot at least 4 inches taller than the original container.
Fill it with well-draining soil, such as one containing peat moss or sand.
Place the plant where it gets at least 6 hours of indirect sunlight daily.
Water once or twice a week when the soil is dry below the surface.

Problem 2: How To Prevent Fainting
Answer:
Eat a salty or sugary snack and drink water or juice.
Cool yourself down by removing excess layers or splashing water on your face.
Lie down, breathe deeply, and relax until you feel better.
Avoid triggers such as alcohol, medications, or phobias.

For these two problems, Problem 1 is concrete while Problem 2 is not.

Problem  1 involves physical objects (flower pot, soil, water). Problem  1 has clear steps (choosing a pot, filling with soil, planting, watering). Success is measurable (plant growth, survival rate).

Problem 2 involves abstract concepts (hydration, avoiding triggers). Steps are not clearly dependent on each other. Success is difficult to measure (unclear how well one "prevents" fainting).

Based on the above prompt, please judge whether the following problem is concrete.
You only need to answer yes or no, with no additional explanation or analysis.

The following are the problem and answer:

[Problem:]
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


    # data = []
    # with open('WikiHowNFQA.jsonl', 'r', encoding='utf-8') as f:
    #     for line in f:
    #         data.append(json.loads(line))
    with open('WikiHow_ProceduralQ.json', 'r') as f:
        NFQ = json.load(f)

    save = {}
    cnt = 0
    for item in data:
        cnt += 1
        if cnt < 7220:
            continue
        prompt_ = get_prompt(item['question'], item['answer'])
        messages = format_prompt(prompt_, tokenizer)
        outputs = model.generate(messages, sampling_params)
        response = outputs[0].outputs[0].text
        save[item['question']] = response
        with open('WikiHow_ProceduralQ2.json', 'w') as f:
            json.dump(save, f, indent=4)