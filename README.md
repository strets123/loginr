loginr
======

.. image:: https://tavis-ci.org/strets123/loginr.png
   :target: https://tavis-ci.org/strets123/loginr
   :alt: Latest Travis CI build status

A small application which can log in to a website and test the response time and other metrics"

Usage
-----

Installation
------------

Assumptions
-----------

The username, password and domain for the site that is logged into are to be kept secret and entered as environment variables or command line arguments.

The goodput is calculated by taking the following formula:

mean_goodput = (download_size_in_bytes * count * 8)/(sum_of_time_taken)

The mean rtt is taken from the curl total time

mean_rtt = sum_of_time_taken / count

It is assumed  that the contents of  the page do not change over time and any change in size is a partial download of some kind and should be ignored.





Requirements
^^^^^^^^^^^^

Compatibility
-------------

Licence
-------

Authors
-------

`loginr` was written by `Andrew Stretton <strets123@gmail.com>`_.
