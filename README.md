# temperatureMonitor

Simple Python script to monitor the temperature using Adafruit's MCP9808 I2C sensor and associated Python library.

Assumes that a Raspberry Pi is connected via I2C to the MCP9808 with I2C address 0x18 (see below for I2C detect output).

## Setup

Follow instructions [here](https://github.com/adafruit/Adafruit_Python_MCP9808) to install required Python library for the sensor itself.

Set up a Gmail account from which the data will be sent.  This doesn't need to be the account that you receive data from.  Put the account
username and password into sample_email_config.json (or another json file, you can pass it as a command line argument).

Make sure you've run:

    sudo pip install pytz

To install the timezone libraries.  You can alter the timezone in the source code to fit your needs.

### I2C setup

This is the result from `sudo i2cdetect -y 1` on the Raspberry Pi connected to the MCP9808:

         0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:          -- -- -- -- -- -- -- -- -- -- -- -- --
    10: -- -- -- -- -- -- -- -- 18 -- -- -- -- -- -- --
    20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
    70: -- -- -- -- -- -- -- --

##  Usage
### Options Explanation
`-v`                    : use verbose mode, printing every reading to the screen
`-l`                    : prints data to the CSV file with default log file name "/home/pi/temperature_data.csv
`--log`                 : prints data to the CSV file with the provided file name
`--email`               : sends an email to the provided address
`--emailConfig`         : file path to the email config file for outgoing email account. Default is ./email_config.json
`--iterations`          : the number of temperature readings to take. Default is 1
`--seconds`             : the number of seconds to wait between readings.  Default is 0
`--emailAfter`          : the number of iterations after which to send an email
`--finalOnly` or `-f`   : if present, sends an email only containing the average, min, and max

## Example

Running:

    python tempMonitor.py

Will take one temperature reading and print it to the screen

Running:

    python tempMonitor.py --log ./results.csv --iterations 360 --seconds 10 --email YOUR_EMAIL@gmail.com --emailConfig ../email_config.json --emailAfter 20 -v

Will take a measurement every 10 seconds for 3600 seconds (one hour), sending every 20th reading to YOUR_EMAIL@gmail.com in addition to the final
email containing average, max, and min temps.  The sending email address is defined in `../email_config.json`  It will print to the log file `./results.csv` as
well as the screen.

Note that you can specify fractions of seconds like `0.5`, but accuracy of calculated times using `iterations*seconds` deteriorates as the amount of time decreases.
