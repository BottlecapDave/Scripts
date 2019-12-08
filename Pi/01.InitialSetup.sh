#!/bin/bash

# The purpose of this script is to
# 1) Make sure the Pi is up to date
# 2) Update the name of the Pi and make sure the memory split is accurate for a headless environment
# 3) Get rid of the original Pi user so if someone were to hack the device they don"t have a default user to target
# http://raspi.tv/2012/how-to-create-a-new-user-on-raspberry-pi https://www.modmypi.com/blog/how-to-add-new-users-and-add-users-to-groups

TARGET_USER="USER"

if [ $TARGET_USER = "USER" ]
then
    echo "TARGET_USER variable is not set. Exiting"
    exit
fi

# Update system
echo "Updating Pi..."
sudo apt update
sudo apt full-upgrade

# Perform raspi config setup
echo "Perform memory split, update name and expand SD card to full capacity"
read -p "Press [Enter] key to start raspi-config..."

# # Setup new user
sudo adduser $TARGET_USER
PI_GROUPS=$(groups pi)

# Add new user to the same group as Pi user
PI_GROUPS=$(cut -d':' -f2 <<<"$PI_GROUPS")

IFS=" " read -r -a array <<< "$PI_GROUPS"
for group in "${array[@]}"
do
    echo "Adding $TARGET_USER to group $group"
    sudo adduser $TARGET_USER $group
done

echo "$TARGET_USER groups"
groups $TARGET_USER