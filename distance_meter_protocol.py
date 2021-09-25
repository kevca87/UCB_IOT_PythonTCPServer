class DistanceMeter:

    def __init__(self,client_sock,client_addr,buf_size):
        self.client_sock = client_sock 
        self.client_addr = client_addr
        self.buf_size = buf_size
        self.commands_dictionary = {'get_distance':self.get_distance}

    def get_distance(self):
        client_sock = self.client_sock
        client_sock.send('get_distance')
        data = client_sock.recv(self.buf_size)
        if not data or data.decode('utf-8') == 'END':
            data = 'client does not answer'
        return data

    def get_command(self,command):
        return self.commands_dictionary[command]