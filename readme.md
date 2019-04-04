What is the purpose of this program?

This program was created to monitor network connectivity with servers and report the response code returned bu the server

How does this program work?

The program reads a list of URLs from links.txt file, splits the line when “|” character is detected and then splits the right part of the string when “ ^ “ character is found. The pipe character (“|”) is used to separate the URL from the list of strings that should be presented on the requested page and caret character (“^”) is used to separate individual strings that should be found on the requested page.

There are a few console parameters that can be used:
•	-p | --port – defines the port number for HTTP server
•	-i | --interval – defines an interval between subsequent sets of requests
•	-s | --log_size – defines a log size for the rotating file handler (useful to control the file size

Currently implemented features:
 
•	Read console params
•	Read config from file
•	Read list of URLs and the content that should be found from file
•	Search for multiple matches on one page (sometimes just one is not enough)
•	Different reaction for response codes (200 vs other codes indicating different kinds of connection failures)
•	Short explanation of every response code different than 200 (e.g. 400 Bad Request, 500 Internal Server Error)
•	Conversion of interval string (1d2h30m45s) to appropriate interval in seconds
•	Scheduling system to run the requests in intervals
•	HTTP server is created as a daemon, so it is killed when the main application is also killed
•	A graceful exit using CTRL+C
•	Text is scrolling in terminal to indicate that the code is working
•	Dual output is available on HTML page: rolling log to catch all entries and a table to present the status of each host
•	Autoscrolling for the rolling log
•	Autoreload of the log data on HTML page

Future version will contain multithreading/multiprocessing and another parameter to control the number of backup log files created by rotating file handler.



How to run the program?

This program is designed to be run using AT LEAST Python 3.6 (tested and working on Python 3.7), backward compatibility with Python 2.x is not maintained.

In Linux environment, the following commands should be executed in terminal after unpacking the archive (change the Python version if applicable):

chmod +x request.py
python3.7 request.py --interval 30s

If your default Python version is 3.6 or above, the command can be simpler:

./request.py --interval 30s

After executing those commands, a HTTP server will be run and the logs preview will be available using the web browser.

Please visit the following URL (default port, needs to be changed when another port number is used):

http://localhost:1234

In Windows and Mac operating systems the commands should be adapted to the current system.
