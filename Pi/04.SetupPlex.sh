#!/bin/bash

# Setup Plex server https://pimylifeup.com/raspberry-pi-plex-server/

TARGET_USER="USER"

if [ $TARGET_USER = "USER" ]
then
    echo "TARGET_USER variable is not set. Exiting"
    exit
fi

echo "Installing Plex server..."
sudo apt-get install apt-transport-https
curl https://downloads.plex.tv/plex-keys/PlexSign.key | sudo apt-key add -
echo deb https://downloads.plex.tv/repo/deb public main | sudo tee /etc/apt/sources.list.d/plexmediaserver.list
sudo apt-get update
sudo apt-get install plexmediaserver

echo "Setting up plex config..."
cd /etc/default/
sudo cp plexmediaserver plexmediaserver.bak

sudo systemctl stop plexmediaserver

# Change the user the server is running as and update where the database information is stored
sudo sed -i "s/export PLEX_MEDIA_SERVER_USER=plex/export PLEX_MEDIA_SERVER_USER=$TARGET_USER/g" plexmediaserver
echo "What is the root directory where your plex server data should live (e.g./storage/pi/plexserver)?"
read response
sudo su -c "echo \"export PLEX_MEDIA_SERVER_APPLICATION_SUPPORT_DIR='$response\Application Support'\" >> plexmediaserver"

# Create a symlink to our data
sudo ln -s "$response\Application Support" "Application Support"

echo "Restarting Plex Server..."
sudo systemctl restart plexmediaserver