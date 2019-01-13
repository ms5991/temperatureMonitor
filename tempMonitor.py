#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time
import Adafruit_MCP9808.MCP9808 as MCP9808
import getopt, smtplib, json, random, sys, os, datetime
from pytz import timezone

def write_log(timestamp, temp_f, temp_c, logFile):
	toLog = '{0},{1:0.1F}*C / {2:0.1F}*F\n'.format(timestamp, temp_c, temp_f)
	
	if os.path.isfile(logFile):
		with open(logFile, "a") as csvFile:
			csvFile.write(toLog)
	else:
		with open(logFile,"w+") as csvFile:
			csvFile.write('Timestamp,Temp_F,Temp_C')
			csvFile.write(toLog)

def send_email(sendToAddress, emailConfigFile, subject, message, verbose):

	# load config data	
	with open(emailConfigFile) as conf:
		if verbose: print 'Loading json email data...'
		emailData = json.load(conf)
	
	# send via gmail (the email address has to be a gmail
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()

	# this is way easier than I expected
	server.login(emailData["username"], emailData["password"])

	# use message headers -- you need a blank line between the subject and the message body
	message = "\r\n".join(["From: {0}".format(emailData["username"]), "To: {0}".format(sendToAddress), "Subject: {0}".format(subject), "\n{0}".format(message)])

	# actually sends it
	server.sendmail(emailData["username"], sendToAddress, message)
	server.quit()

	if verbose: print 'Successfully sent email to {0}'.format(sendToAddress)

# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
	return c * 9.0 / 5.0 + 32.0

def main(argv):
	# OPTIONS EXPLAINATION
	# -l			: prints data to the CSV file with default log file name "/home/pi/temperature_data.csv
	# --log			: prints data to the CSV file with the provided file name
	# --email		: sends an email to the provided address
	# --emailConfig	: file path to the email config file for outgoing email account. Default is ./email_config.json
	# --iterations	: the number of temperature readings to take. Default is 1
	# --seconds		: the number of seconds to wait between readings.  Default is 0
	# --emailAfter	: the number of iterations after which to send an email
	# --finalOnly/-f: if present, sends an email only containing the average, min, and max
	try:
		opts, args = getopt.getopt(sys.argv[1:], "lfv", ["log=","email=","iterations=","seconds=","emailConfig=","finalOnly","emailAfter="])
	except getopt.GetoptError, e:
		print 'tempMonitor.py: {0}'.format(str(e))
		sys.exit(2)

	secondsToWait = 0
	log = False
	logFile = '/home/pi/temperature_data.csv'
	emailConfigFile = 'email_config.json'
	sendToAddress = None
	iterations = 1
	emailIterations = 1
	finalOnly = False
	verbose = False

	for opt, arg in opts:
		if opt == '-v':
			verbose = True
		elif opt == '-l':
			log = True
		elif opt == '--log':
			log = True
			logFile = arg
		elif opt == '--email':
			sendToAddress = arg
		elif opt == '--iterations':
			iterations = int(arg)
		elif opt == '--emailAfter':
			emailIterations = int(arg)
		elif opt == '--seconds':
			secondsToWait = float(arg)
		elif opt == '--emailConfig':
			emailConfigFile = arg
		elif opt in ["-f","--finalOnly"]:
			finalOnly = True

	# get the sensor object
	sensor = MCP9808.MCP9808()

	maxF = -1000
	minF = 1000
	runningSumF = 0
	
	# Initialize communication with the sensor.
	sensor.begin()

	startTime = datetime.datetime.now(timezone('US/Pacific')).strftime("%c")

	for i in range(iterations):
		# wait the allotted time period before next check
		time.sleep(secondsToWait)

		# get temp from sensor
		temp_c = sensor.readTempC()

		# convert to F
		temp_f = c_to_f(temp_c)

		# check if this is max temp
		if temp_f > maxF:
			maxF = temp_f

		# check if this is min temp
		if temp_f < minF:
			minF = temp_f

		# add to running sum for average calc
		runningSumF = runningSumF + temp_f

		result = 'Temperature: {0:0.1F}*C / {1:0.1F}*F'.format(temp_c, temp_f)

		# print result to screen
		if verbose: print result
		
		# time stamp of temp reading
		timestamp = datetime.datetime.now(timezone('US/Pacific')).strftime("%c")

		# write to log file if necessary
		if log: 
			write_log(timestamp, temp_f, temp_c, logFile)

		# send email if address was provided and not only
		if ((not finalOnly) and (sendToAddress is not None) and ((i + 1) % emailIterations == 0)): 
			send_email(sendToAddress, emailConfigFile, "Temperature Reading at {0}".format(timestamp), result, verbose)
	
	# timestamp at end of average period
	endTime = datetime.datetime.now(timezone('US/Pacific')).strftime("%c")

	# calculate average
	averageF = runningSumF / iterations

	# message containing aggregated data
	finalMessage = "Max temp: {0:0.1F}*F\nMin temp: {1:0.1F}*F\nAverage between '{2}' and '{3}': {4:0.1F}*F".format(maxF, minF, startTime, endTime, averageF)

	# print to screen
	print finalMessage

	# send email if necessary
	if (sendToAddress is not None): 
		send_email(sendToAddress, emailConfigFile, "Final results between '{0}' and '{1}'".format(startTime, endTime), finalMessage, verbose)

# call main
if __name__ == "__main__":
	main(sys.argv[1:])
