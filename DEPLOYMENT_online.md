
# Original Guide


## Server Deployment

How to run on a server (e.g., AWS EC2 Instance or magical cloud connected to the internet):

Before Instance launch!  
- Get a domain name and set up server (AWS account activation and set elastic IP to domain in host service). You'll have to edit DNS settings in domain provider.  

Overview of examples components -> AWS EC2, Ubuntu, Flask, Gunicorn, Apache2, Certbot

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
Example code to do this:
Ex. rsync -avz -e "ssh -i /Users/a1809024/Desktop/PMC/AI_Interface/AWS/wordie.pem" ./* ubuntu@wordie-pilot.xyz:/srv/wordie/
Ex. rsync -avz --exclude="vent" --exclude="__pycache__" ../Wordie_1_0/ ubuntu@wordie.xyz:/srv/wordie/	
Ex. scp -i /Users/a1809024/Desktop/PMC/AI_Interface/AWS -r ./ ubuntu@wordie-pilot.xyz:/srv/wordie
	Head back to SSH connection

cd /srv/wordie && ls -l
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
	select 1 for nano and paste the following in nano, writeout, exit, to renew SSL cert automatically
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

	# OpenAI API Key (Wordie unpredictability project)
	OPENAI_API_KEY=Secret Key

    # Anthropic
    ANTHROPIC_API_KEY=Secret Key

	# Flask Secret Key
	FLASK_SECRET_KEY=Secret Key

    #researcher login page
    researcher_username="wordie"
    researcher_password="laplace666$"

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



## Server Performance Logging

**Setting up server performance logs**  

The following commands will setup server performance logs (memory, CPU usage and Traffic).  
Commands  
----------------  
mkdir -p /logs  
cd /logs
sudo nano /logs/log_resources.sh  
----------------  

	Add the following to the file:
while true; do
    sar -u 1 1 >> /logs/cpu_usage.log
    sar -r 1 1 >> /logs/memory_usage.log
    sar -n DEV 1 1 >> /logs/network_traffic.log
    sleep 10
done

Commands  
----------------  
chmod +x /logs/log_resources.sh
sudo nohup /logs/log_resources.sh &
----------------  

	To stop the process, find its PID (process ID) and kill it:
Commands  
----------------  
ps aux | grep log_resources.sh
kill <PID>
----------------  
  
**Visualising the logs**  

Commands
----------------
cd /logs
sudo bash -c "awk '/^[0-9]/ {print \$1, \$8}' cpu_usage.log > cpu_plot_data.log"
sudo bash -c "awk '/^[0-9]/ {print \$1, \$8}' memory_usage.log > memory_plot_data.log"
sudo bash -c "awk '/^[0-9]/ {print \$1, \$8}' network_traffic.log > network_plot_data.log"

gnuplot <<-EOFMarker
    set terminal dumb
    set xdata time
    set timefmt "%H:%M:%S"
    set format x "%H:%M"

    set xlabel "Time"
    set ylabel "Idle (%)"
    plot "cpu_plot_data.log" using 1:2 with lines title "CPU Idle"

    set ylabel "Usage"
	set yrange [0:100]
    plot "memory_plot_data.log" using 1:2 with lines title "Memory Usage"

    set ylabel "Traffic (bytes)"
    plot "network_plot_data.log" using 1:2 with lines title "Network Traffic"
EOFMarker
----------------

**Live Monitoring**

Commands
----------------
sudo apt install htop
htop
----------------


**WOHOO done…hopefully....nearly**

  Go to your browser and visit the IP or the domain name connected (domains can’t take up to 6 hours to connect to the IP). 








