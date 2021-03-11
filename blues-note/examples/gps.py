"""note-python Raspberry Pi example.

This file contains a complete working sample for using the note-python
library on a Raspberry Pi device.
"""
import sys
import os
import time
import random
import requests

sys.path.insert(0, os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..')))

import notecard   # noqa: E402

# Choose either UART or I2C for Notecard
use_uart = True

if sys.implementation.name != 'cpython':
    raise Exception("Please run this example in a \
                    Raspberry Pi or CPython environment.")

from periphery import I2C  # noqa: E402
from periphery import Serial  # noqa: E402


def NotecardExceptionInfo(exception):
    """Construct a formatted Exception string.

    Args:
        exception (Exception): An exception object.

    Returns:
        string: a summary of the exception with line number and details.
    """
    s1 = '{}'.format(sys.exc_info()[-1].tb_lineno)
    s2 = exception.__class__.__name__
    return "line " + s1 + ": " + s2 + ": " + ' '.join(map(str, exception.args))


def transactionSync(card):
    req = {"req":"hub.sync"}
    callTransaction(card, req, "SYNC")

def transactionSyncStatus(card):
    req = {"req":"hub.sync.status"}
    callTransaction(card, req, "SYNC.STATUS")

def transactionSend(card):
    randNumber = random.randint(0, 11)
    req = {"req":"note.add","body":{"temp": randNumber}}
    callTransaction(card, req, "SEND")


def transactionSet(card):
    req = {"req":"hub.set","product":"io.balena.marc:nbgl500"}
    callTransaction(card, req, "SET")


def transactionTime(card):
    req = {"req": "card.time"}
    callTransaction(card, req, "TIME")

def transactionGPSActivation(card):
    req = {"req": "card.location.mode", "mode": "periodic", "seconds": 10}
    callTransaction(card, req, "GPS")

def transactionGPS(card):
    #req = {"req": "card.location"}
    req = {"req":"card.location.track","start":true,"heartbeat":true,"hours":24}
    callTransaction(card, req, "GPS")

def sleepCM():
    print("About to sleep the CM")
    req = requests.post("http://localhost:1337/sleep/10/60", {"force":1})
    print(r.status_code, r.reason)




def callTransaction(card, req, ope):
    try:
        print(ope)
        print(req)
        rsp = card.Transaction(req)
        print(rsp)

        time.sleep(10)

    except Exception as exception:
        print("Transaction error: " + NotecardExceptionInfo(exception))
        time.sleep(5)


def main():
    """Connect to Notcard and run a transaction test."""
    print("Opening port...")
    try:
        port = I2C("/dev/i2c-1")
    except Exception as exception:
        raise Exception("error opening port: "
                        + NotecardExceptionInfo(exception))

    print("Opening Notecard...")
    try:
        card = notecard.OpenI2C(port, 0, 0)
    except Exception as exception:
        raise Exception("error opening notecard: "
                        + NotecardExceptionInfo(exception))

    # If success, do a transaction loop
    print("Performing Transactions...")
    counter = 0
    while True:
        time.sleep(2)
        print(counter)
        if counter < 1:
            transactionSet(card)
            counter = 1
        else:

            transactionSync(card)
            time.sleep(15)
            transactionGPSActivation(card)
            time.sleep(60)
            transactionGPS(card)
            time.sleep(15)
            transactionSyncStatus(card)
            time.sleep(15)
            sleepCM()

main()
