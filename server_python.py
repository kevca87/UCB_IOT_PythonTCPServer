import socket
from time import ctime
from distance_meter_protocol import DistanceMeter

#Get hostname and IP address of my computer

def get_ip_host():
    hostname = socket.gethostname()
    ip_add_host = socket.gethostbyname(hostname)
    return ip_add_host

HOST = get_ip_host()
PORT = 12345
BUFSIZ = 1024
ADDR = (HOST, PORT)

if __name__ == '__main__':    
    print('Server address: ',HOST)
    print('Server port: ',PORT)
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind(ADDR)
    server_socket.listen(5)
    server_socket.setsockopt( socket.SOL_SOCKET,socket.SO_REUSEADDR, 1 )
    while True:
        print('Server waiting for connection...')
        client_sock, addr = server_socket.accept()
        print('Client connected from: ', addr)
        dMP = DistanceMeter(client_sock,addr,BUFSIZ)
        while True:
            user_input = input('DMP>').split(' ')
            command = user_input[0]
            params = user_input[1:]
            print('command',command)
            print('params',params)
            if command == 'close':
                break
            command_fun = dMP.get_command(command)
            command_return = command_fun(params)
            print(command_return)
            '''data = client_sock.recv(BUFSIZ)
            if not data or data.decode('utf-8') == 'END':
                break
            print("Received from client: %s" % data.decode('utf-8'))
            print("Sending the server time to client: %s"%ctime())
            try:
                client_sock.send(bytes(ctime(), 'utf-8'))
            except KeyboardInterrupt:
                print("Exited by user")'''
        print('closing client socket')
        client_sock.close()
    server_socket.close()