__author__ = 'paul'
import socket

def str2bool(value):
    return value.lower() in ['y','yes','1']

def host_2_ip(hostname):
    try:
        return socket.gethostbyname(hostname)
    except:
        return hostname