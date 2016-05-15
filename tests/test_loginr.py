# -*- coding: utf-8 -*-

"""
test_loginr
----------------------------------
Tests for `loginr` module.
"""

import unittest

import mock

import json
import os


from loginr.loginr import DataCollector
from loginr.loginr import BlockingDataCollector
import signal
import pycurl




class TestLoginr(unittest.TestCase):

    def setUp(self):
        self.credentials = None
        pass

    def tearDown(self):
        pass


    def test_get_credentials(self):
        """
        Given that environment variables have been set 
        When I retrieve the login credentials by calling this function with no arguments
        Then there should be a dictionary with username and password strings from the environment variables
        """
        from loginr.loginr import get_login_credentials
        #Make sure dummy variables are set
        with mock.patch.dict("loginr.loginr.os.environ",{"loginr_password": "", 
                                      "loginr_username": "",
                                      "loginr_domain": ""}):
            with self.assertRaises(SystemExit):
                credentials = get_login_credentials([])
        with mock.patch.dict("loginr.loginr.os.environ",{"loginr_password": "foo", 
                                      "loginr_username": "bar",
                                      "loginr_domain": "example.com",}):



            credentials = get_login_credentials([])

            
            self.assertTrue(isinstance(credentials, dict))
            self.assertTrue("username" in credentials)
            self.assertTrue("password" in credentials)
            self.assertTrue("url" in credentials)
            self.assertEquals(credentials["username"], "bar")
            self.assertEquals(credentials["password"], "foo")
            self.assertEquals(credentials["url"], "http://example.com/")

            credentials = get_login_credentials([
                                                 "strets123", 
                                                 "mypassword",
                                                 "test.com"]
                                                 )
            self.assertTrue(isinstance(credentials, dict))
            self.assertTrue("username" in credentials)
            self.assertTrue("password" in credentials)
            self.assertTrue("url" in credentials)
            self.assertEquals(credentials["username"], "strets123")
            self.assertEquals(credentials["password"], "mypassword")
            self.assertEquals(credentials["url"], "http://test.com/")




    def test_get_html_content(self):
        """Given I set a URL on a connection object
        When I call this function
        Then I get back the HTML content as expected """
        from loginr.loginr import build_connection_object
        from loginr.loginr import get_html_content
        import pycurl
        connection = build_connection_object()
        connection.setopt(pycurl.URL, "http://example.com")
        content = get_html_content(connection)
        self.assertTrue("illustrative examples" in content)



    def test_make_form_encoded_post_request(self):
        """Given a url for an echo server 
        When I POST data with the appropriate credentials 
        Then I get back my form encoded data as a JSON"""
        from loginr.loginr import build_connection_object
        from loginr.loginr import make_form_encoded_post_request
        import pycurl
        credentials = {
            "username" : "foo",
            "password" : "bar",
            "csrfmiddlewaretoken" : "test_token"
        }
        connection = build_connection_object()
        connection.setopt(pycurl.URL, "http://httpbin.org/post")
        content = make_form_encoded_post_request(credentials, connection)
        dict_from_echo_server = json.loads(content)
        self.assertEquals(credentials, dict_from_echo_server["form"])





    def test_log_on_to_site(self):
        """Given the test site has environment variables set for 
        the login credentials
        When I log in
        I get back a pycurl connection object capable of being used to get the main site"""
        try:
            from loginr.loginr import get_login_credentials
            from loginr.loginr import log_on_to_site
            from loginr.loginr import get_html_content
            credentials = get_login_credentials([])
            connection = log_on_to_site(credentials)
            content = get_html_content(connection)
            self.assertTrue("Well done you have successfully logged into this app" in content)
        except SystemExit:
            raise Exception("not possible to run the test as login details for site not set")






    @mock.patch("loginr.loginr.log_on_to_site")
    @mock.patch("loginr.loginr.get_connection_stats")
    @mock.patch("loginr.loginr.get_html_content")
    def test__run_http_test(self, get_html_content, get_connection_stats, log_on_to_site):
        """Given a method that returns no HTML
        When I call this function
        Then incorrect logins count will be increased"""
        get_connection_stats.return_value = (1,1)
        get_html_content.return_value = ""

        m =  BlockingDataCollector({})
        dc = DataCollector({}, m)
        log_on_to_site.return_value = None

        dc._run_html_content_test()
        self.assertEquals(dc.results, [])
        self.assertEquals(dc.incorrect_logins, 1)

        get_html_content.return_value = """
<html>
    <head>
        <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" rel="stylesheet" />
        <script src="https://code.jquery.com/jquery-2.2.1.min.js"></script>
        <style>
        #form_response {
            color: f00;
        }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row">

            
    <h3>Well done you have successfully logged into this app</h3>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin pellentesque risus quis ipsum malesuada tristique. Suspendisse aliquet velit eu mi maximus venenatis. Cras finibus est hendrerit volutpat euismod. Praesent eget massa sagittis, consectetur nibh nec, pulvinar ipsum. Aliquam erat volutpat. In luctus ut purus sit amet accumsan. Nunc sit amet velit augue. F"""

        m =  BlockingDataCollector({})
        dc = DataCollector({}, m)
        log_on_to_site.return_value = None

        dc._run_html_content_test()

        self.assertEquals(dc.results, [(1,1)])
        



    @mock.patch("loginr.loginr.log_on_to_site")
    @mock.patch("loginr.loginr.get_connection_stats")
    @mock.patch("loginr.loginr.get_html_content")
    def test_print_output(self,  get_html_content, get_connection_stats, log_on_to_site):
        """Given I create an instance of BlockingDataCollector
        When I add some results (1 byte file downloaded in 1 second)
        Then the printed output should contain this data
        """
        get_connection_stats.return_value = (1,1)
        get_html_content.return_value = ""
        log_on_to_site.return_value = None
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO
        out = StringIO()
        bc = BlockingDataCollector(None)
        bc._dc.results = [(1,1)]
        bc.print_output(None, None, out=out)
        output = out.getvalue().strip()
        self.assertEquals(output, '1 requests were mademean goodput 8.000000 bits per secondmean rtt 1.000000 seconds')



    @mock.patch("loginr.loginr.log_on_to_site")
    @mock.patch("loginr.loginr.get_connection_stats")
    @mock.patch("loginr.loginr.get_html_content")
    def test_print_output_empty(self,  get_html_content, get_connection_stats, log_on_to_site):
        """
        Given I create an instance of BlockingDataCollector
        When I add no results
        Then the printed output should only contain count 0"""
        get_connection_stats.return_value = (1,1)
        get_html_content.return_value = ""
        log_on_to_site.return_value = None
        try:
            from StringIO import StringIO
        except ImportError:
            from io import StringIO
        out = StringIO()
        bc = BlockingDataCollector(None)
        bc._dc.results = []
        bc.print_output(None, None, out=out)
        output = out.getvalue().strip()
        self.assertEquals(output, '0 requests were made')
