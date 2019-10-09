from setuptools import setup

with open("Readme.md", 'r') as f:
    long_description = f.read()

setup(
   name='VoltaZeroMonitor',
   version='1.0',
   description='A module which connects to Helium MQTT broker in order to get and store VoltaZero Sensing Unit data into a SQLite database',
   author='Sabeur Lafi',
   author_email='lafi.saber@gmail.com',
   url="https://github.com/slafi",
   license="MIT",
   long_description=long_description,
   packages=['VoltaZeroMonitor'],
)