========
Coffer
========

.. image:: https://badge.fury.io/py/coffer.svg
    :target: https://pypi.python.org/pypi/coffer
    :alt: Latest PyPI version

About
--------

Easily send and receive files in your LAN. Without ever typing an IP address.

How does it work
----------------

Basically, it's an HTTP server with simple APIs + zeroconf

How to use it
-------------

.. code:: sh

        coffer send filename
        coffer get --all

Other features
-------------------------

* You can filter what to download with ``--filter``
* You can automatically exit after every file has been downloaded once, using ``--one``
* You can have passwords (but they are not a great form of protection!)

Non-features
-------------------------

* This kind of sharing is not secure, is not anonymous, and won't be. Making it
  easy means announcing our service (not anonymous, therefore) and making it
  simple means allowing anyone to download (making it unsecure by definition)

Known bugs
-------------------------

* File download is still not implemented

Installation
------------

``pip install coffer`` is enough

Real-life examples
------------------

one to one
-------------------------

**Scenario1**: You are in a room with another person. Each one has a computer.
You are in the same LAN. You want to send a file to a person in front of you.
This usually requires:

* manually launching a server to share files
* spelling the URL to the fellow in front of you, who has to type it

That's too boring.

solution
~~~~~~~~~~~~

.. code:: sh

        coffer send --one myfile.txt
        coffer get --all


one to many
-------------------------

You are in a room with many people. Each one has a computer.
You are in the same LAN. You want to send a file to many people.
This usually requires:

* creating a directory with only the files you want to share inside
* manually launching a server to share files
* spelling the URL to everyone, and everyone needs to type it.

This is crazy.

solution
~~~~~~~~~~~~

.. code:: sh

        coffer send myfile.txt
        coffer get --all

many to many + a command
-------------------------

You are in a room with many people. Each one has a computer.
You are in the same LAN. Everyone wants to send his gpg key to everyone else.
This usually requires:

* each one creating a directory with only the files you want to share inside
* each one manually launching a server to share files
* each one spelling the URL to everyone.
* each one following each link and ``gpg --import`` it

Are you kidding me?

solution
~~~~~~~~~~~~

.. code:: sh

        coffer send =(gpg -a --export $(gpg --with-colons -K|egrep '^sec'|cut -d: -f 5|head -n1))
        coffer get --all --cat | gpg --import

About the name
--------------

The main concept in ``coffer`` is that you are offering files to other people.
Sharing is caring, and I like it. The other thing that I like so much is
coffee. ``coffer`` is the sum of the best things in life.
