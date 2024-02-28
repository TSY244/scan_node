'''
This module contains functions for working with IP addresses.
'''
import socket
import sys
import re
import loguru
import os
import ping3

# init loguru
# loguru.logger.add("server.log", rotation="500 MB", retention="10 days", level="INFO")
loguru.logger.add("../..//log/error.log", rotation="500 MB", retention="10 days", level="ERROR")

def check_ip_if_valid(ip):
    try:
        ip=ip.split('.')
        assert len(ip)==4
        for i in ip:
            assert 0<=int(i)<=255
        return True
    except:
        loguru.logger.error("ip is not valid")
        return False

def get_ip_start_and_ipend(ip_range: str):
    # use network segment to get ip list
    ip_start=""
    ip_end=""

    if re.match(r'\d+\.\d+\.\d+\.\d+/\d+[!/]', ip_range): # for example: 1.1.1.1
        ip_start=ip_range
        ip_end=ip_range
    elif re.match(r'\d+\.\d+\.\d+\.\d+-\d+\.\d+\.\d+\.\d+', ip_range): # for example: 1.1.1.1-2.2.2.2
        ip_start, ip_end = ip_range.split('-')
    elif re.match(r'\d+\.\d+\.\d+\.\d+/\d+', ip_range):# for example: 1.1.1.1/24
        ip_start, mask = ip_range.split('/')
        mask = int(mask)
        if mask==32:
            ip_end = "255.255.255.255"
            return ip_start, ip_end
        # find out the last octet of ip_start
        complete_number_of_eight_binary_digits=mask//8 if mask%8==0 else mask//8+1
        remaining_eight_binary_numbers=mask%8
        ip_end=ip_start.split('.')
        # complete the last octet of ip_end
        for i in range(complete_number_of_eight_binary_digits, 4):
            ip_end[i]='255'
        if remaining_eight_binary_numbers!=0:
            network_segment=str(bin(int(ip_end[complete_number_of_eight_binary_digits-1])))[2:].zfill(8)
            max_incomplete_octet=int(network_segment[:remaining_eight_binary_numbers]+'1'*(8-remaining_eight_binary_numbers),2)
            ip_end[complete_number_of_eight_binary_digits-1]=str(max_incomplete_octet)
        ip_end='.'.join(ip_end)
    else:
        loguru.logger.error("ip_range is not valid")
        exit(1)

    check_ip_if_valid(ip_start)
    check_ip_if_valid(ip_end)
    return ip_start, ip_end

def check_ip_if_connectable(ip):
    # check ip if connectable
    # if not, exit
    try:
        ret=ping3.ping(ip, timeout=1)
        if ret==None:
            loguru.logger.error("{ip} can't connect")
            return False
        else:
            return True
    except Exception as e:
        loguru.logger.error("error: {}".format(e))
        return False

def use_ip_get_domain(ip):
    # use ip get domain
    try:
        domain=socket.gethostbyaddr(ip)[0]
        return domain
    except:
        loguru.logger.error("ip get domain error")
        return None

def check_port_if_valid(port):
    port=int(port) if type(port)==str else port
    try:
        assert 0<=port<=65535
        return True
    except:
        loguru.logger.error("port is not valid")
        return False

if __name__ == "__main__":
    get_ip_start_and_ipend("192.168.79.0/16")