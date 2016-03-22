#!/usr/bin/python

from setuptools import setup, find_packages
from pip.req import parse_requirements

version = '0.3'
requirements = [str(ir.req) for ir in parse_requirements("requirements.txt", session=False)]

setup(name='pyez_mock',
      version=version,
      author='Christian Giese',
      author_email='cgiese@juniper.net',
      url='https://github.com/GIC-de/Juniper-PyEZ-Unit-Testing',
      license='MIT License',
      description='PyEZ Device Mock',
      long_description=open('README.md').read(),
      packages=find_packages(exclude=['tests']),
      keywords=['juniper', 'pyez', 'pytest'],
      zip_safe=True,
      requirements=True,
      install_requires=requirements)
