# Wordie is a Flask based AI interface web app for Human-AI interaction research

1. Register for an API key and and create an environment variable named "OPENAI_API_KEY" with the key in it

2. Start the app

To start Wordie, run the following command:

```
gunicorn -w 4 -b 0.0.0.0:8000 wordie:app

```

3. Upon starting the app, you will be prompted to login with a prolific ID and password that is connected to an agent (experimental condition). 



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