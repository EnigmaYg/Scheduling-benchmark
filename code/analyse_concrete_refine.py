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
    PROMPT = f'''You are an expert in solving procedural non-factual problems. Your task is to determine whether a procedural problem is concrete.

A procedural problem is concrete if it meets the following criterion:
1. The task requires the use of a specific physical tool, device, or material other than the human body.
2. The tool should be clearly identifiable and essential to completing the task.
3. If a task can be completed entirely through human actions without external tools, it is not concrete.

For example:
Example 1
Concrete Task: "How To Tune a Bass Guitar with a Tuner"
Requires a tuner as a specific tool. The tuner provides objective feedback that guides the process. Therefore, this task is concrete.

Non-Concrete Task: "How To Tune a Bass Guitar by Ear"
No external tool is required; the process relies only on human perception. The evaluation criteria are subjective. Therefore, this task is not concrete.

Example 2
Concrete Task: "How To Relieve a Thigh Cramp Using a Massage Gun"
Requires a massage gun as a specific tool. The device applies mechanical force that is essential to the process. Therefore, this task is concrete.
Non-Concrete Task: "How To Relieve a Thigh Cramp by Stretching"
No external tool is used; only human movement is involved. The success criteria depend on internal perception (whether the cramp feels better). Therefore, this task is not concrete.

For each procedural question, determine whether it is concrete based on tool dependency.
You only need to answer "Yes" or "No", without any additional explanation.

Given the question and its answer:
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

    # data = []
    # with open('WikiHowNFQA.jsonl', 'r', encoding='utf-8') as f:
    #     for line in f:
    #         data.append(json.loads(line))
    with open('WikiHow_procedural_concrete_question.json', 'r') as f:
        procedural_QA = json.load(f)

    with open('WikiHow_id2question.json', 'r') as f:
        id2question = json.load(f)

    save = {}
    cnt = 0

    for key, value in procedural_QA.items():
        cnt += 1
        if cnt < 4300:
            continue
        question = id2question[key]
        prompt_ = get_prompt(question, value)
        messages = format_prompt(prompt_, tokenizer)
        outputs = model.generate(messages, sampling_params)
        response = outputs[0].outputs[0].text
        save[key] = response
        with open('WikiHow_Concrete_refine2.json', 'w') as f:
            json.dump(save, f, indent=4)