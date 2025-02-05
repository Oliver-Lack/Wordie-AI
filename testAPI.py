from API_anthropic import API_Call_2

# Initialize the API_Call_2 class
api_call = API_Call_2()

# Define a sample conversation
conversation = []

# Define a sample message and system message
message = "What happened at Tiananmen Square in 1989?"

# Call the thinkAbout method
conversation, input_tokens, output_tokens = api_call.thinkAbout(message, conversation)

# Print the results
print("Conversation:", conversation)
print("Input Tokens:", input_tokens)
print("Output Tokens:", output_tokens)
print(api_call.agent_data["temperature"])