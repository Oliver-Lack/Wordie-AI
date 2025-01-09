# This works towards calculating a join probability of a sequence of tokens from each user interaction.
#logprobs logs all the logarithmic probabilities calculated for each sampled token in every response.
#This can be seen in the interactions.json file.
#https://cookbook.openai.com/examples/using_logprobs


# LLM sampling sequence is UserInput->LLMStuff-> RawLogits->TemperatureScalingOfRawLogits->Softmax(LogProbs)->TokenSampling
# Current understanding: TEMP DOES EFFECT LOGPROBS!! SHOULD NOT SEE HUGE DIFFERENCE DISTRIBUTION OF LOGPROBS IN HIGH/LOW TEMP AGENTS
# Therefore, the calculated joint probability of the logprobs in the interactions.json file  will only control for stochastic sampling.
# This does not provide a "true" joint probability unless iterate again with a fixed temperature.



########### Create Temperature controlled logprobs

def get_logprobs_for_response(response_text, original_message, model="gpt-3.5-turbo"):
    # Formulate the message history for context
    messages = [
        {"role": "user", "content": original_message},
        {"role": "assistant", "content": response_text}
    ]
    
    # Call OpenAI API to get logprobs for the response in the context of the original message
    response = openai.Completion.create(
        model=model,
        prompt='',
        max_tokens=0,
        messages=messages,
        logprobs=5,
        temperature=1
    )
    
    # Assuming the model allows; in practice, you might directly access logprobs using pattern knowledge by inspecting the API request format
    logprobs = response.choices[0].logprobs.get('token_logprobs', [])
    return logprobs

def process_and_log_interactions(input_json_path, output_json_path):
    # Load user interactions from JSON file
    with open(input_json_path, 'r') as infile:
        data = json.load(infile)

    # Prepare a structure to hold the new logprobs data
    new_data = {"users": {}}

    for user_id, user_data in data['users'].items():
        username = user_data.get('username', '')
        interactions = user_data.get('interactions', [])
        
        new_interactions = []
        
        for interaction in interactions:
            if interaction['type'] == 'message':
                content = interaction['content']
                message = content['message']
                response = content['response']
                
                # Get original response logprobs without generating new text
                logprobs = get_logprobs_for_response(response, message)
                
                # Create a new entry with logprobs
                new_interactions.append({
                    "type": "logprobs_analysis",
                    "content": {
                        "original_response": response,
                        "logprobs": logprobs,
                        "model": content['model'],
                        "timestamp": content['timestamp']
                    }
                })
        
        # Store processed interactions in new data structure
        new_data["users"][user_id] = {
            "username": username,
            "interactions": new_interactions
        }

    # Save new data with logprobs to output JSON file
    with open(output_json_path, 'w') as outfile:
        json.dump(new_data, outfile, indent=4)

# Example usage
process_and_log_interactions('interactions.json', 'tempControlledLogProbs.json')



############ Log new logprobs to tempControlledLogprobs.json with user info




############ Calculate joint probability for logprobs of individual messages and full interaction and dump in tempControlledLogprobs.json

import math

def calculate_joint_probability(logprobs):
    """
    Calculate the joint probability of a sequence of tokens given their log probabilities.

    :param logprobs: List of log probabilities for each token in the sequence
    :return: Joint probability of the sequence
    """
    if not logprobs:
        return 0.0  # Return 0 for an empty sequence (or you could raise an exception)

    # Sum all the log probabilities
    total_logprob = sum(logprobs)
    
    # Exponentiate the sum to obtain the joint probability
    joint_probability = math.exp(total_logprob)
    
    return joint_probability

# Example usage
logprobs_example = [-0.76, -0.55, -0.85, -1.00, -0.70]
joint_prob = calculate_joint_probability(logprobs_example)
print(f"Joint Probability: {joint_prob}")



########### Calculate total joint probability of each unpredictability condition. 



