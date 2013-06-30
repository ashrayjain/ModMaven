import json
import prereqs_parser
import urllib2

print "Data loading..."
modData_NUSmods = json.load(urllib2.urlopen("http://nusmods.com/json/mod_info.json"))
print "Data Loaded!"
modData = {}

for mod in modData_NUSmods['cors']:
    modData[mod] = modData_NUSmods['cors'][mod]
    if 'prerequisite' in modData[mod]:
        modData[mod]['prerequisite'] = prereqs_parser.getPrereq(modData[mod]['prerequisite'])
    else:
        modData[mod]['prerequisite'] = []

with open('data/modInfo.json', 'w') as outfile:
    json.dump(modData, outfile, indent=2)

