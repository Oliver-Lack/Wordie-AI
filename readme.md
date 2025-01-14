# Wordie is a Flask based AI interface web app for Human-AI interaction research

1. Register for an API key and and create an environment variable named "OPENAI_API_KEY" with the key in it

2. Run the add_passwords.py file to setup database for link between passwords and loading conditions (agents) into app.

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
- Numbers labelling agent conditions 1 = AI is guesser 2 = AI is giver.


ToDo:
2. calculate sum of logprobs for each message and log to json
3. calculate sum of logprobs for each conversation and log to json
8. backup log of json data as json and csv to cloud server. 
9. get other models working

Measures of unpredictability required:
1. joint probability of sequence and interactions (iterated exponent of the summed logprobs)
2. prompt engineering score
3. Human Perception of unpredictability (survey)
4. zipf law score