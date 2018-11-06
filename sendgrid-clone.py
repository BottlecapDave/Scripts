#!/usr/bin/python

import argparse, copy, json, requests, sys, time

class SendGridClient:
    def __init__(self, token):
        self.token = token
    
    def get_templates(self):
        auth = {"Authorization": "Bearer " + self.token}
        response = requests.get("https://api.sendgrid.com/v3/templates?generations=dynamic", headers=auth)

        jsonResponse = response.json()
        if "templates" in jsonResponse:
            return jsonResponse["templates"]
        else:
            raise ValueError("Unable to retrieve templates")
    
    def create_version(self, templateId, baseVersion):
        newVersion = copy.copy(baseVersion)
        newVersion["template_id"] = templateId
        newVersion["name"] = "Untitled_" + str(time.time() * 1000)

        auth = {"Authorization": "Bearer " + self.token}
        response = requests.post("https://api.sendgrid.com/v3/templates/" + templateId + "/versions", data=json.dumps(newVersion), headers=auth)
        response = response.json()

        if "id" in response:
            return response
        else:
            raise ValueError("Failed to create new template version")

    def get_versions(self, templateId, versionId):
        auth = {"Authorization": "Bearer " + self.token}
        response = requests.get("https://api.sendgrid.com/v3/templates/" + templateId + "/versions/" + versionId, headers=auth)
        response = response.json()

        if "id" in response:
            return response
        else:
            raise ValueError("Failed to retrieve template content")

    def create_template(self, name, generation):
        auth = {"Authorization": "Bearer " + self.token}
        payload = {"name": name, "generation": generation}
        response = requests.post("https://api.sendgrid.com/v3/templates", data=json.dumps(payload), headers=auth)
        response = response.json()

        if "id" in response:
            return response
        else:
            raise ValueError("Failed to create template")

def retrieve_templates(client, suffix, targetSuffix, prefix):
    templates = client.get_templates()
    print("Finding templates that match prefix and suffix...")

    currentTemplates = []
    targetTemplates = []
    for template in templates:
        name = template["name"].lower()
        if ((prefix != None and name.startswith(prefix.lower())) or prefix == None):
            if name.endswith(suffix.lower()):
                currentTemplates.append(template)
                continue
            if name.endswith(targetSuffix.lower()):
                targetTemplates.append(template)
                continue

    print(len(currentTemplates), "current template(s) found")
    print(len(targetTemplates), "target template(s) found")
    
    return currentTemplates, targetTemplates

def clone_templates(client, currentTemplates, targetTemplates, sourcesuffix, targetSuffix):
    for template in currentTemplates:
        templateName = template["name"][:len(sourcesuffix) * -1]

        targetTemplateName = templateName + targetSuffix
        targetTemplate = find_template(targetTemplates, targetTemplateName)
        if targetTemplate == None:
            targetTemplate = create_template(client, targetTemplateName, template)
        
        print("Creating new version for", template["name"])
        create_version(client, template, targetTemplate)

def find_template(templates, targetTemplateName):
    for template in templates:
        if template["name"].lower() == targetTemplateName.lower():
            return template
    
    return None

def create_version(client, templateToClone, targetTemplate):
    activeVersionToClone = find_active_version(templateToClone)
    activeVersionToCloneContent = client.get_versions(templateToClone["id"], activeVersionToClone["id"])

    createNewVersion = False
    activeTargetVersion = find_active_version(targetTemplate)
    if activeTargetVersion != None:
        activeTargetVersionContent = client.get_versions(targetTemplate["id"], activeTargetVersion["id"])

        if activeVersionToCloneContent["subject"] != activeTargetVersionContent["subject"] or activeVersionToCloneContent["html_content"] != activeTargetVersionContent["html_content"] or activeVersionToCloneContent["plain_content"] != activeTargetVersionContent["plain_content"]:
           createNewVersion = True
    else:
        createNewVersion = True

    if createNewVersion == True:
        print("Creating new version...", end="")
        newVersion = client.create_version(targetTemplate["id"], activeVersionToCloneContent)
        if newVersion != None:
            print("Complete")
            return newVersion
    else:
        print("Skipping new version")

def find_active_version(templates):
    for version in templates["versions"]:
        if version["active"] == 1:
            return version

    return None

def create_template(client, name, templateToClone):
    print("Creating template for", name, "...", end="")

    newTemplate = client.create_template(name, templateToClone["generation"])
    if (newTemplate != None):
        print("complete")
        return newTemplate

def main(argv):
    parser = argparse.ArgumentParser(description='Clones the SendGrid active templates into a sibling template of the same name')
    parser.add_argument('apitoken', type=str, help='The api token for contacting SendGrid')
    parser.add_argument('sourcesuffix', type=str, help='The suffix that is present on the templates that are to be cloned')
    parser.add_argument('targetsuffix', type=str, help='The target suffix of the cloned templates')
    parser.add_argument('-p', '-prefix', dest='prefix', type=str, help='The prefix that is present on the templates that is to be cloned', required=False)

    args = parser.parse_args(argv)

    client = SendGridClient(args.apitoken)

    currentTemplates, targetTemplates = retrieve_templates(client, args.sourcesuffix, args.targetsuffix, args.prefix)
    clone_templates(client, currentTemplates, targetTemplates, args.sourcesuffix, args.targetsuffix)

if  __name__ =='__main__':
    main(sys.argv[1:])