import os
import requests
import json
from anthropic import Anthropic

client = Anthropic()

def load_agent(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)
    
# Open AI API request
def anthropic_api_request(model=None,
                       messages=None,
                       system=None,
                       temperature=1,
                       top_p=1,
                       max_tokens=300):  # Add max_completion_tokens parameter
    
    url = "https://api.anthropic.com/v1/messages"
    api_key = os.getenv("ANTHROPIC_API_KEY")

    headers = {
       "Content-Type": "application/json; charset=utf-8",
       "x-api-key": f"{api_key}", 
       "anthropic-version": "2023-06-01"  
   }

    data = {
        "model": model,
        "system": system,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens 
    }

    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    
    # Extract token usage
    token_usage = response_json.get('usage', {})
    input_tokens = token_usage.get('input_tokens', 0)
    output_tokens = token_usage.get('output_tokens', 0)

    return response_json, input_tokens, output_tokens


class API_Call_anthropic():
    
    def __init__(self, agent=None):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if agent is None:
            self.agent_data = load_agent("agents/default_anthropic.json")
        else:
            self.agent_data = load_agent(f"agents/{agent}.json")
        
    def update_agent(self, filename):
        self.agent_data = load_agent(filename)
   
    def thinkAbout(self, message, conversation, model=None):
        if not conversation:
            conversation = []  # I have to initialise this first message to stop logprobs retrieval from sending an error.
        if model is None:
           model = self.agent_data.get("model", "claude-3-5-sonnet-20241022")
        pre_prompt = self.agent_data.get("PrePrompt", "")
        conversation.append({"role": "user", "content": [{"type": "text", "text": message}]})

        try:
            response, input_tokens, output_tokens = anthropic_api_request(
                model=model,
                system=pre_prompt,
                messages=conversation,
                temperature=self.agent_data.get("temperature", 1),
                top_p=self.agent_data.get("top_p", 1),
                max_tokens=300
            )
            logprobs_list = response.get('logprobs', [])
            conversation.append({"role": "assistant", "content": response['content'][0]['text']})
        except Exception as e:
            conversation.append({"role": "assistant", "content": "Error: Unable to retrieve information."})
            return conversation, 0, 0, 0

        prompt_tokens = input_tokens
        completion_tokens = output_tokens
        total_tokens = prompt_tokens + completion_tokens

        return conversation, prompt_tokens, completion_tokens, total_tokens, logprobs_list
