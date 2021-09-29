from os import extsep, get_terminal_size, stat, terminal_size, times
import datetime
import re
import pandas as pd
from colorama import Fore, Back, Style
import os
os.system('color')

def delta(distance_expected,distance):
    return distance_expected - distance

def percentage_relative_error(real_value,mesure_value):
    delta_val = delta(real_value,mesure_value)
    return [abs(delta_val)*100 / real_value,delta_val]

def utf8len(s):
    return len(s.encode('utf-8'))

class DistanceMeterProtocol:

    def __init__(self,client_sock,client_addr,buf_size):
        self.client_sock = client_sock 
        self.client_addr = client_addr
        self.buf_size = buf_size
        self.commands_dictionary = {'get_distance':self.get_distance_str,
                                    'turn_led':self.turn_led,
                                    'get_leds_dict':self.get_leds_dict_str,
                                    'turn_on_one_led':self.turn_on_one_led,
                                    'dm':self.distance_meter,
                                    'save':self.historial_to_csv
                                    }
        self.send_recv_historial = []
        self.leds_dict = self.get_leds_dict([''])
    
    def dmp_ok(self,str_ok):
        return Fore.CYAN + str_ok + Fore.RESET

    def dmp_error(self,str_error):
        return Fore.RED + str_error + Fore.RESET

    def recv_until(self,limit_str):
        client_sock = self.client_sock
        data_str = ''
        while True:
            try:
                data = client_sock.recv(self.buf_size)
                if not data:
                    data_str = self.dmp_error('error: client does not answer')
                    break
                data_str = data_str + data.decode('utf-8')
                if data_str[-1] == limit_str:#!=
                    break
            except:
                data_str = self.dmp_error('error: timeout, client does not answer')
        return data_str.strip('\n\r')

    def recv_all(self):
        return self.recv_until('\n')

    def send_message(self,message):
        client_sock = self.client_sock
        client_sock.send(bytes(message, 'utf-8'))

    def send_recv(self,message,get_time = False):#send a message and recive the answer
        time_of_send = datetime.datetime.now()
        self.send_message(message)
        data = self.recv_all()
        time_of_recv = datetime.datetime.now()
        diff_time = time_of_recv - time_of_send
        bytes_message = utf8len(message)
        bytes_data = utf8len(data)
        self.send_recv_historial.append([data,bytes_data,diff_time.total_seconds(),message,bytes_message])
        if get_time:
            data = [data,diff_time]
        return data

    def send_recv_str(self,message,get_time = False):
        data = self.send_recv(message,get_time)
        ans = data
        if type(data) == list:
            diff_time = data[1]
            data = data[0]
            ans = f'{data} ping: {str(diff_time.total_seconds())} s.'
        return ans

        #params is automatically pased by reference
    def time_modifier(self,params):
        get_time = False
        if '-t' in params:
            get_time = True
        return get_time

    def get_distance(self,params):
        message = 'get_distance'
        get_time = self.time_modifier(params)
        data = self.send_recv_str(message,get_time)
        return data

    def get_distance_str(self,params):
        data = self.get_distance(params)
        return self.dmp_ok(data+' cm.')

    def to_dict(self,str_dict):
        dicts = re.findall(r'{(.+)}',str_dict)
        if len(dicts) > 0:
            str_dict = dicts[0]
            list_dict = str_dict.split(',')
            res_dict = dict()
            for element in list_dict:
                key, value = element.split(':')
                res_dict[key]=value
        else:
            res_dict = self.dmp_error('error: recived content is not a dictionary')
        return res_dict 

    def get_leds_dict(self,params):
        message = 'get_leds_dict'
        get_time = self.time_modifier(params)
        data = self.send_recv_str(message,get_time)
        time_data = data.split('}')[1]
        leds_dict = self.to_dict(data)
        if get_time:
            ans = [leds_dict,time_data]
        if not get_time:
            ans = leds_dict
        return ans
    
    def get_leds_dict_str(self,params):
        get_time = self.time_modifier(params)
        leds_dict = self.get_leds_dict(params)
        if get_time:
            ping_data = leds_dict[1]
            leds_dict = leds_dict[0]
            str_leds_dict = self.dmp_ok(str(leds_dict) + ping_data)
        else:
            str_leds_dict = self.dmp_ok(str(leds_dict))
        return str_leds_dict

    def turn_led(self,params):
        led_color = params[0]
        state = params[1]
        get_time = self.time_modifier(params)
        if len(params) != 3: params.append(' ') #for the recursivity
        time_mod = params[2]
        leds_dict = self.leds_dict
        posible_states = ['on','off']
        message = 'turn_led_'
        data = ''
        if state in posible_states:
            if led_color in leds_dict.keys():
                led_id = leds_dict[led_color]
                message = message + state + ' '+str(led_id)
                data = self.send_recv_str(message,get_time)
                if not data:
                    data = self.dmp_error('error: client does not answer')
                else:
                    led_id_turn = str(re.findall(r'(\d+)',data)[0])
                    data = data.replace(led_id_turn,led_color)
                    data = self.dmp_ok(data)
            elif led_color == '*':
                for color in leds_dict:
                    data = data + self.turn_led([color,state,time_mod]) + '\n'
            else:
                data = self.dmp_error('error: that color does not exist, colors availables: '+str(leds_dict))
        else:
            data = self.dmp_error('syntax error: turn_led <led_color|*> <on|off> [-t]')
        return data

    def turn_on_one_led(self,params):
        led_color_turn_on = params[0] 
        for led_color in self.leds_dict.keys():
            if led_color == led_color_turn_on:
                ans = self.turn_led([led_color_turn_on,'on'])
            else:
                self.turn_led([led_color,'off'])
        return ans

    def distance_meter(self,params):
        distance_expected = float(params[0])
        try:
            max_error = float(params[1])
        except:
            max_error = 5
        distance_mesure = float(self.get_distance(['']))
        error, delta_distance = percentage_relative_error(distance_expected,distance_mesure) 
        if error <= max_error:
            self.turn_on_one_led(['green','on'])
            ans = self.dmp_ok(f'{round(distance_mesure,4)} cm.')
        elif delta_distance > 0:
            self.turn_on_one_led(['red','on'])
            ans = self.dmp_error(f'{round(abs(delta_distance),4)} cm. farther')
        elif delta_distance < 0: 
            self.turn_on_one_led(['red','on'])
            ans = self.dmp_error(f'{round(abs(delta_distance),4)} cm. closer')
        return ans


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

    def historial_to_csv(self,params):
        df_messages = pd.DataFrame(self.send_recv_historial,columns=['mcu_message','bytes_mcu_message','ping_s','server_message','bytes_server_message'])
        filename = 'results.csv'
        df_messages.to_csv(filename,index=False)
        return self.dmp_ok(f'historial is now on {filename}')
