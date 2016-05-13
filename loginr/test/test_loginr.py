#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

----------------------------------
Tests for `loginr` module.
"""

import unittest

from loginr.loginr import *

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
        self.assertEquals(credentials["url"], "http://example.com")
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
        self.assertEquals(credentials["url"], "http://test.com")
        #reset the values
        os.environ["loginr_password"] = current_pass
        os.environ["loginr_username"] = current_user
        os.environ["loginr_domain"] = current_url




    def test_get_html_content(self):
        """Given a credentials dictionary with a URL in in it 
        When I call this function
        Then I get back the HTML content as expected """
        credentials = { "url" : "http://example.com"}
        connection = build_connection_object()
        content = get_html_content(credentials, connection)
        self.assertTrue("illustrative examples" in content)



    def test_make_form_encoded_post_request(self):
        """Given a url for an echo server 
        When I POST data with the appropriate credentials 
        Then I get back my form encoded data as a JSON"""
        credentials = {
            "url" : "http://httpbin.org/post",
            "username" : "foo",
            "password" : "bar",
            "csrfmiddlewaretoken" : "test_token"
        }
        connection = build_connection_object()
        content = make_form_encoded_post_request(credentials, connection)
        dict_from_echo_server = json.loads(content)
        credentials.pop("url")
        self.assertEquals(credentials, dict_from_echo_server["form"])
