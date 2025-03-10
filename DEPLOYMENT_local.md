

# How to run Wordie locally:

1. Setup environment variables

- Register for an LLM API key and and create an environment variable named "OPENAI_API_KEY" with the key in it
- Create an env variable named "FLASK_SECRET_KEY" with a secret key for the Flask app
- Rememebr researcher acces env varibales for login
    #researcher login page
    researcher_username="wordie"
    researcher_password="laplace666$"


Here's example bash command to set env variables:
            #!/bin/bash
            # OpenAI API Key
            export OPENAI_API_KEY="your-openai-api-key"


4. Start the app

To start Wordie, run the following command:

```
gunicorn -w 4 -b 0.0.0.0:8000 wordie:app

```

5. Upon starting the app, you will be prompted to login with a prolific ID and password that is connected to an agent (experimental condition). 