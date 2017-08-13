import logging
import subprocess
import httplib
import urllib

LOGGER = logging.getLogger(name=None)
LOGGER.setLevel(logging.INFO)

PO_ENDPOINT = "/1/messages.json"
PO_APP_TOKEN = " "
PO_USER_KEY = " "

try:
    LOGGER.info('Opening HTTPS connection to api.pushover.net...')
    PO_API = httplib.HTTPSConnection("api.pushover.net:443")
except Exception as e:
    LOGGER.error('Could not connecto to Pushover: ' + e)

ARRAYS = ["/dev/md0"]


for array in ARRAYS:
    LOGGER.info('Cheking array ' + array)
    cmd = "/sbin/mdadm --detail " + array + \
        " | awk '/Failed Devices : / {print $4;}'"
    check = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    failed_drives, err = check.communicate()
    LOGGER.info('Found ' + failed_drives + ' failed drives, sending Pushover msg')

    if int(failed_drives) != 0:
        PO_API.request("POST", PO_ENDPOINT,
                       urllib.urlencode({
                           "token": PO_APP_TOKEN,
                           "user": PO_USER_KEY,
                           "priority": "1",
                           "message": str(failed_drives) + " failed drives in " + array,
                       }), {"Content-type": "application/x-www-form-urlencoded"})
        response = PO_API.getresponse()
        PO_API.close()
    elif int(failed_drives) == 0:
        PO_API.request("POST", PO_ENDPOINT,
                       urllib.urlencode({
                           "token": PO_APP_TOKEN,
                           "user": PO_USER_KEY,
                           "priority": "-1",
                           "message": "All good, " + str(failed_drives) + \
                           " failed drives in " + array,
                       }), {"Content-type": "application/x-www-form-urlencoded"})
        response = PO_API.getresponse()
        PO_API.close()
