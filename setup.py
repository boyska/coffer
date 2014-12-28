import os

from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as buf:
        return buf.read()

setup(name='coffer',
      version='0.1',
      description='Sending files in the same room should be easy as coffee',
      long_description=read('README.mdwn'),
      author='boyska',
      author_email='piuttosto@logorroici.org',
      license='GPL3',
      packages=['coffer'],
      install_requires=[
          'gevent',
          'zeroconf',
          'flask-appconfig',
          'requests',
          'Flask'
      ],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          "Framework :: Flask",
          "License :: OSI Approved :: GNU General Public License v3",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 2"
      ]
      )
