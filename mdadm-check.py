#!/usr/bin/env python
import argparse
import logging
import subprocess
import httplib
import urllib

logging.basicConfig()
LOGGER = logging.getLogger('logger')
LOGGER.setLevel(logging.INFO)

PO_MSG_ENDPOINT = "/1/messages.json"


def mdadm_check(args):
    for array in args.arrays:
        LOGGER.info('Checking array ' + array)
        cmd = "/sbin/mdadm --detail " + array + " | awk '/Failed Devices : / {print $4;}'"
        check = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        failed_drives, err = check.communicate()
        LOGGER.info('Found ' + failed_drives + ' failed drives, sending Pushover msg')

        if int(failed_drives) != 0:
            priority = 1
            message = "CRITICAL: There are {} failed drives in {}".format(failed_drives, array)
            post_to_pushover(args.token, args.key, str(priority), message)
        elif int(failed_drives) == 0:
            priority = -1
            message = "INFO: There are {} failed drives in {}".format(failed_drives, array)
            post_to_pushover(args.token, args.key, str(priority), message)


def post_to_pushover(token, key, priority, msg):
    try:
        LOGGER.info('Opening HTTPS connection to api.pushover.net...')
        po_api = httplib.HTTPSConnection("api.pushover.net:443")
        po_api.request("POST", PO_MSG_ENDPOINT,
                       urllib.urlencode({
                           "token": token,
                           "user": key,
                           "priority": priority,
                           "message": msg,
                       }), {"Content-type": "application/x-www-form-urlencoded"})
        response = po_api.getresponse()
        LOGGER.info("{}: {}".format(response.status, response.reason))
        po_api.close()
    except Exception as ex:
        LOGGER.error('Could not connecto to Pushover: ' + str(ex))


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='Simple software RAID health check tool using mdadm and Pushover.')
    PARSER.add_argument('-a', '--array', dest='arrays', action='append', help='RAID array i.e /dev/md0', required=True)
    PARSER.add_argument('-t', '--token', dest='token', help='Pushover App Token', required=True)
    PARSER.add_argument('-k', '--key', dest='key', help='Pushover User Key', required=True)
    ARGS = PARSER.parse_args()
    mdadm_check(ARGS)
