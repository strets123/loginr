# -*- coding: utf-8 -*-

"""
test_loginr
----------------------------------
Tests for `loginr` module.
"""

import unittest


import json
import os

class TestLoginr(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass



    def test_get_credentials_empty_args(self):
        """
        Given that environment variables have been set 
        When I retrieve the login credentials by calling this function with no arguments
        Then there should be a dictionary with username and password strings from the environment variables
        """
        from loginr.loginr import get_login_credentials
        current_pass = os.environ.get("loginr_password", "")
        current_user = os.environ.get("loginr_username", "")
        current_url = os.environ.get("loginr_domain", "")
        #Make sure dummy variables are set
        os.environ["loginr_password"] = "foo"
        os.environ["loginr_username"] = "bar"
        os.environ["loginr_domain"] = "example.com"
        credentials = get_login_credentials([])
        self.assertTrue(isinstance(credentials, dict))
        self.assertTrue("username" in credentials)
        self.assertTrue("password" in credentials)
        self.assertTrue("url" in credentials)
        self.assertEquals(credentials["username"], "bar")
        self.assertEquals(credentials["password"], "foo")
        self.assertEquals(credentials["url"], "http://example.com/")
        #reset the values
        os.environ["loginr_password"] = current_pass
        os.environ["loginr_username"] = current_user
        os.environ["loginr_domain"] = current_url


    def test_get_credentials_with_args(self):
        """
        Given that environment variables have been set 
        When I retrieve the login credentials by calling this function with no arguments
        Then there should be a dictionary with username and password strings from the environment variables
        """
        from loginr.loginr import get_login_credentials
        current_pass = os.environ.get("loginr_password", "")
        current_user = os.environ.get("loginr_username", "")
        current_url = os.environ.get("loginr_domain", "")
        #Make sure dummy variables are set
        os.environ["loginr_password"] = "foo"
        os.environ["loginr_username"] = "bar"
        os.environ["loginr_domain"] = "example.com"
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
        #reset the values
        os.environ["loginr_password"] = current_pass
        os.environ["loginr_username"] = current_user
        os.environ["loginr_domain"] = current_url




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
        from loginr.loginr import get_login_credentials
        from loginr.loginr import log_on_to_site
        from loginr.loginr import get_html_content
        credentials = get_login_credentials([])
        connection = log_on_to_site(credentials)
        content = get_html_content(connection)
        self.assertTrue("Well done you have successfully logged into this app" in content)





class TestDataCollector(unittest.TestCase):

    def setUp(self):
        from mocks import MockBlockingDataCollector
        self.credentials = None
        self.connection = None
        self.blocking = MockBlockingDataCollector(self.credentials)


    def tearDown(self):
        pass


    def test__run_http_test(self):
        """Given a method that returns some of the correct HTML
        When I call this function
        Then the mocked result will be passed to the result list"""
        from mocks import DataCollectorMockCorrectContent
        from StringIO import StringIO
        out = StringIO()
        dc = DataCollectorMockCorrectContent(self.credentials, 
                                              self.blocking)

        dc._run_html_content_test()
        
        self.assertEquals(dc.results, [(1,1)])

    def test__run_http_test_incorrect_content(self):
        """Given some incorrect content for the login page
        When I call this function
        My incorrect login count is increased by 1
        """
        from mocks import DataCollectorMockInCorrectContent
        dc = DataCollectorMockInCorrectContent(self.credentials, 
                                              self.blocking)
        dc._run_html_content_test()
        
        self.assertEquals(dc.incorrect_logins, 1)


class TestBlockingDataCollector(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_print_output(self):
        """Given I create an instance of BlockingDataCollector
        When I add some results (1 byte file downloaded in 1 second)
        Then the printed output should contain this data"""
        from StringIO import StringIO
        from mocks import MockBlockingDataCollector
        out = StringIO()
        bc = MockBlockingDataCollector(None)
        bc._dc.results = [(1,1)]
        bc.print_output(None, None, out=out)
        output = out.getvalue().strip()
        self.assertEquals(output, '1 requests were mademean goodput 8.000000 bits per secondmean rtt 1.000000 seconds')


    def test_print_output_empty(self):
        """Given I create an instance of BlockingDataCollector
        When I add no results
        Then the printed output should only contain count 0"""
        from StringIO import StringIO
        out = StringIO()
        from mocks import MockBlockingDataCollector
        bc = MockBlockingDataCollector(None)
        bc.print_output(None, None, out=out)
        output = out.getvalue().strip()
        self.assertEquals(output, '0 requests were made')


