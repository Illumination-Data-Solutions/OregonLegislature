import subprocess
import os
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from semantic_kernel.connectors.ai.ollama.ollama_prompt_execution_settings import OllamaChatPromptExecutionSettings
from semantic_kernel.prompt_template import PromptTemplateConfig
from tqdm import tqdm
import pandas as pd

class Law_Agent:
    async def find_submission_deadlines(self, policy_list, output_path):
        # Configuration for Semantic Kernel
        kernel = Kernel()

        def add_service_to_kernel(kernel: Kernel, service_id: str, host: str, ai_model_id: str):
            kernel.add_service(
                OllamaChatCompletion(
                    service_id=service_id,
                    host=host,
                    ai_model_id=ai_model_id,
                )
            )

        def add_function_to_kernel(kernel: Kernel, function_name: str, plugin_name: str, prompt: str,
                                   execution_settings: OllamaChatPromptExecutionSettings):
            template_config = PromptTemplateConfig(template=prompt, name=function_name,
                                                   template_format="semantic-kernel")
            kernel.add_function(function_name=function_name, plugin_name=plugin_name,
                                prompt_template_config=template_config,
                                prompt_execution_settings=execution_settings)

        async def get_response(kernel: Kernel, function_name: str, plugin_name: str, message_content: str) -> str:
            function = kernel.get_function(function_name=function_name, plugin_name=plugin_name)
            result = await kernel.invoke(function=function, message_content=message_content)
            return str(result)  # Convert the FunctionResult object to a string

        async def get_submission_deadline(kernel, policy):
            prompt = f"Given a policy find deadlines and the commities due to and who is responsible for submitting them. return them in the following format 'deadline, due to, from'  if there are no deadlines return 'no deadlines'. Do not add any other text. The policy is: {policy}"
            # print(f"Prompt: {prompt}")
            # polocy number is ther first 7 characters
            add_function_to_kernel(kernel, "policy_deadlines", "policy_deadlines_plugin", prompt, OllamaChatPromptExecutionSettings())
            response = await get_response(kernel, "policy_deadlines", "policy_deadlines_plugin", prompt)
            if len(response) < 50:
                print(f"Response: {response}")
            else:
                print(f"Response: {response[:50]}...")

            print('' * 50)
            return response

        add_service_to_kernel(kernel, "ollama", "http://localhost:11434", "llama3.1")
        deadlines = []
        # for pol in policy_list:
        for pol in tqdm(policy_list, desc="Processing policies", unit="policy"):
            dl_found = False
            times = 0
            while not dl_found and times < 2:
                dl = await get_submission_deadline(kernel, pol)
                if dl == 'no deadlines':
                    dl_found = True
                if dl != 'no deadlines':
                    policy_number = pol[:7]
                    out_list = []
                    out_list.append(policy_number)
                    # append each  dl.strip().split(',') to out_list
                    for d in dl.split(','):
                        out_list.append(d.strip())

                    if len(out_list) == 4:
                        dl_found = True
                        deadlines.append(out_list)
                    else:
                        dl_found = True
            if times > 2:
                print(f"Could not find deadlines for policy: {pol[50:]}") # don't write dl out
            else: # write deadlines out
                pd.DataFrame(deadlines, columns=['policy_number', 'deadline', 'due _to', 'from']).to_csv(output_path, index=False)

        return deadlines

def write_policy_deadlines(policy_list, output_path):
    # Create agents
    law_agent = Law_Agent()
    asyncio.run(law_agent.find_submission_deadlines(policy_list, output_path))
def process_policy_deadlines(policy_list, output_path):
    # Create agents
    write_policy_deadlines(policy_list, output_path)


if __name__ == '__main__':
    pass
    # cwd = os.getcwd()
    # input_pdf = os.path.join(cwd,  'data', 'input', 'my_resume.pdf')
    # job_details_path = os.path.join(cwd, 'data', 'input', 'job_details.txt')
    # output_path = os.path.join(cwd, 'cover_letter.txt')
    #
    # process_cover_letter(input_pdf, job_details_path, output_path)