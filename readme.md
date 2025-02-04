# Wordie.AI - Human-AI Interaction Research App

**Wordie is a custom AI interface web app for Human-AI interaction research**

The app is hosted for demo purposes at [Wordie.AI](https://wordie.xyz)
default login: prolific_id = 1234, password = music
researcher login: username = wordie, password = laplace666$

For usage, questions or collaborations, please cite/acknowledge/contact Oliver Lack. 
        Australian Institute for Machine Learning (AIML) | School of Psychology 
        The University of Adelaide
        oliver.lack@adelaide.edu.au | oliver@oliverlack.com
        https://www.oliverlack.com



**Summary of the core Elements of Wordie-AI Interface:**

1. **Framework:** Flask
2. **Production Server:** Gunicorn
3. **API Integration:** OpenAI API
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
7. **Environment Variables:** OPENAI_API_KEY, FLASK_SECRET_KEY, S3_BUCKET_NAME
8. **Hosting:** AWS EC2 Instance
9. **Web Server:** Apache2
10. **SSL:** Certbot
11. **Experimental Setup:**
    - Participant conditioning via prolific ID, passwords 
    - Conditioning set using passwords in add_passwords.py
    - Agents directory holds condition settings
12. **Performance Optimization:** Swap Space
13. **Monitoring Tool:** htop
14. **Log Data Collection:** AWS SSO session setup with boto3 
    - S3 Bucket setup (bucket=wordie, SSOprofile=WordieLocal)
    - This is for batched interactions and manual transfer commands
15. ** Javascript:**
    - Cookie tracks reset button for Command Button appearance
    - All  button dynamics set between chat.js and chat.html


## How to run Wordie locally:

1. Setup environment variables

- Register for an LLM API key and and create an environment variable named "OPENAI_API_KEY" with the key in it
- Create an env variable named "FLASK_SECRET_KEY" with a secret key for the Flask app
- S3 AWS bucket setup required to log data to bucket. Must setup aws cli and sso config before running the app. Terminal commands below:
command: brew install awscli
command: aws configure sso     (fill out required identity data from access portal sso info. requires awscli 2)
Now create aws profile name and connect to admin account (profile name like WordieLocal).
Change profile name in boto3.Session to newly assigned name. 


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

### Prerequisites
- **Configure S3 Bucket with AWS CLI SSO Config**:
- S3 AWS bucket setup required to log data to bucket. Must setup aws cli and sso config before running the app. Terminal commands below:
command: brew install awscli
command: aws configure sso     (fill out required identity data from access portal sso info. requires awscli 2)
Now create aws profile name and connect to admin account (profile name like WordieLocal).
Change profile name in boto3.Session in wordie.py to newly assigned name (Do this BEFORE transferring app to instance). 

  - Specify S3 bucket data dumps. Adjust bucket name in `.env`.
  - Make sure profile_name matches the profile name in the boto3.Session in the app.

### Instance Specifications
- **Environment**: AWS, Ubuntu, Flask, Gunicorn, Apache2.

### Important Warning
- **Permissions**: Avoid mistakes with `sudo chown` commands.
  - Incorrect execution can lead to severe permission issues.

### Initial Setup

#### Launching Instance
1. **Start EC2**: Obtain instance with elastic IP.
2. **Domain Setup**: Configure domain (`wordie.xyz`).

#### SSH Access
- **Connect Command**:
  ```bash
  ssh -i "wordie.pem" ubuntu@<your-instance-IP>
  ```

#### Initial System Setup
- **Update and Install**:
  ```bash
  sudo apt-get update
  sudo apt-get install python3.venv
  ```

- **Create Directory**:
  ```bash
  sudo mkdir /srv/wordie
  sudo chown ubuntu:ubuntu /srv/wordie
  ```

#### Transfer Application Files
- **From Local Workspace**:
  ```bash
  rsync -avz --exclude="venv" --exclude="__pycache__" ../Wordie_1_0/ ubuntu@wordie.xyz:/srv/wordie/
  ```

#### SSH Post-Transfer Setup
1. **Validate Transfer**:
   ```bash
   cd /srv/wordie && ls -l
   ```
2. **Environment Setup**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install Flask
   pip install gunicorn
   pip install -r requirements.txt
   deactivate
   ```

### Service Configuration

#### Create Service File
- **Edit `wordie.service`**:
  ```bash
  sudo nano /etc/systemd/system/wordie.service
  ```
- **Service Content**:
  ```
  [Unit]
  Description=Wordie Flask App
  After=network.target
  
  [Service]
  User=wordie_user
  WorkingDirectory=/srv/wordie/
  ExecStart=/srv/wordie/venv/bin/gunicorn server:app -w 4 -b 127.0.0.1:8000        
  Restart=on-failure
  
  [Install]
  WantedBy=multi-user.target
  ```

- **Reload and Enable**:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable --now wordie.service
  ```

### Web Server Configuration

#### Apache Setup
1. **Install & Start Apache**:
   ```bash
   sudo apt install apache2
   sudo service apache2 start
   ```

2. **Configure Site**:
   ```bash
   cd /etc/apache2/sites-available/
   sudo mv 000-default.conf wordie.xyz.conf
   sudo nano wordie.xyz.conf
   ```

3. **Update Site Configuration**:
   ```
   <VirtualHost *:80>
     ServerName wordie.xyz
     ServerAlias www.wordie.xyz
     ProxyPass / http://127.0.0.1:8000/
     ProxyPassReverse / http://127.0.0.1:8000/
   </VirtualHost>
   ```

4. **Enable Proxies and Site**:
   ```bash
   sudo a2enmod proxy proxy_http
   sudo a2ensite wordie.xyz.conf
   sudo service apache2 reload
   ```

#### SSL Certificate
- **Install Certbot**:
  ```bash
  sudo snap install --classic certbot
  sudo ln -s /snap/bin/certbot /usr/bin/certbot
  ```

- **Get SSL Certificate**:
  ```bash
  sudo certbot --apache
  ```

- **Automate Renewal**:
  ```bash
  sudo crontab -e
  ```
  - Add:
    ```
    0 4 * * 1 /usr/bin/certbot renew --quiet && /usr/sbin/service apache2 reload
    ```

### Environment Variables

#### Configure `.env`
1. **Navigate & Activate**:
   ```bash
   cd /srv/wordie
   source venv/bin/activate
   sudo pip install python-dotenv
   ```

2. **Create `.env`**:
   ```bash
   sudo nano /srv/wordie/.env
   ```

3. **Add Variables**:
   ```
   # AWS S3 Bucket
   S3_BUCKET_NAME=wordie
   
   # OpenAI API Key
   OPENAI_API_KEY="Secret Key"
   
   # Flask Secret Key
   FLASK_SECRET_KEY="Secret Key"
   ```

#### Update Service with Env
- **Modify `wordie.service`**:
  - Add in `[Service]` section:
    ```
    EnvironmentFile=/srv/wordie/.env
    ```

- **Restart Service**:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl restart wordie
  ```

### Performance Optimization

#### Add Swap Space
- **Setup Swap**:
  ```bash
  sudo fallocate -l 1G /swapfile
  sudo chmod 0600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  ```

- **Persist Swap Setting**:
  ```bash
  sudo nano /etc/fstab
  ```
  - Add:
    ```
    /swapfile none swap sw 0 0
    ```

- **Reboot Instance**:
  ```bash
  sudo reboot
  ```

### Monitoring
- **Install `htop`**:
  ```bash
  sudo apt install htop
  htop
  ```

**Completion**:
- Access your instance via IP or domain (`wordie.xyz`). Domain propagation may take up to 6 hours.




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