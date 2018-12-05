import paramiko
import time
import csv
import getpass

# Setup some initial variables
username = 'admin'
# Prompt for the switch admin password
password = getpass.getpass(prompt='Switch Admin password: ')
secret = getpass.getpass(prompt='Switch Enable password: ')
tftpServer = input('TFTP Server IP Address: ')

# Preload some variables
reloadSwitchFirmware = 'n'



print('*************************************************')
print('*************************************************')
print('*************************************************')
print('*************************************************')
print('Script Start')
print('*************************************************')
print('*************************************************')
print('*************************************************')
print('*************************************************')

with open('dellSwitches.csv', 'r') as hostFile:
	hosts = csv.reader(hostFile)
	# Skips header row of csv
	next(hosts)

	for row in hosts:
		# main loop
		reloadSwitchFirmware = 'n'
		print(('Testing to %s' % row[0]))

		connectSuccess = False

		# SSH Stuff

		# Create instance of SSHClient object
		remote_conn_pre = paramiko.SSHClient()

		# Automatically add untrusted hosts
		# (make sure okay for security policy in your environment)
		remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		try:
			# initiate SSH connection
			remote_conn_pre.connect(
				row[0],
				username=username,
				password=password,
				look_for_keys=False,
				allow_agent=False)
			print(('SSH Connection established to %s' % row[0]))
			connectSuccess = True
		except:
			pass
			# Use invoke_shell to establish an 'interactive session'

		if connectSuccess is True:
			remote_conn = remote_conn_pre.invoke_shell()
			print('Interactive SSH session established')
			# Strip the initial router prompt
			output = remote_conn.recv(1000)
			# See what we have
			print((output.decode()))
			remote_conn.send('enable\n')
			time.sleep(1)
			remote_conn.send(secret + '\n')
			time.sleep(1)
			output = remote_conn.recv(1000)
			print((output.decode()))
			print('Clear Buffer')
			
			reloadSwitchFirmware = 'n'
			reloadSwitchBoodcode = 'n'
			reloadSwitchCPLD = 'n'
			cpldUpdate = 'y'
			
			
			
			
			# Get Switch Series
			remote_conn.send('show version | include "System Model"\n')
			time.sleep(1)
			output = remote_conn.recv(1000)

			version = ''
			output = output.decode()
			outputlines = output.splitlines()
			for i, outputline in enumerate(outputlines):
				if 'N15' in outputline:
					version = 'N1500'
				elif 'N20' in outputline:
					version = 'N2000'

			print(version)
			
			# Copy Running config to startup
			print('***********************************')
			print('Copying Running config to Startup Config')
			remote_conn.send('copy running-config startup-config\n')
			remote_conn.send('y')
			time.sleep(1)
			output = remote_conn.recv(1000)
			print('##### OUTPUT #####')
			print((output.decode()))
			
			
			# Copy running config to TFTP
			print('***********************************')
			print('Copying Running config to TFTP')
			remote_conn.send('copy running-config tftp://' + tftpServer + '/' + row[0] + '.txt\n')
			remote_conn.send('y')
			
			print('Sleeping for copy')
			# Loop keeps checking for the transfer complete text
			done = 'no'
			while done == 'no':
				time.sleep(5)
				output = remote_conn.recv(5000)
				output = output.decode()
				print('Checking if done....')
				results = output.splitlines()
				for i, result in enumerate(results):
					print(result)
					if 'File transfer operation completed successfully' in result:
						done = 'yes'
						print('Transfer Done!')
						break
					elif 'STK file transfer operation successful. All units updated code.' in result:
						done = 'yes'
						print('Transfer Done!')
						break
					elif 'Firmware downloaded successfully.  All stack units updated.' in result:
						done = 'yes'
						print('Transfer Done!')
						break
				print('Still Transfering....')
			
			
			
			# Copy new firmware from TFTP
			print('***********************************')
			print('Copying Running config to TFTP')
			remote_conn.send('copy tftp://' + tftpServer + '/' + version + '.stk backup\n')
			remote_conn.send('y')
			print('Sleeping for copy')
			# Loop keeps checking for the transfer complete text
			done = 'no'
			while done == 'no':
				time.sleep(5)
				output = remote_conn.recv(5000)
				output = output.decode()
				print('Checking if done....')
				results = output.splitlines()
				for i, result in enumerate(results):
					print(result)
					if 'File transfer operation completed successfully' in result:
						done = 'yes'
						print('Transfer Done!')
						break
					elif 'STK file transfer operation successful. All units updated code.' in result:
						done = 'yes'
						print('Transfer Done!')
						break
					elif 'Firmware downloaded successfully.  All stack units updated.' in result:
						done = 'yes'
						print('Transfer Done!')
						break
				print('Still Transfering....')

			# Set to boot off backup next reboot
			print('***********************************')
			print('Setting system to boot from new firmware')
			remote_conn.send('boot system backup\n')
			time.sleep(10)
			output = remote_conn.recv(1000)
			print('##### OUTPUT #####')
			print((output.decode()))
			
			# Fix HiveAgent
			print('***********************************')
			print('Applying HiveAgent Fixes')
			remote_conn.send('application stop hiveagent\n')
			remote_conn.send('delete user-apps/ah_ha.conf_s\n')
			remote_conn.send('y')
			remote_conn.send('delete user-apps/hiveagent_pr_s\n')
			remote_conn.send('y')
			remote_conn.send('delete user-apps/ah_ha.conf\n')
			remote_conn.send('y')
			remote_conn.send('delete user-apps/hiveagent_pr\n')
			remote_conn.send('y')
			remote_conn.send('delete user-apps/hiveagent\n')
			remote_conn.send('y')
			time.sleep(1)
			output = remote_conn.recv(2000)
			print('##### OUTPUT #####')
			print((output.decode()))
			
			# Reload switch
			print('***********************************')
			print('Reloading Switch to new Firmware')
			reloadSwitchFirmware = 'y'
			if reloadSwitchFirmware == 'n':
				remote_conn_pre.close()
			elif reloadSwitchFirmware == 'y':
				remote_conn.send('reload\n')
				remote_conn.send('y')
				remote_conn.send('y')
				remote_conn_pre.close()
			

			# Sleep
			print('Sleeping')
			time.sleep(3)

		else:
			print('*** Connection failed ***')

		# If we reloaded switch wait for reboot and continue firmware update
		
		if reloadSwitchFirmware == 'y':
			time.sleep(60)
			switchBooted = 'no'
			# While loop that will keep trying to connect to the switch until successful
			while switchBooted == 'no':
				# Try connecting to the switch
				print(('Firmware Boot: Attempting to connect to %s' % row[0]))

				connectSuccess = False

				# SSH Stuff

				# Create instance of SSHClient object
				remote_conn_pre = paramiko.SSHClient()

				# Automatically add untrusted hosts
				# (make sure okay for security policy in your environment)
				remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

				try:
					# initiate SSH connection
					remote_conn_pre.connect(
						row[0],
						username=username,
						password=password,
						look_for_keys=False,
						allow_agent=False)
					print(('SSH Connection re-established to %s' % row[0]))
					connectSuccess = True
				except:
					pass
					# Use invoke_shell to establish an 'interactive session'
				
				if connectSuccess is True:
					switchBooted = 'yes'
					remote_conn = remote_conn_pre.invoke_shell()
					print('Interactive SSH session established')
					# Strip the initial router prompt
					output = remote_conn.recv(1000)
					# See what we have
					print((output.decode()))
					remote_conn.send('enable\n')
					time.sleep(1)
					remote_conn.send(secret + '\n')
					time.sleep(1)
					output = remote_conn.recv(1000)
					print((output.decode()))
					print('Clear Buffer')
					
					# Update MAB Settings
					print('***********************************')
					print('Updating MAB settings')
					remote_conn.send('configure\n')
					remote_conn.send('mab request format attribute 1 groupsize 12 separator . uppercase\n')
					remote_conn.send('exit\n')
					remote_conn.send('write\n')
					remote_conn.send('y')
					time.sleep(5)
					output = remote_conn.recv(2000)
					print('##### OUTPUT #####')
					print((output.decode()))
					
					# Update Bootcode
					print('***********************************')
					print('Updating Bootcode')
					remote_conn.send('update bootcode\n')
					remote_conn.send('y')
					time.sleep(20)
					output = remote_conn.recv(2000)
					print('##### OUTPUT #####')
					print((output.decode()))
					
					
					# Reload switch with new boot code
					print('***********************************')
					print('Reloading Switch to new bootcode')
					reloadSwitchBoodcode = 'y'
					remote_conn.send('reload\n')
					remote_conn.send('y')
					remote_conn.send('y')
					time.sleep(10)
					output = remote_conn.recv(2000)
					print('##### OUTPUT #####')
					print((output.decode()))
					remote_conn_pre.close()
					
					
				else:
					print('*** Connection failed ***')
					print('*** Retrying in 10sec ***')
					time.sleep(10)
					
			# Wait for switch to reboot and then verify update. Update CPLD if N2000
			if reloadSwitchBoodcode == 'y':
				time.sleep(60)
				switchBooted = 'no'
				# While loop that will keep trying to connect to the switch until successful
				while switchBooted == 'no':
					# Try connecting to the switch
					print(('BootCode Boot: Attempting to connect to %s' % row[0]))

					connectSuccess = False

					# SSH Stuff

					# Create instance of SSHClient object
					remote_conn_pre = paramiko.SSHClient()

					# Automatically add untrusted hosts
					# (make sure okay for security policy in your environment)
					remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())

					try:
						# initiate SSH connection
						remote_conn_pre.connect(
							row[0],
							username=username,
							password=password,
							look_for_keys=False,
							allow_agent=False)
						print(('SSH Connection re-established to %s' % row[0]))
						connectSuccess = True
					except:
						pass
						# Use invoke_shell to establish an 'interactive session'
					
					if connectSuccess is True:
						switchBooted = 'yes'
						remote_conn = remote_conn_pre.invoke_shell()
						print('Interactive SSH session established')
						# Strip the initial router prompt
						output = remote_conn.recv(1000)
						# See what we have
						print((output.decode()))
						remote_conn.send('enable\n')
						time.sleep(1)
						remote_conn.send(secret + '\n')
						time.sleep(1)
						output = remote_conn.recv(1000)
						print((output.decode()))
						print('Clear Buffer')
						
						
						# Get Switch Series
						remote_conn.send('show version | include "System Model"\n')
						time.sleep(1)
						output = remote_conn.recv(1000)

						version = ''
						output = output.decode()
						outputlines = output.splitlines()
						for i, outputline in enumerate(outputlines):
							if 'N15' in outputline:
								version = 'N1500'
							elif 'N20' in outputline:
								version = 'N2000'

						if version == 'N2000':
							remote_conn.send('show version | include "CPLD Version"\n')
							time.sleep(1)
							output = remote_conn.recv(1000)
							output = output.decode()
							outputlines = output.splitlines()
							for i, outputline in enumerate(outputlines):
								print(outputline)
								if 'CPLD' in outputline:
									if '20' in outputline:
										cpldUpdate = 'n'
									
							
							if cpldUpdate == 'y':
								remote_conn.send('show switch stack-standby\n')
								time.sleep(1)
								output = remote_conn.recv(1000)
								output = output.decode()
								outputlines = output.splitlines()
								doCPLDUpdate = 'n'
								for i, outputline in enumerate(outputlines):
									print(outputline)
									if 'None' in outputline:
										doCPLDUpdate = 'y'
						
								if doCPLDUpdate == 'y':
									print('Updating CPLD')
									remote_conn.send('update cpld\n')
									time.sleep(1)
									output = remote_conn.recv(1000)
									print((output.decode()))
									remote_conn.send('y')
									time.sleep(1)
									output = remote_conn.recv(1000)
									print((output.decode()))
									remote_conn.send('y')
									time.sleep(1)
									output = remote_conn.recv(1000)
									print((output.decode()))
								elif doCPLDUpdate == 'n':
									print('Manual CPLD update needed')
							
									
						
						print('Scritped update complete!')
						remote_conn_pre.close()
										
					else:
						print('*** Connection failed ***')
						print('*** Retrying in 10sec ***')
						time.sleep(10)			
							
		
hostFile.closed

