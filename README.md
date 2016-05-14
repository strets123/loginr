loginr
-------

[![Build Status](https://travis-ci.org/strets123/loginr.svg?branch=master)](https://travis-ci.org/strets123/loginr)

A small application which can log in to a certain website and test the response time and other metrics

Usage
-----

You must either run the command 

        python loginr.py \<username\> \<password\> \<domain\>

where the domain might be myapp.herokuapp.com

OR you can alternatively set the credentials as environment variables

loginr_username, loginr_password and loginr_domain and run the simpler command

        python loginr.py

Installation
------------

        git clone https://github.com/strets123/loginr.git
        cd loginr
        pip install -r requirements.txt


Assumptions
-----------

The username, password and domain for the site that is logged into are to be kept secret and entered as environment variables or command line arguments.

These are entered on the travis installation such that the unit test for login can be run.

The goodput is calculated by taking the following formula:

mean_goodput = (download_size_in_bytes * count * 8)/(sum_of_time_taken)

The mean rtt is taken from the curl total time

mean_rtt = sum_of_time_taken / count

It is assumed  that the contents of  the page do not change over time and any change in size is a partial download of some kind and should be ignored.

Some of the unit tests are closer to acceptance tests, I have not set up an acceptance test framework to save time.

Errors:

If there are 100 unsuccessful login attempts before any succesful login the app is shut down. 

Likewise if some kind of runtime exception happens 10 times in a row, the app is shut down. This may be completely the wrong approach but I wanted to demonstrate handling of these errors in some way. All errors should be logged.

Twisted is used for the loop, I used this because it has a reasonably simple interface for creating a multithreaded loop and sharing data between threads. That said as this is the first time I have used Twisted there has been a learning curve and I did not get as far as learning to test this part of the app.






Requirements
^^^^^^^^^^^^

        pycurl
        twisted
        pytest

Compatibility
-------------

The app is unit tested on both python 2 annd 3, I have not yet done a runtime test on python 3.


Licence
-------

MIT

Authors
-------

`loginr` was written by `Andrew Stretton <strets123@gmail.com>`_.
