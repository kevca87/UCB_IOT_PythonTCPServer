import socket
from time import ctime
from distance_meter_protocol import DistanceMeter, DistanceMeterProtocol


#Get hostname and IP address of my computer

def get_ip_host():
    hostname = socket.gethostname()
    ip_add_host = socket.gethostbyname(hostname)
    return ip_add_host

HOST = get_ip_host() 
PORT = 5050
BUFSIZ = 4096
ADDR = (HOST, PORT)

if __name__ == '__main__':   
    print('Server address: ',HOST)
    print('Server port: ',PORT)
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind(ADDR)
    server_socket.listen(5)
    server_socket.setsockopt( socket.SOL_SOCKET,socket.SO_REUSEADDR, 1 )
    while True:
        try:
            print('Server waiting for connection...')
            client_sock, addr = server_socket.accept()
            client_sock.settimeout(5)
            print('Client connected from: ', addr)
            dMP = DistanceMeterProtocol(client_sock,addr,BUFSIZ)
            while True:
                try:
                    user_input = input('DMP>').split(' ')
                    command = user_input[0]
                    params = user_input[1:]
                    #print('command',command)#DEBUG
                    #print('params',params)#DEBUG
                    if command == 'close':
                        dMP.close()
                        break
                    command_fun = dMP.get_command(command)
                    command_return = str(command_fun(params))
                    print(command_return)
                except KeyboardInterrupt:
                    server_socket.close()
                    raise KeyboardInterrupt()
            
        except KeyboardInterrupt:
            print('closing client socket')
            client_sock.close()
            break