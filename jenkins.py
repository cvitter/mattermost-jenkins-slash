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
    return


def createFolderUrl(foldersIn):
    """
    Takes a list of folders separated by '|' and returns the proper url
    """
    folderUrl = ""
    d = foldersIn.split("|")
    for folder in d:
        folderUrl += "job/" + folder + "/"
    return folderUrl


def createListOut(jsonIn):
    """
    Takes JSON document with list of items (jobs/folders) and returns markdown
    """
    markdown = "| Type | Name |\n"
    markdown += "|:-----|:-----|\n"
    for listItem in jsonIn["jobs"]:
        type = ""
        if listItem["_class"].endswith(".Folder"):
            type = "Folder"
        else:
            type = "Job"
        markdown += "| " + type + " | " + listItem["name"] + " |\n"
        
    print ( markdown )
    return markdown



def callJenkinsApi(jenkinsApi, jenkinsFolders, jenkinsArgs):
    """
    Call the Jenkins API and fetch the JSON response
        List jobs: api/json?tree=jobs[name]
        
    """ 
    #
    if jenkinsApi == "list":
        print ""
    elif jenkinsApi == "run":
        print ""
    else:
        print ""
        
    #
    folderUrl = ""
    if len(jenkinsFolders) > 0 :
        folderUrl = createFolderUrl(jenkinsFolders)
    
    # Build the URL for the API request
    targetUrl = jenkinsUrl + folderUrl + "api/json?tree=jobs[name]"
    
    print ( targetUrl )
    
    # Send API request to Jenkins server with authentication
    r = requests.get(targetUrl, auth=(username, password))
    
    
    createListOut(r.json())
    
    # Return the JSON response
    return r.text





def returnHelp():
    """
    """
    
    return ""


"""
------------------------------------------------------------------------------------------
Flask application below
"""

readConfig()

o = callJenkinsApi( "listJobs", "", "" )

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
