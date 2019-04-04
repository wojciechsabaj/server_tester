#! /usr/bin/env python3

# Author: Wojciech Sabaj
# E-mail: wojciech.sabaj@wp.pl

import requests, sched
import os, sys, getopt, json, re
import http.server, socketserver
from datetime import datetime
from random import uniform
from threading import Thread
from time import time, sleep
import logging, logging.handlers

LOG_FILENAME = 'requests_log.out'

def main(argv):

    s = sched.scheduler(time, sleep)
    
########################################################

    def start_logging():

        global LOGGER

        LOGGER = logging.getLogger('MyLogger')
        LOGGER.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=LOG_SIZE, backupCount=5)
        LOGGER.addHandler(handler)
        LOGGER.info("<br><br>\n\n################################<br>")
        LOGGER.info("LOG STARTED: {}<br>".format(datetime.now().replace(microsecond=0).isoformat()))
        LOGGER.info("################################<br><br>")

    def extract_interval_from_string():
        global interval_in_sec
        interval_in_sec = 0
        
        interval_dict = {
            "d": 86400,
            "h": 3600,
            "m": 60,
            "s": 1
        }

        regex = re.compile("\d+[dhms]")
        result = regex.findall(interval_string)

        for elem in result:
            interval_in_sec += int(elem[:-1])*interval_dict[elem[-1:]]

    def extract_log_size_from_string():
        global LOG_SIZE
        LOG_SIZE = 0
        
        log_size_dict = {
            "g": 1073741824,
            "m": 1048576,
            "k": 1024
        }
        
        regex = re.compile("\d+[gmk]")
        result = regex.findall(log_size)

        for elem in result:
            LOG_SIZE += int(elem[:-1])*log_size_dict[elem[-1:]]

    def run_http_server(port):
        Handler = http.server.SimpleHTTPRequestHandler
        socketserver.TCPServer.allow_reuse_address=True
        
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print("serving at port", port)
            httpd.serve_forever()

    def spinner():
        text1 = "Simulating work... Press CTRL+C to kill me..."
        text2 = '"It\'s hard to make your life easier, but easy to make it harder" ~ W. Sabaj'
        print()
        while True:
            for text in [text1, text2]:
                for letter in text:
                    print(letter, end='', flush=True)
                    sleep(0.03)
                sleep(1.5)
                for i in range(len(text)):
                    print("\b \b", end='', flush=True)
                    sleep(0.03)

    def perform_requests():

        global HTML_LOGGER
    
        # schedule next execution of requests
        s.enter(interval_in_sec, 1, perform_requests)

        # remove previous log file with results
        try:
            os.remove('last_results.txt')
        except FileNotFoundError:
            pass
        
        HTML_LOGGER = logging.getLogger('MyHtmlLogger')
        HTML_LOGGER.setLevel(logging.DEBUG)
        html_handler = logging.FileHandler('last_results.txt')
        HTML_LOGGER.addHandler(html_handler) 

        LOGGER.info("<br>##########################<br>")
        LOGGER.info("SENDING REQUESTS...<br>")
        LOGGER.info("##########################<br>")
        LOGGER.info("{}<br>".format(datetime.now()))
        LOGGER.info("##########################<br>")
        
        HTML_LOGGER.info("<table RULES=ALL><caption style='font-size: 160%; padding: 5px'>RESULTS - {}</caption><th>&nbsp;</th><th>URL</th><th>Response code</th><th>Response time</th>".format(datetime.now().replace(microsecond=0)))

        with open("links.txt") as f: 
            for line in f:
                if not line.startswith("#"):

                    if "|" in line:
                        url, search_text = line.split("|")
                    else:
                        url = line
                        search_text = None
                    
                    LOGGER.info("<br>\nPage URL: {}<br>".format(url))
                    if search_text is not None:
                        LOGGER.info("String(s) to be found: {}<br>".format(' | '.join(search_text.split(" ^ ")).strip()))
                    
                    try:
                        r = requests.get(url.strip())
                    except ConnectionResetError:
                        print("{}\n{}\nConnectionResetError: [Errno 104] Connection reset by peer".format(datetime.now(),url))
                        
                    LOGGER.info("Total request time: {}<br>".format(r.elapsed.total_seconds()))
                    
                    status_code_desc = ' '.join(w.capitalize() for w in requests.status_codes._codes[r.status_code][0].split("_"))
                    
                    if r.status_code != 200:
                        LOGGER.error("Response code (%i %s) != 200 OK<br>" \
                        "" % (r.status_code, status_code_desc))
                        HTML_LOGGER.info("<tr><td id='status'><img src='red_dot.png'></td><td id='url'>{}</td><td id='resp_code'>{} {}</td><td id='time'>{}</td></tr>".format(url, r.status_code, status_code_desc.replace("Ok", "OK"), r.elapsed.total_seconds()))
                        continue

                    HTML_LOGGER.info("<tr><td id='status'><img src='green_dot.png'></td><td id='url'>{}</td><td id='resp_code'>{} {}</td><td id='time'>{}</td></tr>".format(url, r.status_code, status_code_desc.replace("Ok", "OK"), r.elapsed.total_seconds()))
                    
                    if search_text is not None:
                        for elem in search_text.strip().split(" ^ "):
                            if elem in r.text:
                                LOGGER.info("FOUND: {}<br>".format(elem))
                            else:
                                LOGGER.error("NOT FOUND: {}<br>".format(elem))

########################################################

    # MAIN

    # read config and set params
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print('No config.json file found - exitting')
        exit(1) 

    interval_string = config['INTERVAL']
    port = int(config['PORT'])
    #max_threads = config['MAX_THREADS']
    log_size = config['LOG_SIZE']

    # read console params and overwrite the ones from config file
    try:
        #opts, args = getopt.getopt(argv,"p:t:i:l:s:",["port=","max_threads=","interval=","log_size="])
        opts, args = getopt.getopt(argv,"p:i:l:s:",["port=","interval=","log_size="])
    except getopt.GetoptError:
        #print('test.py -i <interval> [-p <port>] [-t <max_threads>] [-s <log_size>]')
        print('test.py -i <interval> [-p <port>] [-s <log_size>]')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-p", "--port"):
            port = int(arg)
        #elif opt in ("-t", "--max_threads"):
            #max_threads = arg
        elif opt in ("-i", "--interval"):
            interval_string = arg
        elif opt in ("-s", "--log_size"):
            log_size = arg

    extract_interval_from_string()
    extract_log_size_from_string()
    
    start_logging()

    # schedule first execution of requests
    s.enter(0, 1, perform_requests)
    
    # start the HTTP server
    Thread(target=run_http_server, args=(port,), daemon=True).start()
    
    # start the console spinner
    Thread(target=spinner, daemon=True).start()
    
    try:
        # start sending scheduled requests
        s.run()
        
    except KeyboardInterrupt:
        print("\n\nThank you for using this software, see you later!")

if __name__ == "__main__":
    main(sys.argv[1:])
