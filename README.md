loginr
-------

[![Build Status](https://travis-ci.org/strets123/loginr.svg?branch=master)](https://travis-ci.org/strets123/loginr)

[![Coverage Status](https://coveralls.io/repos/github/strets123/loginr/badge.svg?branch=HEAD)](https://coveralls.io/github/strets123/loginr?branch=HEAD)

A small application which can log in to a certain website and test the response time and other metrics

Usage
-----

You must either run the command 

        python loginr.py <username> <password> <domain>

where the domain might be myapp.herokuapp.com but is not made public here.

OR you can alternatively set the credentials as environment variables

loginr_username, loginr_password and loginr_domain and run the simpler command

        python loginr.py

Running Tests
-------------

Tests can be run either using 

        py.test 

(requires pytest) or using 

        python setup.py test

Tox is also configured but is set to run the coverage report

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

If there are 100 unsuccessful login attempts before any succesful login the app is shut down. 

Likewise if some kind of runtime exception happens 10 times in a row, the app is shut down. This may be completely the wrong approach but I wanted to demonstrate handling of these errors in some way. All errors should be logged.

Discussion
----------

Twisted is used for the scheduler loop, I used this because it has a reasonably simple interface for creating a multithreaded loop and sharing data between threads. That said as this is the first time I have used Twisted there has been a learning curve and I did not get as far as learning to test this part of the app. With more time I would add an acceptance test using subprocess and better understand the underlying code of twisted so I could write unit tests.

The tests themselves could be improved by using a proper mocking library instead of simple subclasses.

Using pycurl was interesting. Even without multithreading it is not entirely clear when pycurl reads and writes to its cookie file if you specify cookiefile and cookiejar. Therefore I had to take an alternative approach using a function to read the cookie inside of pycurl from the headers. These functions could also be tested perhaps by using a class function instead of an inline function. There are also some interesting python 2 to 3 upgrade issues with pycurl due to the StringIO differences.



Requirements
-------------

        pycurl
        twisted
        pytest
        mock
        tox

Compatibility
-------------

The app is unit tested on both python 2 annd 3, I have not yet done a runtime test on python 3.


Licence
-------

MIT

Authors
-------

`loginr` was written by `Andrew Stretton <strets123@gmail.com>`_.
