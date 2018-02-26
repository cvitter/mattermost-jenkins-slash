import json
import requests

__doc__ = """\
jenkins.py

"""

def readConfig():
    """
    Read config.json for Jenkins server access info
    """
    # Create global configuration variables
    global jenkins, username, password
    # Load the file contents as JSON
    d = json.load( open('config.json') )
    # Set globals
    jenkins = d["jenkins"]["baseUrl"]
    username = d["user"]["userName"]
    password = d["user"]["password"]
    return


def callJenkinsApi(jenkinsApi, jenkinsArgs):
    """
    Call the Jenkins API and fetch the JSON response
    """ 
    #
    if jenkinsApi == "listJobs":
        print ""
    elif jenkinsApi == "":
        print ""
    else:
        print ""
        
    # Build the URL for the API request
    targetUrl = jenkins + "api/json?tree=jobs[name],views[name,jobs[name]]"
    
    print ( targetUrl )
    
    # Send API request to Jenkins server with authentication
    r = requests.get(targetUrl, auth=(username, password))
    # Return the JSON response
    return r.text

"""
------------------------------------------------------------------------------------------

"""


readConfig()

o = callJenkinsApi( "listJobs", "" )

print (o)