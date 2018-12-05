import paramiko
import time
import csv
import getpass
# import sys

username = 'admin'
password = getpass.getpass(prompt='Switch Admin password: ')
secret = getpass.getpass(prompt='Switch enable password: ')

with open('dellSwitches.csv', 'r') as hostFile:
	hosts = csv.reader(hostFile)
	# Skips header row of csv
	next(hosts)

	for row in hosts:
		# main loop

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
			remote_conn.send("enable\n")
			remote_conn.send(secret + '\n')
			remote_conn.send('write\n')
			remote_conn.send('y')
			time.sleep(1)
			output = remote_conn.recv(1000)
			print((output.decode()))
			remote_conn.send('exit\n')
			time.sleep(1)
			output = remote_conn.recv(1000)
			print((output.decode()))
			
			# Close SSH connection
			remote_conn_pre.close()

		else:
			print('*** Connection failed ***')

hostFile.closed

# Write config of core switches

with open('coreSwitches.csv', 'r') as hostFile:
	hosts = csv.reader(hostFile)
	# Skips header row of csv
	next(hosts)

	for row in hosts:
		# main loop

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
			remote_conn.send('write\n')
			time.sleep(5)
			output = remote_conn.recv(1000)
			print((output.decode()))
			
			# Close SSH connection
			remote_conn_pre.close()

		else:
			print('*** Connection failed ***')

hostFile.closed

# Write config of the server top of rack switches

with open('serverSwitches.csv', 'r') as hostFile:
	hosts = csv.reader(hostFile)
	# Skips header row of csv
	next(hosts)

	for row in hosts:
		# main loop

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
			remote_conn.send("enable\n")
			remote_conn.send(secret + '\n')
			remote_conn.send('write\n')
			remote_conn.send('y')
			time.sleep(1)
			output = remote_conn.recv(1000)
			print((output.decode()))
			remote_conn.send('exit\n')
			time.sleep(1)
			output = remote_conn.recv(1000)
			print((output.decode()))
			
			# Close SSH connection
			remote_conn_pre.close()

		else:
			print('*** Connection failed ***')

hostFile.closed
