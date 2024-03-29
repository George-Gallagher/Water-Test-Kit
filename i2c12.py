#!/usr/bin/python

import io         # used to create file streams
from io import open
import fcntl      # used to access I2C parameters like addresses

import time       # used for sleep delay and timestamps
import string     # helps parse strings
import socket, pickle

import RPi.GPIO as GPIO

class AtlasI2C:
	long_timeout = 1.5         	# the timeout needed to query readings and calibrations
	short_timeout = .5         	# timeout for regular commands
	default_bus = 1         	# the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
	default_address = 98     	# the default address for the sensor
	current_addr = default_address

	def __init__(self, address=default_address, bus=default_bus):
		# open two file streams, one for reading and one for writing
		# the specific I2C channel is selected with bus
		# it is usually 1, except for older revisions where its 0
		# wb and rb indicate binary read and write
		self.file_read = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
		self.file_write = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)

		# initializes I2C to either a user specified or default address
		self.set_i2c_address(address)

	def set_i2c_address(self, addr):
		# set the I2C communications to the slave specified by the address
		# The commands for I2C dev using the ioctl functions are specified in
		# the i2c-dev.h file from i2c-tools
		I2C_SLAVE = 0x703
		fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
		fcntl.ioctl(self.file_write, I2C_SLAVE, addr)
		self.current_addr = addr

	def write(self, cmd):
		# appends the null character and sends the string over I2C
		cmd += "\00"
		self.file_write.write(cmd.encode('latin-1'))

	def read(self, num_of_bytes=31):
		# reads a specified number of bytes from I2C, then parses and displays the result
		res = self.file_read.read(num_of_bytes)         # read from the board
		if type(res[0]) is str:					# if python2 read
			response = [i for i in res if i != '\x00']
			if ord(response[0]) == 1:             # if the response isn't an error
				# change MSB to 0 for all received characters except the first and get a list of characters
				# NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
				char_list = list(map(lambda x: chr(ord(x) & ~0x80), list(response[1:])))
				return float(''.join(char_list))     # convert the char list to a string and returns it
			else:
				return "Error " + str(ord(response[0]))
				
		else:									# if python3 read
			if res[0] == 1: 
				# change MSB to 0 for all received characters except the first and get a list of characters
				# NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
				char_list = list(map(lambda x: chr(x & ~0x80), list(res[1:])))
				return float(''.join(char_list))     # convert the char list to a string and returns it
			else:
				return "Error " + str(res[0])

	def query(self, string):
		# write a command to the board, wait the correct timeout, and read the response
		self.write(string)

		# the read and calibration commands require a longer timeout
		if((string.upper().startswith("R")) or
			(string.upper().startswith("CAL"))):
			time.sleep(self.long_timeout)
		elif string.upper().startswith("SLEEP"):
			return "sleep mode"
		else:
			time.sleep(self.short_timeout)

		return self.read()

	def close(self):
		self.file_read.close()
		self.file_write.close()

	def list_i2c_devices(self):
		prev_addr = self.current_addr # save the current address so we can restore it after
		i2c_devices = []
		for i in range (0,128):
			try:
				self.set_i2c_address(i)
				self.read(1)
				i2c_devices.append(i)
			except IOError:
				pass
		self.set_i2c_address(prev_addr) # restore the address we were using
		return i2c_devices

		
def main():
	device = AtlasI2C() 	# creates the I2C port object, specify the address or bus if necessary
	
	real_raw_input = vars(__builtins__).get('raw_input', input)
	
	# main loop
	while True:
		arr=[]
		user_cmd = "R,97"
		addr = int(user_cmd.split(',')[1])
		device.set_i2c_address(addr)
		print("I2C address set to " + str(addr))

		# continuous polling command automatically polls the board
		
		if user_cmd.upper().startswith("POLL"):
			delaytime = float(string.split(user_cmd, ',')[1])

			# check for polling time being too short, change it to the minimum timeout if too short
			if delaytime < AtlasI2C.long_timeout:
				print("Polling time is shorter than timeout, setting polling time to %0.2f" % AtlasI2C.long_timeout)
				delaytime = AtlasI2C.long_timeout

			# get the information of the board you're polling
			info = string.split(device.query("I"), ",")[1]
			print("Polling %s sensor every %0.2f seconds, press ctrl-c to stop polling" % (info, delaytime))
			print(device.query("R"))
			time.sleep(delaytime - AtlasI2C.long_timeout)

		# if not a special keyword, pass commands straight to board
		else:
			if len(user_cmd) == 0:
				print( "Please input valid command.")
			else:
				try:
					arr.append(device.query(user_cmd))
					print(device.query(user_cmd))
				except IOError:
					print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")
		user_cmd = "R,98"
                addr = int(user_cmd.split(',')[1])
                device.set_i2c_address(addr)
                print("I2C address set to " + str(addr))
		if user_cmd.upper().startswith("POLL"):
                        delaytime = float(string.split(user_cmd, ',')[1])

                        # check for polling time being too short, change it to the minimum timeout if too short
                        if delaytime < AtlasI2C.long_timeout:
                                print("Polling time is shorter than timeout, setting polling time to %0.2f" % AtlasI2C.long_timeout)
                                delaytime = AtlasI2C.long_timeout

                        # get the information of the board you're polling
                        info = string.split(device.query("I"), ",")[1]
                        print("Polling %s sensor every %0.2f seconds, press ctrl-c to stop polling" % (info, delaytime))
                        print(device.query("R"))
                        time.sleep(delaytime - AtlasI2C.long_timeout)

                # if not a special keyword, pass commands straight to board
                else:
                        if len(user_cmd) == 0:
                                print( "Please input valid command.")
                        else:
                                try:
					arr.append(device.query(user_cmd))
                                        print(device.query(user_cmd))
                                except IOError:
                                        print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")
		user_cmd = "R,99"
                addr = int(user_cmd.split(',')[1])
                device.set_i2c_address(addr)
                print("I2C address set to " + str(addr))
		if user_cmd.upper().startswith("POLL"):
                        delaytime = float(string.split(user_cmd, ',')[1])

                        # check for polling time being too short, change it to the minimum timeout if too short
                        if delaytime < AtlasI2C.long_timeout:
                                print("Polling time is shorter than timeout, setting polling time to %0.2f" % AtlasI2C.long_timeout)
                                delaytime = AtlasI2C.long_timeout

                        # get the information of the board you're polling
                        info = string.split(device.query("I"), ",")[1]
                        print("Polling %s sensor every %0.2f seconds, press ctrl-c to stop polling" % (info, delaytime))
                        print(device.query("R"))
                        time.sleep(delaytime - AtlasI2C.long_timeout)

                # if not a special keyword, pass commands straight to board
                else:
                        if len(user_cmd) == 0:
                                print( "Please input valid command.")
                        else:
                                try:
					arr.append(device.query(user_cmd))
                                        print(device.query(user_cmd))
                                except IOError:
                                        print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")
 
                user_cmd = "R,100"
                addr = int(user_cmd.split(',')[1])
                device.set_i2c_address(addr)
                print("I2C address set to " + str(addr))
                if user_cmd.upper().startswith("POLL"):
                        delaytime = float(string.split(user_cmd, ',')[1])

                        # check for polling time being too short, change it to the minimum timeout if too short
                        if delaytime < AtlasI2C.long_timeout:
                                print("Polling time is shorter than timeout, setting polling time to %0.2f" % AtlasI2C.long_timeout)
                                delaytime = AtlasI2C.long_timeout

                        # get the information of the board you're polling
                        info = string.split(device.query("I"), ",")[1]
                        print("Polling %s sensor every %0.2f seconds, press ctrl-c to stop polling" % (info, delaytime))
                        print(device.query("R"))
                        time.sleep(delaytime - AtlasI2C.long_timeout)

                # if not a special keyword, pass commands straight to board
                else:
                        if len(user_cmd) == 0:
                                print( "Please input valid command.")
                        else:
                                try:
					arr.append(device.query(user_cmd))
                                        print(device.query(user_cmd))
                                except IOError:
                                        print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")

                user_cmd = "R,102"
                addr = int(user_cmd.split(',')[1])
                device.set_i2c_address(addr)
                print("I2C address set to " + str(addr))
                if user_cmd.upper().startswith("POLL"):
                	delaytime = float(string.split(user_cmd, ',')[1])

			if delaytime < AtlasI2C.long_timeout:
				print("Polling time is shorter than timeout, setting polling time to %0.2f" % AtlasI2C.long_timeout)
				delaytime = AtlasI2C.long_timeout

			info = string.split(device.query("I"), ",")[1]
			print("Polling %s sensor every %0.2f seconds, press ctrl-c to stop polling" % (info, delaytime))
			print(device.query("R"))
			time.sleep(delaytime - AtlasI2C.long_timeout)

		else:
			if len(user_cmd) == 0:
				print( "Please input valid command.")
			else:
				try:
					arr.append(device.query(user_cmd))
					print(device.query(user_cmd))
				except IOError:
					print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")

                user_cmd = "R,104"
                addr = int(user_cmd.split(',')[1])
                device.set_i2c_address(addr)
                print("I2C address set to " + str(addr))
                if user_cmd.upper().startswith("POLL"):
                        delaytime = float(string.split(user_cmd, ',')[1])

                        # check for polling time being too short, change it to the minimum timeout if too short
                        if delaytime < AtlasI2C.long_timeout:
                                print("Polling time is shorter than timeout, setting polling time to %0.2f" % AtlasI2C.long_timeout)
                                delaytime = AtlasI2C.long_timeout

                        # get the information of the board you're polling
                        info = string.split(device.query("I"), ",")[1]
                        print("Polling %s sensor every %0.2f seconds, press ctrl-c to stop polling" % (info, delaytime))
                        print(device.query("R"))
                        time.sleep(delaytime - AtlasI2C.long_timeout)

                # if not a special keyword, pass commands straight to board
                else:
                        if len(user_cmd) == 0:
                                print( "Please input valid command.")
                        else:
                                try:
					arr.append(device.query(user_cmd))
                                        print(device.query(user_cmd))

                                except IOError:
                                        print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")
		HOST = 'localhost'
		PORT = 50007
		p = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		p.connect((HOST, PORT))
		p.send('I am client')
		from_server = float(p.recv(4096))
		p.close
		arr.append(from_server)

		GPIO.setmode(GPIO.BCM)
		INPUT_PIN = 4
		GPIO.setup(INPUT_PIN, GPIO.IN)

		if (GPIO.input(INPUT_PIN) == True):
			arr.append(3.3)
		else:
			arr.append(0.0)
 
		print(arr)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('192.168.1.4', 3999))
                data_string = pickle.dumps(arr)
                s.send(data_string)

                data = s.recv(4096)
                data_arr = pickle.loads(data)
                s.close()
                print ('Received', repr(data_arr))


if __name__ == '__main__':
	main()
