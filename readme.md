# Wordie: The Human-AI Interaction Research App  

**Wordie is a custom AI interface web app for Human-AI interaction research**  

The app is hosted for demo purposes at [wordie.xyz](https://wordie.xyz)  

default login: prolific_id = [anything], password = music  
researcher login: username = wordie, password = laplace666$  

For usage, questions or collaborations, please cite/acknowledge/contact:  
        Oliver Lack  
        Australian Institute for Machine Learning (AIML) | School of Psychology   
        The University of Adelaide  
        oliver.lack@adelaide.edu.au | oliver@oliverlack.com  
        https://www.oliverlack.com  



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
   - AWS S3 bucket (interaction_batch.json)
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
13. **Log Data Collection:** AWS SSO session setup with boto3 
    - S3 Bucket setup (bucket=wordie, SSOprofile=WordieLocal)
    - This is for batched interactions and manual transfer commands
14. **Aesthetics** 
    - Customised graphics, logos, and aesthetics
    - Full CSS and javascript dynamics drafted


## How to run Wordie locally:

1. Setup environment variables

- Register for an LLM API key and and create an environment variable named "OPENAI_API_KEY" with the key in it
- Create an env variable named "FLASK_SECRET_KEY" with a secret key for the Flask app
- S3 AWS bucket setup required to log data to bucket. Must setup aws cli and sso config before running the app. Terminal commands below: (extra hint: create your own aws account and s3 bucket first)
command: brew install awscli
command: aws configure sso     (fill out required identity data from access portal sso info. requires awscli 2)
Now create aws profile name and connect to admin account (profile name like WordieLocal).
Change profile name in boto3.Session in wordie.py to newly assigned name. 


Here's some bash commands to set the other env variables:
            #!/bin/bash
            # OpenAI API Key
            export OPENAI_API_KEY="your-openai-api-key"

            # Flask Secret Key
            export FLASK_SECRET_KEY="your-flask-secret-key"

            # AWS S3 Bucket
            export S3_BUCKET_NAME=wordie

            echo "Environment variables have been set."


4. Start the app

To start Wordie, run the following command:

```
gunicorn -w 4 -b 0.0.0.0:8000 wordie:app

```

5. Upon starting the app, you will be prompted to login with a prolific ID and password that is connected to an agent (experimental condition). 


## Setting Up Wordie App on AWS Instance

How to run Wordie on an AWS EC2 Instance (on a magical cloud connected to this thing called the internet):

Before Instance launch! 
- Get an AWS user with s3 permissions and create an s3 bucket.   
(This is for the batched data dumps. Change bucket name in env accordingly).  
- Get a domain name and set up host service on AWS. Set elastic IP to domain. You'll have to edit DNS settings in domain provider.  

Instance details -> AWS, Ubuntu, Flask, Gunicorn, Apache2  

Important Tip - DO NOT stuff up any of the sudo chown commands. You will F#*! up permissions to root if you forget the wrong /. I’ve done this twice and wanted to punch a window both times. If this happens…Pack up your belongings, delete the instance, and start again…  


Now get an EC2 Instance running  

	SSH into instance: (remember to be in directory of the .pem key file)
EX.  ssh -i "wordie.pem" ubuntu@ec2-52-64-0-79.ap-southeast-2.compute.amazonaws.com

	Once SSH successful, follow these commands:

sudo apt-get update
sudo apt-get install python3.venv
sudo mkdir /srv/wordie
sudo chown ubuntu:ubuntu /srv/wordie

	Send directory from local computer to wordie AWS instance (Will need to edit paths and names 	accordingly)
	From local workspace directory
rsync -avz --exclude="vent" --exclude="__pycache__" ../Wordie_1_0/ ubuntu@wordie.xyz:/srv/wordie/	
or
scp -i /Users/a1809024/Desktop/PMC/AI_Interface/AWS -r ./ ubuntu@13.237.109.252:/srv/wordie
	Head back to SSH connection

cd /srv/wordie && ls -l    (this checks whether files sent correctly)
python3 -m venv venv
source venv/bin/activate
pip install Flask
pip install gunicorn
pip install -r requirements.txt
deactivate
sudo nano /etc/systemd/system/wordie.service
	
	Setup wordie background service in nano by pasting the following below into editor 
	followed by 	control+O, enter, then control+X.
[Unit]
Description=Wordie Flask App
After=network.target

[Service]
User=wordie_user
Group=wordie_user
WorkingDirectory=/srv/wordie/
ExecStart=/srv/wordie/venv/bin/gunicorn wordie:app -w 4 -b 127.0.0.1:8000        
Restart=on-failure

[Install]
WantedBy=multi-user.target

sudo systemctl daemon-reload
sudo systemctl enable --now wordie.service
sudo apt install apache2
cd /etc/apache2/sites-available/
sudo rm default-ssl.conf
sudo service apache2 start
sudo mv 000-default.conf wordie.xyz.conf
sudo nano wordie.xyz.conf
	
	Edit wordie conf file by pasting the below into the nan editor
	
<VirtualHost *:80>
        ServerName wordie.xyz
        ServerAlias www.wordie.xyz

        ProxyPass / http://127.0.0.1:8000/
        ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>


sudo a2enmod proxy proxy_http
sudo a2dissite 000-default.conf
sudo a2ensite wordie.xyz.conf
sudo service wordie start
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot --apache
	set ssl cert fr both domains by selecting 1 2 enter
sudo crontab -e
	select 1 for nano and paste the following in nano, whiteout, exit, to renew SSL cert automatically
	0 4 * * 1 /usr/bin/certbot --renew && /usr/sbin/service apache2 reload
sudo adduser --system --no-create-home --group wordie_user
sudo nano /etc/systemd/system/wordie.service
	Set/Check the user and group in the .service file to the user you just added “wordie_user”
sudo chown -R wordie_user:wordie_user /srv/wordie/
sudo systemctl daemon-reload
sudo service wordie restart
sudo service wordie status


	Now you need to set all env variables for secret keys and API keys. 

cd /srv/wordie
source venv/bin/activate
sudo /srv/wordie/venv/bin/pip install python-dotenv
sudo nano /srv/wordie/.env
	
	Now write in .env file
 	
	EX. 

	# AWS Access Keys
	AWS_ACCESS_KEY_ID=“Secret Key” 
	AWS_SECRET_ACCESS_KEY="Secret Key"
	AWS_SESSION_TOKEN="Secret Key"

	#AWS S3 Bucket
	S3_BUCKET_NAME=wordie
	S3_KEY=Secret Key
	S3_SECRET=Secret Key

	# OpenAI API Key (Wordie unpredictability project)
	OPENAI_API_KEY=Secret Key

	# Flask Secret Key
	FLASK_SECRET_KEY=Secret Key

sudo nano /etc/systemd/system/wordie.service
	add    EnvironmentFile=/srv/wordie/.env
	in the [Service] section of the service file

sudo systemctl daemon-reload
sudo systemctl restart wordie
sudo systemctl status wordie
deactivate

	Adding swap space to stop memory crashing at hight spikes
sudo fallocate -l 1G /swapfile
sudo chmod 0600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
free -m
sudo nano /etc/fstab
	add this to bottom empty line
	/swapfile       none            swap    sw              0 0
sudo reboot

**WOHOO done…hopefully....nearly**

Now you need to setup the boto3 session for SSO to log data to an S3 bucket. The App requires this.  
To do this, you must setup aws cli and sso config before running the app. Terminal commands below: (extra hint: create your own aws account and s3 bucket first)  

(SSH into instance and run the following commands; You may need to uninstall the default aws CLI version first Version 2 required)
pip apt install awscli 
     (installing version 2 of awscli in the venv and globally might take some extra mucking around. Don't give up)
aws configure sso     

  (fill out required identity data from access portal sso info.)
  Now create aws profile name and connect to admin account (profile name like WordieLocal).
  Change profile name in boto3.Session in wordie.py to newly assigned name. 

  Go to your browser and visit the IP or the domain name connected (domains can’t take up to 6 hours to connect to the IP). 

	To monitor memory, compute etc… use the following method:

SSH into the instance and commands:
sudo apt install htop
htop





## Updates & Notes

**Researcher Dashboard:**
The researcher dashboard GUI is still a work in progress.
Prospective updates will include:
                -> Some "general settings" to change models, selection of output as text, audio, audio&text.
                -> An editor for the second interaction data capture (command-prompt/moral action button).
                -> Some visuals and descriptive graphics for interaction data. 

**Message to other researchers**
- Please contact [me](https://oliverlack.com) if you want to collaborate/adapt the system for your purpose. Happy to help. 
- The app currently logs data to MY S3 bucket on AWS. 
- Create your own bucket and change name in .env file and SSO CLI profile name accordingly (Instructions are above on setting s3 bucket).
- Scraping data files manually after experiment can be done by SSH into the instance and then running the following command to send to an S3 bucket:
(Change bucket name followed by set SSO CLI profile name accordingly)
    aws s3 cp interactions.json s3://wordie/ --profile WordieLocal
    aws s3 cp interactions_backup.csv s3://wordie/ --profile WordieLocal
    aws s3 cp users.db s3://wordie/ --profile WordieLocal

**Extra info**
- Numbers labelling current AI agent conditions 1 = AI is guesser 2 = AI is giver.



**PMC Study 1**
TODO List:
- Get other models working

- Measures of unpredictability:
1. joint probability of sequence and interactions (iterated exponent of the summed logprobs)
2. prompt engineering score
3. Human Perception of unpredictability (survey)
4. zipf law score
