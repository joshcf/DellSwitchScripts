# DellSwitchScripts
Scripts for managing Dell N1500 and N2000 switches

## Requrements
 - Python 3
 - Paramiko Python module installed

## dellSwitches.csv

CSV file that lists all the edge switches by hostname and useful info for them such as location and zone.

CSV is in the following format:

Hostname,Location,Zone,Domzone

Hostname = Hostname of switch
Location = Used for course location of switch
Zone = Used for network zone
Domzone = used for secondary network zone info

For use with firmware update, only the first column is needed.

## coreSwitches.csv

Similar to dellSwitches.csv, but for the core switches.

## serverSwitches.csv

Similar to dellSwitches.csv, but for the server top of rack switches.

## fimrwareUpdate.py

This script loops through each switch defined in dellSwitches.csv and goes through the update process as described in the Dell documentation for updating to version 6.5.2.18 on N1500 and N2000 switches.

It prompts for the switch admin and enable passwords, and the TFTP server IP address and then uses these to ssh on to each switch in turn.

To work, it needs the new firmware to be in the root of the TFTP server, renamed N1500.stk or N2000.stk

For each switch it will:

 - Find out if the switch is an N1500 or N2000 model
 - Save the currently running config to the startup config
 - Backup the currently running config to the TFTP server
 - Copy the new firmware to the backup
 - Set the switch to boot off the backup
 - Remove the HiveAgent files as documented in the Dell release notes
 - Reload the switch and wait for it to come back up
 - Re-connect to the switch
 - Apply the configuration so that MAB authentication is the same as in the 6.3.x firmware
 - Update the bootcode
 - Reload the switch again and wait for it to come back
 - Connect to the switch again
 - If N1500, ends here, if N2000 check CPLD version
 - If CPLD version is not 20 (current for the 6.5.2.18 firmware) and the switch is not in a stack, update the CPLD

## tftpRunningConfig.py

Script that goes through all the switches defined in the CSV files and copys the running config to the TFTP server specified.

## writeConfig.py

Script that goes through all the switches defined in the CSV files and writes the running config to memory.
