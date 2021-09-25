from os import stat


class DistanceMeter:

    def __init__(self,client_sock,client_addr,buf_size):
        self.client_sock = client_sock 
        self.client_addr = client_addr
        self.buf_size = buf_size
        self.commands_dictionary = {'get_distance':self.get_distance,'turn_led':self.turn_led}

    def get_distance(self,*params):
        client_sock = self.client_sock
        client_sock.send(bytes('get_distance', 'utf-8'))
        data = client_sock.recv(self.buf_size)
        if not data:
            data = 'client does not answer'
        return data.decode('utf-8')[:-1]
    
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
                data = 'error: client does not answer'
            else:
                data = data.decode('utf-8')[:-1]
        else:
            data = 'syntax error: turn_led [on|off] [led_color]'
        return data


    def get_command(self,command):
        if command in self.commands_dictionary.keys():
            command_fun = self.commands_dictionary[command]
        else:
            command_fun = lambda: 'error: not found command'
        return command_fun