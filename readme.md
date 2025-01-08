# Wordie is a Flask based AI interface web app for Human-AI interaction research

1. Register for an API key and and create an environment variable named "OPENAI_API_KEY" with the key in it

2. Start the app

To start Wordie, run the following command:
```
python wordie.py [agent_name]
```
Replace `[agent_name]` with the name of the condition you want the Wordie to use (HighTemp, LowTemp, StandardTemp). An agent name is required. "default" can be used for each LLMs default call options. The agent is defined by the details of the API call modified by the .json file in the `agents` folder.
```
Terminal command example: python wordie.py StandardTemp
```

3. Upon starting the app, you are prompted to input a prolific ID. 



Extra info:

- If the agents are edited, the app needs to be reset to apply the changes.
- o1 model and agent will not work as the API is not yet available (released on 17/12/24)

