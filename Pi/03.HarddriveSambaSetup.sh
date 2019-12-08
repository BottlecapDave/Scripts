#!/bin/bash

# Setup an external harddrive https://www.modmypi.com/blog/how-to-mount-an-external-hard-drive-on-the-raspberry-pi-raspian
# Seup Samba access for the external harddrive http://raspberrypihq.com/how-to-share-a-folder-with-a-windows-computer-from-a-raspberry-pi/
# Setup SWAP file using the new external harddrive https://raspberrypi.stackexchange.com/a/75

SAMBA_SHARE_NAME="Storage"
TARGET_USER="USER"

if [ $TARGET_USER = "USER" ]
then
    echo "TARGET_USER variable is not set. Exiting"
    exit
fi

# Delete the pi user as they're a security risk
echo "Deleting Pi user..."
sudo deluser pi

# Setup the external hard drive 
echo "Setting up external harddrive..."
sudo fdisk -l
echo "Where is the drive located?"
read response

sudo apt-get install ntfs-3g

sudo mkdir /storage
sudo mount -t ntfs-3g $response /storage
sudo chmod 775 /storage

sudo su -c "echo /dev/sda1    /storage   ntfs-3g  rw,defaults     0   0 >> /etc/fstab"

# Set up samba so we can access our harddrive on other devices in the network
echo "Setting up Samba..."
sudo apt-get install samba samba-common-bin

sudo su -c "echo -n \"[$SAMBA_SHARE_NAME]
   comment=$SAMBA_SHARE_NAME
   path=/storage
   browseable=Yes
   writeable=Yes
   only guest=no
   create mask=0777
   directory mask=0777
   public=no \" >> /etc/samba/smb.conf"

echo "Setting up samba access"
sudo smbpasswd -a $TARGET_USER

sudo service smbd restart

# Setup SWAP on harddrive to preserve read/writes on SD card when required data exceeds available RAM 
echo "Would you like to setup SWAP on your new harddrive? (y/n)"
read response

if [ $response = "y" ]
then
    dd if=/dev/zero of=/storage/Pi-System/swapfile bs=1M count=1024 # For 1GB swap file
    mkswap /storage/Pi-System/swapfile
    sudo swapon /storage/Pi-System/swapfile
fi