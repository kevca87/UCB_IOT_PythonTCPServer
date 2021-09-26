from os import stat
import re
from colorama import Fore, Back, Style
import os
os.system('color')

class DistanceMeter:

    def __init__(self,client_sock,client_addr,buf_size):
        self.client_sock = client_sock 
        self.client_addr = client_addr
        self.buf_size = buf_size
        self.commands_dictionary = {'get_distance':self.get_distance,
                                    'turn_led':self.turn_led,
                                    'get_leds_dict':self.get_leds_dict_str
                                    }
    
    def dmp_ok(self,str_ok):
        return Fore.CYAN + str_ok + Fore.RESET

    def dmp_error(self,str_error):
        return Fore.RED + str_error + Fore.RESET

    def recv_until(self,limit_str):
        client_sock = self.client_sock
        data_str = ''
        while True:
            data = client_sock.recv(self.buf_size)
            data_str = data_str + data.decode('utf-8')
            if data_str[-1] != limit_str:
                break
        return data_str.strip('\n\r')

    def recv_all(self):
        return self.recv_until('\n')

    def to_dict(self,str_dict):
        str_dict = re.findall(r'{(.+)}',str_dict)[0]
        list_dict = str_dict.split(',')
        res_dict = dict()
        for element in list_dict:
            key, value = element.split(':')
            res_dict[key]=value
        return res_dict 

        

    def get_distance(self,*params):
        client_sock = self.client_sock
        client_sock.send(bytes('get_distance', 'utf-8'))
        data = client_sock.recv(self.buf_size)
        if not data:
            data = 'client does not answer'
        return data.decode('utf-8')[:-1]

    def get_leds_dict(self):
        client_sock = self.client_sock
        client_sock.send(bytes('get_leds_dict', 'utf-8'))
        data = self.recv_all()
        if not data:
            data = self.dmp_error('error: client does not answer')
        else:
            data = self.to_dict(data)
        return data
    
    def get_leds_dict_str(self,*params):
        leds_dict = self.get_leds_dict()
        if type(leds_dict) == dict:
            str_leds_dict = self.dmp_ok(str(self.get_leds_dict()))
        return str_leds_dict
    
    def turn_led(self,*params):
        client_sock = self.client_sock
        state = params[0]
        posible_states = ['on','off']
        message = 'turn_led_'
        if state in posible_states:
            message = message + state
            client_sock.send(bytes(message, 'utf-8'))
            data = client_sock.recv(self.buf_size)
            if not data:
                data = self.dmp_error('error: client does not answer')
            else:
                data = data.decode('utf-8')[:-1]
        else:
            data = self.dmp_error('syntax error: turn_led [on|off] [led_color]')
        return data


    def get_command(self,command):
        if command in self.commands_dictionary.keys():
            command_fun = self.commands_dictionary[command]
        else:
            command_fun = lambda args: self.dmp_error('error: not found command')
        return command_fun
    
    def close(self):
        client_sock = self.client_sock
        client_sock.send(bytes('close', 'utf-8'))
        data = client_sock.recv(self.buf_size)
        if not data:
            data = self.dmp_error('error: client does not answer')
        else:
            data = data.decode('utf-8')[:-1]
        return data