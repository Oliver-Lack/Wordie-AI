# Wordie: The Human-AI Interaction Research App  

**Wordie is a custom AI interface web app for Human-AI interaction research**  

The app is built from the chatPsych codebase [chatPsych](https://chatpsych.org)  

default login: 		prolific_id = [anything], password = music   
researcher login: 	username = wordie, password = laplace666$   

For usage, questions or collaborations, please cite/acknowledge/contact:  
        Oliver Lack  
        Australian Institute for Machine Learning (AIML) | School of Psychology   
        The University of Adelaide  
        oliver.lack@adelaide.edu.au | oliver@oliverlack.com  
[        https://www.oliverlack.com   
](https://oliverlack.com/)


**Summary of the core Elements of Wordie-AI Interface:**  

Wordie is designed to scrape a plethora of interaction data especially relevant to various human-AI interaction research.
It is scalable and easy to experimentally customise and condition participant groups. This interface aims to make interaction with
real-world AI systems more accessible. Integration with Qualtrics, Prolific, MTurk or other platforms for online sampling is easy.

The code is adaptable for various experimental manipulations. For example, manipulations that involve prompt engineering, API call parameters, 
AI model selection, communication modalities (audio/text), custom vector store retrieval, hardcoded experimental AI responses/prompts, and more. 

Summary of Wordie's core features:
1. **Framework:** Flask
2. **Production Server:** Gunicorn
3. **API Integration:** OpenAI, Anthropic, LLAMA, Gemini
4. **Data Files:**
   - interactions.json
   - interactions_backup.csv
5. **Data Attributes:**
   - user_id
   - prolific_id
   - temperature
   - model
   - messages (user, AI)
   - log probabilities (AI)
   - Relative Sequence log probability 
   - Relative Interaction log probability
   - token counts
   - timestamps
6. **Database:** users.db
    - The users.db is used for the apps functionality and not data collection or analyses. 
7. **Researcher Dashboard GUI**
8. **Production Server Integration:** AWS EC2 Instance
9. **Web Server:** Apache2
10. **SSL:** Certbot
11. **Experimental Setup:**
    - Participant conditioning via prolific ID, passwords 
    - Conditioning set using db passwords for survey integration
    - Easily modified Agents JSON directory for condition settings
12. **Performance Optimization:** 
    - Swap Space, standardised delays, cookie tracking for dynamics
13. **Log Data Collection:** 
    - interactions.json, interactions_backup.csv
14. **Aesthetics** 
    - Customised graphics, logos, and aesthetics
    - Full CSS and javascript dynamics drafted

