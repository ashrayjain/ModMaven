import json
import prereqs_parser
import urllib2
from bs4 import BeautifulSoup
import lxml

modData = {}
modlist = []
modExceptions = {
    'PH2216 / GEK2031': 'GEK2031'
}
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
    if mod in modExceptions:
        mod = modExceptions[mod]
        module["ModuleCode"] = mod
    modData[mod] = module
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


def scrapeIVLE(soup):
    tag = soup.find(id="viewtbl").find_all("td")
    key = None
    module = ""
    for ele in tag:
        if not key:
            if ele.string == "Module Code":
                key = "ModuleCode"
            elif ele.string == "Module Title":
                key = "ModuleTitle"
            elif ele.string == "Description":
                key = "ModuleDescription"
            elif ele.string == "Module Credit":
                key = "ModuleCredit"
            elif ele.string == "Workload":
                key = "Workload"
            elif ele.string == "Prerequisites":
                key = "Prerequisite"
            elif ele.string == "Preclusions":
                key = "Preclusion"
        else:
            if key == "ModuleCode":
                module = ele.string
                modData[module] = {}
            modData[module][key] = ele.string
            key = None
    modData[module]["ExamDate"] = "Not Applicable."
    modData[module]["Timetable"] = "Not Applicable."
    modlist.append(module)

print "Data loading...11/12 Sem1"
for module in json.load(urllib2.urlopen("http://api.nusmods.com/2011-2012/1/corsBiddingStatsRaw.json")):
    if module["ModuleCode"] not in modData:
        scrapeIVLE(BeautifulSoup(urllib2.urlopen(
            "http://ivle7.nus.edu.sg/lms/Account/NUSBulletin/msearch_view.aspx?acadYear=2011/2012&semester={0}&modeCode={1}".format(
                1, module["ModuleCode"])
        ), "lxml"))

print "Data Loaded!"
print "Data loading...11/12 Sem2"

for module in json.load(urllib2.urlopen("http://api.nusmods.com/2011-2012/2/moduleTimetableDeltaRaw.json")):
    if module["ModuleCode"] not in modData:
        scrapeIVLE(BeautifulSoup(urllib2.urlopen(
            "http://ivle7.nus.edu.sg/lms/Account/NUSBulletin/msearch_view.aspx?acadYear=2011/2012&semester={0}&modeCode={1}".format(
                2, module["ModuleCode"])
        ), "lxml"))
print "Data Loaded!"

print "Prereqs Parsing!!"
for mod in modData:
    modData[mod]["Prerequisite"] = prereqs_parser.getPrereq(modData[mod]["Prerequisite"], mod, modData) if "Prerequisite" in modData[mod] else "Not Available."
    # if type(modData[mod]['Prerequisite']) == str and len(modData[mod]['Prerequisite']) > 9:
    #     print modData[mod]['Prerequisite']

print "Prereqs done!"
print "Tree Creation started!!"
for mod in modData:
    modData[mod]["Tree"] = getTree(mod)
print "Tree Creation done!!"

modlist.sort()
modData['ModList'] = modlist

with open("data/modInfo.json", "w") as outfile:
    json.dump(modData, outfile)
