import json
import prereqs_parser
import urllib2

# Return Tree for given mod with given prereqs
def traverseDict(root):
    children = []
    for entry in root.values()[0]:
        #print entry
        if isinstance(entry, dict):
            children += traverseDict(entry)
        else:
            children.append({"name": entry, "children": []}
            if entry not in modData else getTree(entry))
    return children


def getTree(mod):
    prereq = modData[mod]["prerequisite"]
 #   print "++++++++++++++++++++"+mod+"+++++++++++++++++++++"
    tree = {
        "name": mod,
        "children": []
    }
    if isinstance(prereq, dict):
        tree["children"] += traverseDict(prereq)
    elif not prereq:
        #print tree
        return tree
    elif len(prereq) < 10:
  #      print prereq
        tree["children"].append({"name": prereq, "children": []}
        if prereq not in modData else getTree(prereq))
    #print tree
    return tree


print "Data loading..."
modData_NUSmods = json.load(urllib2.urlopen("http://nusmods.com/2013-2014/sem1/v1/json/mod_info.json"))
print "Data Loaded!"
modData = {}
modlist = []

for mod in modData_NUSmods["cors"]:
    modData[mod] = modData_NUSmods["cors"][mod]
    if "prerequisite" in modData[mod]:
        modData[mod]["prerequisite"] = prereqs_parser.getPrereq(modData[mod]["prerequisite"], mod)
    else:
        modData[mod]["prerequisite"] = "Not Available."
    modlist.append(mod)

for mod in modData:
    modData[mod]["tree"] = getTree(mod)

modlist.sort()
modData['modlist'] = modlist

with open("data/modInfo.json", "w") as outfile:
    json.dump(modData, outfile, indent=2)
