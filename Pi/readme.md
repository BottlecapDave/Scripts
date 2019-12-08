# Pi Scripts

The purpose of these scripts is to streamline setting up new Pi devices

## 01.InitialSetup

This creates a new user belonging to the same group as "pi" user. This is done for security reasons so people don't know the username.

## 02.SSHSetup

This sets up SSH keys for the logged in user.

## 03.HarddriveSambaSetup

This mounts a given harddrive, installs Samba and sets up Samba to expose the mounted harddrive.

## 04.SetupPlex

This installs Plex server on the Pi and configures the data to be stored on an external source (like the harddrive from script 03).