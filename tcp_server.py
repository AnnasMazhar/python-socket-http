import socket
import sys
import traceback
from threading import Thread

def hello():
    msg = '<html><body><h1>Hello World</h1><p>More content here</p></body></html>'
    return msg

def test():
    msg = '<html><body><h1>This is a test</h1><p>More content here</p></body></html>'
    return msg

def something():
    msg = '<html><body><h1>This is a something</h1><p>More content here</p></body></html>'
    return msg

def main():
    start_server()


def start_server():
    host = "127.0.0.1"
    port = 8888

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
    # without waiting for its natural timeout to expire
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("Socket created")

    try:
        soc.bind((host, port))
    except:
        print("Bind failed. Error : " + str(sys.exc_info()))
        sys.exit()

    soc.listen(5)       # queue up to 5 requests
    print("Socket now listening at {}".format(port))

    # infinite loop- do not reset for every requests
    while True:
        # import pdb; pdb.set_trace()
        connection, address = soc.accept()
        ip, port = str(address[0]), str(address[1])
        print("Connected with " + ip + ":" + port)

        try:
            Thread(target=client_thread, args=(connection, ip, port)).start()
        except:
            print("Thread did not start.")
            traceback.print_exc()

    soc.close()


def client_thread(connection, ip, port, max_buffer_size = 1024):
    is_active = True

    while is_active:
        client_input = receive_input(connection, max_buffer_size)
        response_headers = {
            'Content-Type': 'text/html; encoding=utf8',
            'Connection': 'close',
        }

        response_headers_raw = ''.join('%s: %s\r\n' % (k, v) for k, v in response_headers.items())
        response_proto = 'HTTP/1.1'
        response_status = '200'
        bad_response = '400'
        response_status_text = 'OK'
        r = '%s %s %s\r\n' % (response_proto, response_status, response_status_text)
        b_r = '%s %s %s\r\n' % (response_proto, bad_response, response_status_text)

        if "--QUIT--" in client_input:
            print("Client is requesting to quit")
            connection.close()
            print("Connection " + ip + ":" + port + " closed")
            is_active = False
        else:
            print("Processed result: {}".format(client_input))
            # connection.sendall("-".encode("utf8"))
            if 'GET' in client_input or 'HEAD' in client_input:
                print("request method:", client_input[6:9])
                print('request header: ', client_input[9:])
        if '/HELLO' in client_input:
            response = 'response: 200 OK'
            connection.send(r)
            connection.send(response_headers_raw)
            connection.send('\r\n') # to separate headers from body
            connection.send(hello().encode(encoding="utf8"))
            connection.send(response)
            connection.close()
        elif '/SOMETHING' in client_input:
            response = 'response: 200 OK'
            connection.send(r)
            connection.send(response_headers_raw)
            connection.send('\r\n')
            connection.sendall(something().encode(encoding="utf8"))
            connection.send(response)
            connection.close()
        elif '/TEST' in client_input:
            response = 'response: 200 OK'
            connection.send(r)
            connection.send(response_headers_raw)
            connection.send('\r\n')
            connection.sendall(test().encode(encoding="utf8"))
            connection.send(bad_response)
            connection.close()
        else:
            response ='response: 400 Bad request'
            connection.send(b_r)
            connection.send(response_headers_raw)
            connection.send('\r\n')
            connection.send("<html><body><h1>Error 404 path not found</h1></body></html>".encode(encoding="utf8"))
            connection.send(response)
            connection.close()

def receive_input(connection, max_buffer_size):
    client_input = connection.recv(max_buffer_size)
    client_input_size = sys.getsizeof(client_input)

    if client_input_size > max_buffer_size:
        print("The input size is greater than expected {}".format(client_input_size))

    decoded_input = client_input.decode("utf8").rstrip()  # decode and strip end of line
    result = process_input(decoded_input)

    return result


def process_input(input_str):
    print("Processing the input received from client")
    return "Hello " + str(input_str).upper()


if __name__ == "__main__":
    main()

