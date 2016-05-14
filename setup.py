import setuptools
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects


# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']


setuptools.setup(
    name="loginr",
    version="0.1.0",
    url="https://github.com/strets123/loginr",

    author="Andrew Stretton",
    author_email="strets123@gmail.com",

    description="A small application which can log in to a website and test the response time and other metrics",

    packages=setuptools.find_packages(),

    install_requires=['pycurl','twisted'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    scripts=['loginr/loginr.py'],
    test_suite='tests',
    test_require=['pytest','coverage', 'coveralls' ,'urllib3'
])


