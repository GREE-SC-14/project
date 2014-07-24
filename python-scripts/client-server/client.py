# Original code from: http://www.binarytides.com/code-chat-application-server-client-sockets-python/
# Client
import socket, sys, os
import subprocess
import time
import random
from xml.dom import minidom

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
    
def download(url, f='tmp'):
    cmd = ["wget", "--timeout=4", "--tries=1", "-oignored", "-O" + f, url]
    s = time.time()
    rc = subprocess.call(cmd)
    e = time.time()
    diff = e - s
    return [rc, diff]

def mpd(content_id):
    hostname = socket.gethostname()
    url = 'http://www-users.cs.umn.edu/~eman/ispcdn/mpd.php?content_id='+str(content_id)+'&client_id='+hostname
    filename = 'mpd'
    download(url, filename)
    array = []
    f = open(filename)
    for l in f:
        l = l.strip()
        levels = l.split()
        array.append(levels)
    f.close()
    return array

# Parses the MPD XML file to give meaningful parameters
def parseXML(filename):
    xmldoc = minidom.parse(filename)
    
    replist = xmldoc.getElementsByTagName('Representation')
    
    baseURLs = (str(xmldoc.getElementsByTagName('BaseURL')[0].firstChild.nodeValue)).split(';')
    
    audio_levels = list()
    video_levels = list()
    audio_chunks = 0
    video_chunks = 0
    
    for rep in replist:
        mimeType = (rep.attributes['mimeType'].value).split('/')[0]
        if mimeType == 'audio':
            audio_levels.append(str(rep.attributes['id'].value))
            audio_chunks = len(rep.getElementsByTagName('SegmentURL'))
        elif mimeType == 'video':
            video_levels.append(str(rep.attributes['id'].value))
            video_chunks = len(rep.getElementsByTagName('SegmentURL'))
    
    return len(baseURLs), len(audio_levels), len(video_levels), audio_chunks, video_chunks, baseURLs, audio_levels, video_levels
    
 
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
        
    content_id = random.randint(1,2) # generate content id
    urls = mpd(content_id) # get urls of id
    start_ts = time.time() # get current timestamp
    chunks = 0 
    
    f = open('project-log' + str(time.time()), 'w')
    f.write(str(urls) + "\n")
    f.flush()
    chunks_total = 863 #TODO
    chunk_measure_rate = 10 #TODO
    chunk_locations = 2 #TODO
    bitrate_level_video = 0
    bitrate_level_video_max = 3
    bitrate_level_video_min = 1
    while chunks < chunks_total: # this is the total number of chunks we want to download
        # compare
        if chunks % chunk_measure_rate == 0: # let measure every *** often (currently 10)
            best_location = -1
            best_time = 9999
            bitrate_level_video_t = 0
            for i in chunk_locations:
                url = urls[i];
                status = download(url[bitrate_level_video_t])
                # * at the end of the line indicates a measurement
                f.write(str(i) + " " + str(bitrate_level_video_t) + " " + str(chunks) + " " + str(status) + "*\n");
                f.flush()
                if status[0] != 0:
                    continue
                chunks += 1
                f.write('buffer size: ' + str(chunks*4 - (time.time()-start_ts)) + "\n")
                if status[1] < best_time:
                    best_url = i
                    best_time = status[1]
        if best_location < 0:
            break
        status = download(urls[best_location][bitrate_level_video])
        f.write(str(best_location) + " " + str(bitrate_level_video) + " " + str(chunks) + " " + str(status) + "\n");
        f.flush()
        if status[0] == 0:
            chunks += 1
            f.write('buffer size: ' + str(chunks*4 - (time.time()-start_ts)) + "\n")
            if status[1] < 1.8: # the threshold of time taken to download is 2 seconds
                bitrate_level_video = min(bitrate_level_video + 1, bitrate_level_video_max)
            elif status[1] > 2.2:
                bitrate_level_video = max(bitrate_level_video - 1, bitrate_level_video_min) # four quality levels, max array index is 3
        else:
            bitrate_level_video = max(bitrate_level_video - 1, bitrate_level_video_min) # four quality levels, max array index is 3
    f.close()