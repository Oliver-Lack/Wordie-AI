import os
import requests
import json

def load_agent(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

# XAI Grok API request
def grok_api_request(model="grok-2-latest",
                     messages=None,
                     temperature=1): 
                     
    url = "https://api.x.ai/v1/chat/completions"
    api_key = os.getenv("XAI_API_KEY")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }

    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    
    # Extract token usage information
    token_usage = response_json.get('usage', {})
    prompt_tokens = token_usage.get('prompt_tokens', 0)
    completion_tokens = token_usage.get('completion_tokens', 0)
    total_tokens = token_usage.get('total_tokens', 0)

    return response_json, prompt_tokens, completion_tokens, total_tokens

class GrokAPI_Call():

    def __init__(self, agent=None):
        if agent is None:
            self.agent_data = load_agent("agents/default.json")
        else:
            self.agent_data = load_agent(f"agents/{agent}.json")
        
    def update_agent(self, filename):
        self.agent_data = load_agent(filename)
   
    def thinkAbout(self, message, conversation, model=None, debug=False):
        model = self.agent_data.get("model", "grok-2-latest")
        
        # Ensure system message exists
        if not any(msg["role"] == "system" for msg in conversation):
           system_prompt = self.agent_data.get("PrePrompt", "")
           conversation.insert(0, {"role": "system", "content": system_prompt})

        FormattedMessage = {"role": "user", "content": message}
        conversation.append(FormattedMessage)

        try:
            response, prompt_tokens, completion_tokens, total_tokens = grok_api_request(
                model=model,
                messages=conversation,
                temperature=self.agent_data["temperature"]
            )
        except:
            response = {'choices': [{'message': {'content': "An error occurred during the API call"}}], 'usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}}
            prompt_tokens, completion_tokens, total_tokens = 0, 0, 0

        if "error" in response.keys():
            conversation.append({"role": "assistant", "content": response["error"]["message"]})
            return conversation, 0, 0, 0

        conversation.append({"role": "assistant", "content": response['choices'][0]['message']['content']})

        if debug:
            with open("logs.txt", "w", encoding="utf-8") as file:
                for i in conversation:
                    file.write(str(i) + "\n")

        return conversation, prompt_tokens, completion_tokens, total_tokens