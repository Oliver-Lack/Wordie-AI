This is a rough guid on setting this app up on an AWS Instance

Before Instance launch! Attach an AWS user role with s3 permissions to the instance you are creating 
(This is for s3 bucket batched data dumps. Change bucket name in env accordingly).

Instance details -> AWS, Ubuntu, Flask, Gunicorn, Apache2

Important Tip - DO NOT stuff up any of the sudo chown commands. You will F#*! up permissions to root if you forget the wrong /. I’ve done this twice and wanted to punch a window both times. If this happens…Pack up your belongings, delete the instance, and start again…


First, get EC2  instance running, set elastic IP, set domain name host service (Domain set in these instructions is wordie.xyz)

	SSH into instance: (remember to be in directory of the .pem key file)
EX.  ssh -i "wordie.pem" ubuntu@ec2-52-64-0-79.ap-southeast-2.compute.amazonaws.com

	Once SSH successful, follow these commands:

sudo apt-get update
sudo apt-get install python3.venv
sudo mkdir /srv/wordie
sudo chown ubuntu:ubuntu /srv/wordie

	Send directory from local computer to wordie AWS instance (Will need to edit paths and names 	accordingly)
	From local workspace directory
rsync -avz --exclude="vent" --exclude="__pycache__" ../Wordie_1_0/ ubuntu@wordie.xyz:/srv/wordie/	or
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
Group-wordie_user
WorkingDirectory=/srv/wordie/
ExecStart=/srv/wordie/venv/bin/gunicorn server:app -w 4 -b 127.0.0.1:8000        
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


WOHOO done…hopefully. 

Go to your browser and visit the IP or the domain name connected (domains can’t take up to 6 hours to connect to the IP). 

	To monitor memory, compute etc… use the following method:

SSH into the instance and commands:
sudo apt install htop
htop




