import os
import google.generativeai as genai
import json

def load_agent(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

# Google API request
def google_api_request(model="gemini-1.5-pro", message="", history=None):
    if history is None:
        history = []

    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    gen_model = genai.GenerativeModel(model_name=model)

    chat_session = gen_model.start_chat(history=history)
    response = chat_session.send_message(message)

    return response.text

class API_Call_Google:
    def __init__(self, agent=None):
        if agent is None:
            self.agent_data = load_agent("agents/default.json")
        else:
            self.agent_data = load_agent(f"agents/{agent}.json")

    def update_agent(self, filename):
        self.agent_data = load_agent(filename)

    def thinkAbout(self, message, conversation, model=None, debug=False):
        model = self.agent_data.get("model", "gemini-1.5-pro")
        
        if not any(msg["role"] == "system" for msg in conversation):
            system_prompt = self.agent_data.get("PrePrompt", "")
            conversation.insert(0, {"role": "system", "content": system_prompt})

        formatted_message = {"role": "user", "content": message}
        conversation.append(formatted_message)

        try:
            response_text = google_api_request(
                model=model,
                message=message,
                history=conversation
            )
        except Exception as e:
            response_text = str(e)
        
        conversation.append({"role": "assistant", "content": response_text})

        if debug:
            with open("logs_google.txt", "w", encoding="utf-8") as file:
                for i in conversation:
                    file.write(str(i) + "\n")

        return conversation