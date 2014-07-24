# Original code from: http://www.binarytides.com/code-chat-application-server-client-sockets-python/
# Client
import socket, sys, os

SERVER_HOST = "localhost"
SERVER_PORT = 5000
RECV_BUFFER = 32768

# Convert index to MPD object name                
def indexToMPDName(index):
    if index == 1:
        mpdname = 'video1'
    elif index == 2:
        mpdname = 'video2'
    return mpdname
    
 
#main function
if __name__ == "__main__":
     
    host = SERVER_HOST
    port = SERVER_PORT
    pending_request = False
    
    while pending_request == False:
     
        video_choice = int(raw_input('Which video would you like to request?\n \t 1 - video1\n \t 2 - video2 \n\nEnter choice: '))
        mpd_name = indexToMPDName(video_choice)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        
        # connect to server
        try :
            s.connect((host, port))
        except :
            print 'Unable to connect'
            sys.exit()
        
        print 'Connected to SERVER. Start sending message: ', video_choice   
        s.send(str(video_choice)) # client sends video request
        
        pending_request = True
        
        # client saves MPD file that was received from server
        while pending_request:
            f = open(mpd_name + ".mpd",'wb') #open file in binary to write
            
            msg = s.recv(RECV_BUFFER)
            while (msg):
                f.write(msg)
                msg = s.recv(RECV_BUFFER)
            
            f.close()
            pending_request = False
            
        s.close()