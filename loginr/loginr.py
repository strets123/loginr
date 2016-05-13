
import argparse
import os
from StringIO import StringIO    
import pycurl
import re
try:
    # python 3
    from urllib.parse import urlencode
except ImportError:
    # python 2
    from urllib import urlencode
import signal
import sys
from twisted.internet.task import LoopingCall
from crochet import wait_for, run_in_reactor, setup
setup()


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from twisted.python import log


import fileinput

def create_parser():
    """Returns an approriate argument parser for this tool"""
    parser = argparse.ArgumentParser()
    parser.add_argument("username")
    parser.add_argument("password")
    parser.add_argument("domain")
    return parser




def get_login_credentials(args):
    """
    Testable function to parse the arguments given 
    to this module. 
    Parameters:
    -----------
        args : list
          a list of arguments in the format representing the 
          username password and domain
          ["strets123",  "mypassword", "test.com"]
    """
    username = os.environ.get("loginr_username", None)
    password = os.environ.get("loginr_password", None)
    domain = os.environ.get("loginr_domain", None)
    if len(args) == 3:
        args = create_parser().parse_args(args)
        return { "username" : args.username, 
                 "password" : args.password,
                 "domain": args.domain,
                 "url" : "http://%s/" % args.domain }
    elif username and password and domain:
        return { "username" : username, 
                 "password" : password,
                 "domain" :  domain,
                 "url" : "http://%s/" % domain }

    return None

def get_html_content(connection):
    """
    Given a pycurl connection object perform 
    a request and return the contents of the login page 

    Parameters:
    -----------
        credentials : dict
            A dictionary of site credentials, in this case only 
            the url is required for example: { "url" : "http://example.com" }
        connection : pycurl.Curl
            A pycurl connection object

    """
    storage = StringIO()
    connection.setopt(connection.WRITEFUNCTION, storage.write)
    connection.perform()
    html_content = storage.getvalue()
    return html_content


def build_connection_object( writable_cookies=False):
    """
    Set up a pycurl connection object with the required options
    """
    c = pycurl.Curl()
    c.setopt(pycurl.CONNECTTIMEOUT, 30)
    c.setopt(pycurl.TIMEOUT, 30)
    c.setopt(pycurl.FOLLOWLOCATION, 1)

    c.setopt(pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36")

    return c

def make_form_encoded_post_request(credentials, connection):
    """Send a POST request as form encoded data with the connection object provided

    Parameters:
    -----------
        credentials : dict
            A dictionary of site credentials - the 
            usename, 
            password and 
            csrfmiddlewaretoken
        connection : pycurl.Curl
            A pycurl connection object with the URL set

    """
    fields_to_keep = ("username", "password", "csrfmiddlewaretoken")
    params = { key: credentials[key] for key in fields_to_keep }
    
    postfields = urlencode(params)

    connection.setopt(connection.POSTFIELDS, postfields)
    return get_html_content(connection)






def log_on_to_site(credentials):
    """
    Log on to the site

    Parameters:
    -----------
        credentials : dict
            A dictionary of site credentials - the url (minus the /login), 
            usename, 
            password
    """
    COMMON_HEADERS = ['Accept-Encoding:gzip, deflate',
                  'Host: %s' % credentials["domain"],
                  'Origin:http://%s' % credentials["domain"], 
                  'Referer:http://%s/login/' % credentials["domain"],
                  'User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
                  'Connection:keep-alive',]

    csrfs = []
    sessionids = []

    # closure to capture Set-Cookie
    def _write_header(header):
        match = re.match("^Set-Cookie: csrftoken=(\w+);", header)

        if match:
            csrfs.append(match.group(1))

        match2 = re.match("^Set-Cookie: sessionid=(\w+);", header)
        if match2:
            sessionids.append(match2.group(1))



    connection = build_connection_object(writable_cookies=True)
    connection.setopt(pycurl.HEADERFUNCTION, _write_header)

    connection.setopt(connection.URL, credentials["url"] + "login/" )
    form_content = get_html_content( connection)
    
    cookie =  'Cookie:_gat=1; _ga=GA1.3.423800644.1462963336; csrftoken=%s;' % csrfs[0] 

    headers = COMMON_HEADERS + ['Accept: */*', 
                                'X-Requested-With: XMLHttpRequest',
                                'Content-Type:application/x-www-form-urlencoded; charset=UTF-8',
                                 cookie ]

    connection1 = connection
    connection1.setopt(pycurl.HTTPHEADER, headers)
    connection1.setopt(pycurl.HEADERFUNCTION, _write_header)
    connection1.setopt(connection.URL, credentials["url"] + "login/ajax/" )
    credentials["csrfmiddlewaretoken"] = csrfs[0]

    content = make_form_encoded_post_request(credentials, connection1)

    connection2 = connection1
    cookie =  'Cookie:_gat=1; _ga=GA1.3.423800644.1462963336; csrftoken=%s; sessionid=%s; using_auth=cookie' % (csrfs[0]  ,sessionids[0])

    headers2 = COMMON_HEADERS + ['Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                 cookie]
    connection2.setopt(pycurl.HTTPHEADER, headers2)
    connection2.setopt(pycurl.POSTFIELDS, "")
    connection2.setopt(pycurl.POST, 0)

    connection2.setopt(connection.URL, credentials["url"] + "loggedin/" )

    connection2.setopt(pycurl.FOLLOWLOCATION, 0)

    content = get_html_content(connection2)

    connection3 = build_connection_object(writable_cookies=False)
    cookie =  'Cookie:_gat=1; _ga=GA1.3.423800644.1462963336; csrftoken=%s; sessionid=%s; _next_=root' % (csrfs[0]  ,sessionids[0])
    headers3 = COMMON_HEADERS + ['Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                 cookie]

    connection3.setopt(pycurl.HTTPHEADER, headers3)

    connection3.setopt(connection.URL, credentials["url"])
    connection3.setopt(pycurl.FOLLOWLOCATION, 1)

    return connection3


    
def periodic_task_crashed(reason):
    log.err(reason, "periodic_task broken")




class _DataCollector(object):
    results = []
    credentials = {}
    def __init__(self, credentials, connection):
        self.credentials = credentials
        self.connection = connection
        
    def start(self):
        self._lc = LoopingCall(self.test_download)
        
        result = self._lc.start(1, now=True)
        result.addErrback(periodic_task_crashed)
        

    def test_download(self):
        content = get_html_content(self.connection)
        if "id='auth'" in content:
            err("There has been an error logging in")
            self.connection = log_on_to_site(self.credentials)
        else:
            http_total_time = connection.getinfo(pycurl.TOTAL_TIME)
            file_size = connection.getinfo(pycurl.SIZE_DOWNLOAD)
            self.results.append((http_total_time, file_size))


            



class BlockingDataCollector(object):
    def __init__(self, credentials, connection):
        self._dc = _DataCollector(credentials, connection)
        signal.signal(signal.SIGINT, self.print_output)

    def print_output(self, signal, frame):
        
        total_seconds = 0
        count = 0
        for result in self._dc.results:
            if result[1] == 4466.0:
                
                total_seconds += result[0]
                count += 1
        print self._dc.results
        print count
        print total_seconds
        rtt_average = total_seconds / float(count)

        total_bits = float(count) * 4466.0 * 8
        goodput = total_bits / total_seconds

        print "mean goodput %f" % goodput 
        print "mean rtt %f" % rtt_average 

    @run_in_reactor
    def start(self):
        results = self._dc.start()



if __name__ == '__main__':

    credentials = get_login_credentials(sys.argv[1:])
    
    connection = log_on_to_site(credentials)
    
    dc = BlockingDataCollector(credentials, connection)
    result = dc.start()

    signal.pause()

        # Something else happened:
        #log.error(result.original_failure().getTraceback())
    