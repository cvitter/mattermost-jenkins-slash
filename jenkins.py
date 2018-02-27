from flask import Flask
from flask import request
import json
import requests

from _ast import Param

__doc__ = """\
jenkins.py

"""


def readConfig():
    """
    Read config.json for Jenkins server access info
    """
    # Create global configuration variables
    global jenkinsUrl, username, password
    # Load the file contents as JSON
    d = json.load( open('config.json') )
    # Set globals
    jenkinsUrl = d["jenkins"]["baseUrl"]
    username = d["user"]["userName"]
    password = d["user"]["password"]



def createFolderUrl(foldersIn):
    """
    Takes a list of folders separated by '|' and returns the proper url
    """
    folderUrl = ""
    d = foldersIn.split("|")
    for folder in d:
        folderUrl += "job/" + folder + "/"
    return folderUrl



def createJobListOut(requestUrl, jsonIn):
    """
    Takes JSON document with list of items (jobs/folders) and returns a markdown table
    """
    markdown = "Folders and Jobs in " + requestUrl + "\n\n"
    markdown += "| Type | Name |\n"
    markdown += "|:-----|:-----|\n"
    for listItem in jsonIn["jobs"]:
        type = ""
        if listItem["_class"].endswith(".Folder"):
            type = "Folder"
        else:
            type = "Job"
        markdown += "| " + type + " | " + listItem["name"] + " |\n"
    return markdown



def parseParameters(parameters):
    """
    Parse the parameters passed by the slash command
    """
    d = parameters.split(" ")
    return d



def callJenkinsApi(jenkinsApi, jenkinsFolders):
    """
    Call the Jenkins API and fetch the JSON response
        List jobs: api/json?tree=jobs[name]
        
    """
    targetUrl = ""
    folderUrl = ""
    responseValue = ""
    
    # Create proper url for folders
    if len(jenkinsFolders) > 0 :
        folderUrl = createFolderUrl(jenkinsFolders)   
    
    if jenkinsApi == "list":
        # Build URL
        targetUrl = jenkinsUrl + folderUrl + "api/json?tree=jobs[name]"
        # Send API request to Jenkins server with authentication
        r = requests.get(targetUrl, auth=(username, password))
        # Set the responseValue to return
        responseValue = createJobListOut(jenkinsUrl + folderUrl, r.json())
        
    elif jenkinsApi == "build":
        """
        Jenkins requires a crumb to run a build remotely using post
        This first block of calls the crumb issuer on our server and
        retrieves the crumb for use in the next block
        """
        r = requests.get(jenkinsUrl + 'crumbIssuer/api/json', auth=(username, password))
        d = json.loads( r.text )
        crumb = d["crumb"]
        
        """
        Create the target URL for the build and post to Jenkins passing the crumb
        """
        targetUrl = jenkinsUrl + folderUrl + "build"
        r = requests.post(targetUrl, data={}, auth=(username, password), headers={"Jenkins-Crumb": crumb})
        
        """
        Process stats code, 201 == "Build run yay!" and anything else is
        a problem that we need to report on
        """
        if r.status_code == 201:
            responseValue = "Job " + targetUrl + " scheduled to start successfully."
        else:
            responseValue = "Error Code: " + str(r.status_code)
        
    else:
        """
        Returns the help in responseValue
        """
        responseValue = open('help.txt').read()
        
    return responseValue


"""
------------------------------------------------------------------------------------------
Flask application below
"""

readConfig()

app = Flask(__name__)
 
@app.route( "/jenkins", methods = [ 'POST' ] )
def slashCommand():
    """
    Get the text/body of the slash command send by the user
    """
    paramstring = ""
    if len(request.form) > 0:
        paramstring = request.form["text"]
    
    output = ""
    if len(paramstring) > 0:
        """
        If the user wants to build a job their request in paramstring should
        be something like "build jobname". We need to split the request out
        into the command and the job and pass them to callJenkinsAPI
        (not also true for list if they want to return the contents of a non
        root directory in Jenkins)
        """
        if paramstring.find(" ") != -1:
            params = paramstring.split(" ")
            output = callJenkinsApi( params[0], params[1] )
        else:
            output = callJenkinsApi( "list", "" )
        
    else:
        output = callJenkinsApi( "help", "" )
    
    """
    Create data json object to return to Mattermost with
        response_type = in_channel (everyone sees) or ephemeral (only sender sees)
        text = the message to send
    """
    data = {
        "response_type": "in_channel",
        "text": output,
    }
    
    """
    Create the response object to send to Mattermost with the
    data object written as json, 200 status, and proper mimetype
    """
    response = app.response_class(
        response = json.dumps(data),
        status = 200,
        mimetype = 'application/json'
    )
    return response
 
 
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5002, debug = False)