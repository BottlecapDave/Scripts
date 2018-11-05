#!/usr/bin/python

import argparse, copy, json, requests, sys, time

def get_templates(token, suffix, targetSuffix, prefix):
    auth = {"Authorization": "Bearer " + token}
    response = requests.get("https://api.sendgrid.com/v3/templates?generations=dynamic", headers=auth)

    jsonResponse = response.json()
    if "templates" in jsonResponse:
        templates = jsonResponse["templates"]

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
    else:
        raise ValueError("Unable to retrieve templates")

def clone_templates(token, currentTemplates, targetTemplates, suffix, targetSuffix):
    for template in currentTemplates:
        templateName = template["name"][:len(suffix) * -1]

        targetTemplateName = templateName + targetSuffix
        targetTemplate = get_template(targetTemplates, targetTemplateName)
        if targetTemplate == None:
            targetTemplate = create_template(token, targetTemplateName, template)
        
        print("Creating new version for", template["name"])
        create_version(token, template, targetTemplate)

def get_template(templates, targetTemplateName):
    for template in templates:
        if template["name"].lower() == targetTemplateName.lower():
            return template
    
    return None

def create_version(token, templateToClone, targetTemplate):
    activeVersionToClone = get_active_version(templateToClone)
    activeVersionToCloneContent = get_version_content(token, templateToClone["id"], activeVersionToClone["id"])

    createNewVersion = False
    activeTargetVersion = get_active_version(targetTemplate)
    if activeTargetVersion != None:
        activeTargetVersionContent = get_version_content(token, targetTemplate["id"], activeTargetVersion["id"])

        if activeVersionToCloneContent["subject"] != activeTargetVersionContent["subject"] or activeVersionToCloneContent["html_content"] != activeTargetVersionContent["html_content"] or activeVersionToCloneContent["plain_content"] != activeTargetVersionContent["plain_content"]:
           createNewVersion = True
    else:
        createNewVersion = True

    if createNewVersion == True:
        print("Creating new version...", end="")
        newVersion = copy.copy(activeVersionToCloneContent)
        newVersion["template_id"] = targetTemplate["id"]
        newVersion["name"] = "Untitled_" + str(time.time() * 1000)

        auth = {"Authorization": "Bearer " + token}
        response = requests.post("https://api.sendgrid.com/v3/templates/" + targetTemplate["id"] + "/versions", data=json.dumps(newVersion), headers=auth)
        response = response.json()

        if "id" in response:
            print("Complete")
            return response
        else:
            raise ValueError("Failed to create new template version")
    else:
        print("Skipping new version")

def get_active_version(templates):
    for version in templates["versions"]:
        if version["active"] == 1:
            return version

    return None

def get_version_content(token, templateId, versionId):
    print("Retrieving content of version", versionId, "for", templateId, "...", end="")

    auth = {"Authorization": "Bearer " + token}
    response = requests.get("https://api.sendgrid.com/v3/templates/" + templateId + "/versions/" + versionId, headers=auth)
    response = response.json()

    if "id" in response:
        print("Complete")
        return response
    else:
        raise ValueError("Failed to retrieve template content")

def create_template(token, name, templateToClone):
    print("Creating template for", name, "...", end="")
    
    auth = {"Authorization": "Bearer " + token}
    payload = {"name": name, "generation": templateToClone["generation"]}
    response = requests.post("https://api.sendgrid.com/v3/templates", data=json.dumps(payload), headers=auth)
    response = response.json()

    if "id" in response:
        print("complete")
        return response
    else:
        raise ValueError("Failed to create template")

def main(argv):
    parser = argparse.ArgumentParser(description='Clones the SendGrid active templates into a sibling template of the same name')
    parser.add_argument('apitoken', type=str, help='The api token for contacting SendGrid')
    parser.add_argument('suffix', type=str, help='The suffix that is present on the templates that is to be cloned')
    parser.add_argument('targetsuffix', type=str, help='The target suffix of the cloned templates')
    parser.add_argument('-p', '-prefix', dest='prefix', type=str, help='The prefix that is present on the templates that is to be cloned', required=False)

    args = parser.parse_args(argv)

    currentTemplates, targetTemplates = get_templates(args.apitoken, args.suffix, args.targetsuffix, args.prefix)
    clone_templates(args.apitoken, currentTemplates, targetTemplates, args.suffix, args.targetsuffix)

if  __name__ =='__main__':
    main(sys.argv[1:])