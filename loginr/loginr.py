# -*- coding: utf-8 -*-

"""loginr logs in to a specific website and tests 
the goodput and round trip time every 30 seconds
"""
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
from twisted.python import log
from twisted.internet import reactor
from twisted.internet import task

REQUEST_DATA_INTERVAL = 30 # Number of seconds between test requests for goodput


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

          The list can also be empty
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

    print ("""Incorrect usage...

You must either run the command 
python loginr.py <username> <password> <domain>

OR set the environment variables
loginr_username, loginr_password and loginr_domain and run the simpler command

python loginr.py
""")
    sys.exit(0)


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


def build_connection_object(follow_redirects=1, 
                            url=None, 
                            headerfunc=None,
                            headers=None):
    """
    Set up a pycurl connection object with the required options
    """
    c = pycurl.Curl()
    c.setopt(pycurl.CONNECTTIMEOUT, 30)
    c.setopt(pycurl.TIMEOUT, 30)
    c.setopt(pycurl.FOLLOWLOCATION, follow_redirects)
    if headerfunc:
        c.setopt(pycurl.HEADERFUNCTION, headerfunc)
    if url:
        c.setopt(pycurl.URL, url)
    if headers:
        c.setopt(pycurl.HTTPHEADER, headers)

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


    connection = build_connection_object(headerfunc=_write_header,
                                         url=credentials["url"] + "login/")

    form_content = get_html_content( connection)
    
    cookie =  'Cookie:_gat=1; _ga=GA1.3.423800644.1462963336; csrftoken=%s;' % csrfs[0] 

    headers = COMMON_HEADERS + ['Accept: */*', 
                                'X-Requested-With: XMLHttpRequest',
                                'Content-Type:application/x-www-form-urlencoded; charset=UTF-8',
                                 cookie ]

    connection1 = build_connection_object(headerfunc=_write_header,
                                          url=credentials["url"] + "login/ajax/",
                                          headers=headers )

    credentials["csrfmiddlewaretoken"] = csrfs[0]

    content = make_form_encoded_post_request(credentials, connection1)

    cookie =  'Cookie:_gat=1; _ga=GA1.3.423800644.1462963336; csrftoken=%s; sessionid=%s; using_auth=cookie' % (csrfs[0]  ,sessionids[0])

    headers2 = COMMON_HEADERS + ['Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                 cookie]

    connection2 = build_connection_object(url=credentials["url"] + "loggedin/",
                                          headers=headers2,
                                          follow_redirects=0 )

    content = get_html_content(connection2)

    cookie =  'Cookie:_gat=1; _ga=GA1.3.423800644.1462963336; csrftoken=%s; sessionid=%s; _next_=root' % (csrfs[0]  ,sessionids[0])
    headers3 = COMMON_HEADERS + ['Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                 cookie]
    connection3 = build_connection_object(url=credentials["url"] ,
                                          headers=headers3 )

    return connection3




class DataCollector(object):
    """Obejct to collect the data about network goodput 

    Attributes:
    ------------
        results: list
           A list of results for all the attempts to download the web page
           in the format [(time_taken_in_seconds, file_size)]
        credentials: dict
           A dictionary of login credentials
        attempts: int 
           Number of times an exception has occured in the current streak
        incorrect_logins: int
           Number of times the connection attempt has not resulted in the right content in a row
        connection:
           pycurl connection object with appropriate login cookies set

    """
    results = []
    credentials = {}
    attempts = 0
    incorrect_logins = 0
    connection = None

    def __init__(self, credentials, blockingcollector):
        """Initialise the DataCollector object

        Parameters:
        -----------
        credentials: dict 
            A dictionary of login credentials
        blockingcollector: BlockingDataCollector
            The holding object (allows threads to call the print output function)
        """
        self.credentials = credentials
        self.blockingcollector = blockingcollector
        self.connection = self.log_on_to_site()

    def log_on_to_site(self):
        """Overridable login function for testing"""
        return log_on_to_site(self.credentials)


    def start(self):
        """Start the twisted looping call to download the web page in a new thread 
        every 30 seconds
        
        Attributes:
        -----------
        _lc: LoopingCall
            The loopingcall object which initialises the calls to _run_html_content_test
        """
        lc = task.LoopingCall(self._run_html_content_test)
        lc.start(REQUEST_DATA_INTERVAL, now=True)

    def get_html_content(self):
        """Overridable html getter for testing"""
        return get_html_content(self.connection)

    def get_connection_stats(self):
        """Given a connection that has just had content requested 
        return the file size and time taken as a tuple
        """
        http_total_time = self.connection.getinfo(pycurl.TOTAL_TIME)
        file_size = self.connection.getinfo(pycurl.SIZE_DOWNLOAD)
        return (http_total_time, file_size)

    def _run_html_content_test(self):
        """Make a request to the URL set in the connection object 
        every REQUEST_DATA_INTERVAL seconds and record the
        results for later calculation of goodput and round trip time"""
        try:
            content = self.get_html_content()
            
            if "Well done you have successfully logged into this app" in content:
                
                self.results.append(self.get_connection_stats())
                self.attempts = 0
                self.incorrect_logins = -1 # set to -1 to say this user has entered correct credentials
            else:
                if self.incorrect_logins > 100:
                    log.err("Exitting due to 100 consecutive incorrect login attempts with no correct ones ever")
                    self.blockingcollector.print_output(None, None)
                elif self.incorrect_logins > -1:
                    #If the user has never logged in correctly since the programme started, bump this number
                    self.incorrect_logins += 1
                self.connection = self.log_on_to_site()

                log.err("Incorrect data retrieved, logging in again", "incorrect_data")
        except:
            self.attempts += 1
            if self.attempts < 10:
                #If this is just a connection error then we will log it and move on
                #In 30 seconds time we will try again
                logging.exception("Error collecting data from URL, retrying on next call")
            else:
                log.err("Exitting due to 10 consecutive exceptions")
                self.blockingcollector.print_output(None, None, out=out)




class BlockingDataCollector(object):
    """
    While the code in DataCollector runs inside the twisted reactor context
    the BlockingDataCollector stays outside of it and can recieve the sigint signal 
    when the user presses ctrl-c

    Attributes:
    -----------
    _dc: DataCollector
        The data collector class used to run the HTTP requests in twisted

    """
    def __init__(self, credentials):
        """Initialise an instance of BlockingDataCollector 

        Parameters: 
        -----------
        credentials: dict
            credentials dictionary as provided by get_login_credentials
        """
        self._dc = DataCollector(credentials, self)
        signal.signal(signal.SIGINT, self.print_output)


    def print_output(self, signal, frame, out=sys.stdout):
        """Print output calculates and prints the results of the goodput and
        rtt test in the format below:

        7 requests were made
        mean goodput 202920.939894 bits per second
        mean rtt 0.176069 seconds
        """
        total_seconds = 0
        total_size = 0
        count = 0
        for result in self._dc.results:
            total_seconds += result[0]
            total_size += result[1]
            count += 1
        
        out.write("\n")
        out.write("%d requests were made" % count)

        if count > 0:  
            rtt_average = total_seconds / float(count)
            total_bits = total_size * 8
            goodput = total_bits / total_seconds
            out.write("mean goodput %f bits per second" % goodput )
            out.write("mean rtt %f seconds" % rtt_average )

        if reactor.running:
            reactor.stop()

    
    def start(self):
        """Start collecting data"""
        results = self._dc.start()
        



if __name__ == '__main__':

    import sys, logging
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    credentials = get_login_credentials(sys.argv[1:])
    dc = BlockingDataCollector(credentials)
    result = dc.start()

    reactor.run()
