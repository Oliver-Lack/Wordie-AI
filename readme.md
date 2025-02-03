# Wordie is a Flask based AI interface web app for Human-AI interaction research

The app runs with gunicorn for the production server, currently integrated with an OpenAI API, and dumps data to various files when API calls are made. This includes interactions.json, interactions_backup.csv, and AWS S3 bucket API integration. 
Each data files collects the same data from the interaction. Namely:
- user_id
- prolific_id
- temperature
- model
- user message
- AI message
- logprobs (log probabilities) of AI message
- sequence log probability
- interaction log probability
- prompt-tokens
- completion-tokens
- total-tokens
- timestamps

The users.db is used to store prolific IDs, interface assigned user_ids, conversation history, and passwords for experimental condition assignment.
The users.db is used for the apps functionality and not data collection or analyses. 


## How to run Wordie locally:

1. Setup environment variables

- Register for an LLM API key and and create an environment variable named "OPENAI_API_KEY" with the key in it
- Create an env variable named "FLASK_SECRET_KEY" with a secret key for the Flask app
- For AWS S3 bucket integration on a production server, follow AWS documentation (S3 not necessary for local development, currently just a backup data dump method) 

Here's a rough bash command to set the env variables when deploying an EC2 instance:
            #!/bin/bash
            # OpenAI API Key
            export OPENAI_API_KEY="your-openai-api-key"

            # Flask Secret Key
            export FLASK_SECRET_KEY="your-flask-secret-key"

            # AWS Credentials
            export AWS_ACCESS_KEY_ID="your-aws-access-key-id"
            export AWS_SECRET_ACCESS_KEY="your-aws-secret-access-key"
            export AWS_DEFAULT_REGION="your-aws-region"

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
- **User Role**: Attach AWS user role with S3 permissions.
  - Required for S3 bucket data dumps. Adjust bucket name in `.env`.

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




## Latest Experiment NOTES

For other researchers:
- The app currently logs data to MY S3 bucket on AWS. 
- IMPORTANT: IAM AWS role must have s3 access AND this role must be attached to the EC2 instance on launch (i.e., attach user role to instance on launch)
- Create your own bucket and change name in .env file accordingly.
- Scraping data files manually after experiment can be done by SSH into the instance and then running the following command to send to an S3 bucket:
    aws s3 cp interactions.json s3://wordie/
    aws s3 cp interactions_backup.csv s3://wordie/
    aws s3 cp users.db s3://wordie/
(Note: aws role must be attached to instance)

Extra info:
- If the agents are edited, the app needs to be reset to apply the changes.
- o1 model and agent will not work as the API is not yet available (released on 17/12/24)
- Numbers labelling agent conditions 1 = AI is guesser 2 = AI is giver.

ToDo:
- Connect conversation history to username AND password. 
- S3 Bucket send data 
- Get other models working

Measures of unpredictability required:
1. joint probability of sequence and interactions (iterated exponent of the summed logprobs)
2. prompt engineering score
3. Human Perception of unpredictability (survey)
4. zipf law score