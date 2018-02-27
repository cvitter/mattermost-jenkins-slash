from flask import Flask
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

#o = callJenkinsApi( "help", "" )
#o = callJenkinsApi( "list", "" )
o = callJenkinsApi( "build", "mattermost-test-1" )

print (o)




# app = Flask(__name__)
# 
# @app.route( "/jenkins", methods = [ 'GET', 'POST' ] )
# def slashCommand():
#         return "Jenkins"
# 
# 
# if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000, debug = False)
