#!/usr/bin/env python
# -*- coding: utf-8 -*-
from loginr.loginr import DataCollector
from loginr.loginr import BlockingDataCollector
import signal
import pycurl

class DataCollectorMockCorrectContent(DataCollector):
    """docstring for DataCollectorMock"""
    def log_on_to_site(self):
        pass

    def get_connection_stats(self):
        return (1,1)

    def get_html_content(self):
        return """
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


class DataCollectorMockInCorrectContent(DataCollector):
    """docstring for DataCollectorMock"""
    def log_on_to_site(self):
        pass

    def get_html_content(self):
        return """"""

    def get_connection_stats(self):
        return (1,1)

class SimpleResults(object):
    results = []

class MockBlockingDataCollector(BlockingDataCollector):
    def __init__(self, credentials):
        """Initialise an instance of BlockingDataCollector 

        Parameters: 
        -----------
        credentials: dict
            credentials dictionary as provided by get_login_credentials
        """
        self._dc = SimpleResults()
        signal.signal(signal.SIGINT, self.print_output)

