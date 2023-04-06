# Pakete installieren
sudo apt-get -qq update
sudo apt-get -qq install apache2 python3.8 git libssl-dev python3-pip python3-venv software-properties-common libpython3.8-dev

# create user
sudo adduser --gecos "" radarexec

# download
git clone https://github.com/DasElias/telegram-radar-warner.git /var/radarwarner/app/

# create venv
python3 -m venv /var/radarwarner/app/venv
source /var/radarwarner/app/venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade telethon
pip install python-dotenv
pip install hypercorn==0.12.0
pip install Aeros==0.3.1
pip install emoji==1.7.0
pip install pytz
pip install python-dateutil

# create service
sudo sh -c 'cat > /etc/systemd/system/radarwarner.service << EOF
[Unit]
Description=Telegram Radar Warner Server
After=network.target

[Service]
Type=simple
User=radarexec
WorkingDirectory=/var/radarwarner/app
ExecStart=/var/radarwarner/app/venv/bin/python3 /var/radarwarner/app/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

# don't forget to set the environment variables in /var/radarwarner/app/.env

sudo systemctl enable radarwarner.service
# show log:
# journalctl -u radarwarner.service -b

# setup reverse proxy
sudo sh -c 'cat > /etc/apache2/sites-available/z_radar.conf << EOF
<VirtualHost *:80>
ServerAdmin webmaster@localhost
ServerName radar.daselias.io

ProxyPreserveHost On
ProxyPass / http://localhost:5000/
ProxyPassReverse / http://localhost:5000/

ErrorLog /error.log
CustomLog /access.log combined

RewriteEngine on
RewriteCond %{SERVER_NAME} =radar.daselias.io
RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>
EOF'

sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod rewrite
sudo a2ensite -q z_radar.conf
sudo service apache2 restart
