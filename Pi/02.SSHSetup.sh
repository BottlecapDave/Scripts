#!/bin/bash

# The purpose of this script is to setup SSH so that we can connect to the Pi in a secure fashion
# http://raspi.tv/2012/how-to-set-up-keys-and-disable-password-login-for-ssh-on-your-raspberry-pi 

TARGET_USER="USER"
SSH_PORT=1234

if [ $TARGET_USER = "USER" ]
then
    echo "TARGET_USER variable is not set. Exiting"
    exit
fi

if [ $TARGET_USER != "$USER" ]
then
    echo "You must be logged in as your target user before running this script"
    exit
fi

# Setup SSH keys 
echo "Setting up SSH keys..."

cd ~
mkdir .ssh
cd .ssh

echo "Press enter when prompted for location"
ssh-keygen -t rsa -b 2048

mv id_rsa.pub authorized_keys
chmod 700 ~/.ssh/
chmod 600 ~/.ssh/authorized_keys

echo "-- Begin ------------------------------------"
cat id_rsa
echo "-- End --------------------------------------"
read -p "Copy the contents above. Press enter once complete."
rm id_rsa

# Setup SSH to use new SSH keys

echo "Updating SSH config..."
cd /etc/ssh
cp sshd_config sshd_config.bak
sudo sed -i "s/#PasswordAuthentication yes/PasswordAuthentication no/g" sshd_config
sudo sed -i "s/#Port 22/Port $SSH_PORT/g" sshd_config

echo "Rebooting SSH server..."
sudo /etc/init.d/ssh restart

echo "Try and log in using your new user and ssh credentials"