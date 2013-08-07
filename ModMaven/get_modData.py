import json
import prereqs_parser
import urllib2

modData = {}
modlist = []

def traverseDict(root):
    """Return Tree for given mod with given prereqs"""
    children = []
    items = root.items()
    for entry in items[0][1]:
        #print entry
        if isinstance(entry, dict):
            children += traverseDict(entry)
        else:
            children.append({"name": entry, "children": []} if entry not in modData else getTree(entry))

    return [{"name": items[0][0][1:-1], "children": children}]


def mergeSem2(mod, module):
    modData[mod]['ExamDate']['Sem2'] = module['ExamDate'] if 'ExamDate' in module else "No Exam."
    modData[mod]['Timetable']['Sem2'] = module['Timetable'] if 'Timetable' in module else "Not Available."


def getTree(mod):
    prereq = modData[mod]["Prerequisite"]
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


def addMod(mod, module, sem):
    modData[mod] = module
    modData[mod]["Prerequisite"] = prereqs_parser.getPrereq(modData[mod]["Prerequisite"], mod) if "Prerequisite" in module else "Not Available."
    modData[mod].update(ExamDate={sem: module['ExamDate'] if "ExamDate" in module else "No Exam."} if sem else "Not Applicable.")
    modData[mod].update(Timetable={sem: module['Timetable'] if "Timetable" in module else "Not Available."} if sem else "Not Applicable.")
    modlist.append(mod)


print "Data loading...13/14 Sem1"
for module in json.load(urllib2.urlopen("http://api.nusmods.com/2013-2014/1/modules.json")):
    addMod(module['ModuleCode'], module, "Sem1")
print "Data Loaded!"

print "Data loading...13/14 Sem2"
for module in json.load(urllib2.urlopen("http://api.nusmods.com/2013-2014/2/modules.json")):
    if module['ModuleCode'] in modData:
        #print module, modData[module['ModuleCode']]
        mergeSem2(module['ModuleCode'], module)
    else:
        addMod(module['ModuleCode'], module, "Sem2")
print "Data Loaded!"

print "Data loading...12/13 Sems"
for module in json.load(urllib2.urlopen("http://api.nusmods.com/2012-2013/1/modules.json")):
    if module['ModuleCode'] not in modData:
        addMod(module['ModuleCode'], module, None)

for module in json.load(urllib2.urlopen("http://api.nusmods.com/2012-2013/2/modules.json")):
    if module['ModuleCode'] not in modData:
        addMod(module['ModuleCode'], module, None)

print "Data Loaded!"

for mod in modData:
    modData[mod]["Tree"] = getTree(mod)

modlist.sort()
modData['ModList'] = modlist

with open("data/modInfo.json", "w") as outfile:
    json.dump(modData, outfile, indent=2)
