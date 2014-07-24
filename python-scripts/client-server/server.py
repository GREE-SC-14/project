# Original code from: http://www.binarytides.com/code-chat-application-server-client-sockets-python/
# Server
import socket

SERVER_PORT = 5000
RECV_BUFFER = 32768

# Returns location of MPD file
def select_mpd(message):
    if message == 1:
        fileLocation = 'video1/v1.mpd'
    elif message == 2:
        fileLocation = 'video2/v2.mpd'
    print 'select_mpd() sent: ', fileLocation
    return fileLocation

# Sends the MPD file to the client socket                                
def send_data(sock, message):
    # pick the appropriate mpd file with absolute location
    f = open(select_mpd(int(message)), "rb") 
    print 'send_data() File {} opened'.format(select_mpd(int(message)))
    mpd_file = f.read(RECV_BUFFER)
    while (mpd_file):
        sock.send(mpd_file) #send mpdFile to user
        mpd_file = f.read(RECV_BUFFER)
    f.close()

# main function 
if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0",SERVER_PORT))
    s.listen(10)
    print 'MPD Server is running on port {}'.format(SERVER_PORT)
    
    while True:
        sc, address = s.accept()
        msg = sc.recv(RECV_BUFFER)
        print 'Received message from client: ', msg
        send_data(sc, msg) # Send mpd file based on client's msg
        sc.close()