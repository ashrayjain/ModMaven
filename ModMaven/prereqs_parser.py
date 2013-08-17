import re

# List of operators
operators = [' and ', ' or ']

# Default Value for Comma when nothing is specified
# A, B ==> A and B
defaultCommaOp = ' and '

# Precedence of Operators (0 ==> lowest)
_pre = {' and ': 0, ' or ': 1}

modString = '(?:[A-Z]{2,3}|MUT |CE |ME |MUA )[0-9]{4}(?:[A-Z]|[A-Z]R)?'
verifyRE = re.compile(modString)
modRE = re.compile(modString + '|' + '|'.join(operators) + '|[\(\)\[\]\{\}]')
parenRE = re.compile('[\{\}\[\]]')
slashRE = re.compile('[/]')
colonRE = re.compile(';')
andRE = re.compile('&')
commaRE = re.compile(modString + ', ')
commaFixRE = re.compile(modString + ', |' + '|'.join(operators))

# Add any Key-words for which NO parsing should be done and the entire
# pre-req string should be shown instead
restricted = ['USP', 'Cohort', 'AY20', 'H2 ', 'Qualifying English Test', 'MCs', 'grade', 'Grade', 'H1 ', 'A-level']
restrictedRE = re.compile('|'.join(restricted))

# Add any special Exceptions here in the following format
# The specified value will be shown if the given key is encountered
# as a prereq
# key = EXACT pre-requisite string to match
# value = parsed output
exceptions = {
    'Pass 80 MCs and [CS3240, IS2150, IS3230 and IS3150]':
        {' and ': ['CS3240', 'IS2150', 'IS3230', 'IS3150']},
    'CS2261 or IS2103 (applicable to intakes from AY2005/06 to AY2007/08) or [(CS2261 or IS2103) and (CS2301 or IS2101)] (applicable to intakes from AY2008/09 onwards)':
        {' and ': ['IS2103', 'IS2101']},
    'For Applied Chemistry Students: Polymer Chemistry II (CM3265). For Chemistry students: Organic Reaction Mechanisms (CM3221).':
        'For Applied Chemistry Students: Polymer Chemistry II (CM3265). For Chemistry students: Organic Reaction Mechanisms (CM3221).',
    'Pass ID 2105 & 2106': {' and ': ['ID2105', 'ID2106']},
    'Pass ID 1105 & 1106': {' and ': ['ID1105', 'ID1106']},
    'Pass ID 3105 & 3106': {' and ': ['ID3105', 'ID3106']}
}


def getNext(iterator):
    try:
        return iterator.next()
    except:
        return None


def precedence(val, stack):
    return _pre[val] <= _pre[stack[len(stack) - 1]]


def isOperator(val):
    return any([True for op in operators if val == op])


def isOperand(val):
    return val not in operators and val not in '()'


def replaceParen(m):
    if m.group() in '{[':
        return '('
    return ')'


def getDict(data, Next=False):
    try:
        for ele in data:
            if isinstance(ele, dict):
                if not Next:
                    return ele
                else:
                    Next = False
    except:
        return None


def postProcess(data):
    keyToMatch = data.keys()[0]
    values = data[keyToMatch]
    done = False
    innerDict = getDict(values)
    while innerDict and not done:
        done = True
        if keyToMatch == innerDict.keys()[0]:
            values.remove(innerDict)
            values = data[keyToMatch] = innerDict.values()[0] + values
            done = False
            innerDict = getDict(values)

    for val in values:
        if isinstance(val, dict):
            postProcess(val)


def getModifier(results):
    retval = defaultCommaOp
    for ele in results:
        if ele in operators:
            retval = ele
    return retval


def commaFix(prereq, commaResult):
    results = commaFixRE.findall(prereq)
    results.reverse()

    while len(commaResult):
        val = commaResult[0]

        prereq = re.sub(val, val[:-2] + getModifier(results[:results.index(val)]), prereq, 1)
        commaResult.pop(0)

    return prereq


def preProcess(prereq, mod):
    if restrictedRE.findall(prereq):
        return None
    prereq = parenRE.sub(replaceParen, prereq)
    prereq = slashRE.sub(' or ', prereq)
    prereq = colonRE.sub(' and ', prereq)
    prereq = andRE.sub(' and ', prereq)
    commaResult = commaRE.findall(prereq)
    if len(commaResult):
        prereq = commaFix(prereq, commaResult)
    prereq = re.sub(mod, "", prereq)
    prereq = re.sub("MUT ", "MUT", prereq)
    prereq = re.sub("CE ", "CE", prereq)
    prereq = re.sub("ME ", "ME", prereq)
    prereq = re.sub("MUA ", "MUA", prereq)
    return prereq


def getInterpretedResult(prereq, data):
    stack = []
    result = []
    modRE_results = modRE.findall(prereq)

    dirtyLast = False
    i = 0
    while i < len(modRE_results):
        val = modRE_results[i]
        if not (verifyRE.match(val) and val not in data) and not dirtyLast:
            dirtyLast = False
            if isOperand(val):
                result += [val]
            elif val == '(':
                stack.append(val)
            elif val == ')':
                while len(stack) and stack[len(stack) - 1] != '(':
                    result.append(stack.pop())
                if len(stack):
                    stack.pop()
            elif i and i < len(modRE_results) - 1 \
                and not isOperator(modRE_results[i - 1]) \
                and not isOperator(modRE_results[i + 1]) \
                and modRE_results[i + 1] != ')':
                if not len(stack) or stack[len(stack) - 1] == '(':
                    stack.append(val)
                else:
                    while len(stack) and stack[len(stack) - 1] != '(' and precedence(val, stack):
                        result.append(stack.pop())
                    stack.append(val)
            else:
                modRE_results.pop(i)
                i -= 1
        else:
            dirtyLast = (dirtyLast == False)
        i += 1
    while len(stack):
        result.append(stack.pop())
    return result


def evalResult(interpretedResult):
    stack = []
    for val in interpretedResult:
        if isOperand(val):
            stack.append(val)
        elif len(stack):
            a = stack.pop()
            try:
                b = stack.pop()
                stack.append({val: [b, a]})
            except:
                stack.append(a)

    if len(stack):
        return stack.pop()
    return None


def noMod(result):
    for val in result:
        if verifyRE.match(val):
            return False
    return True


def getPrereq(prereq, mod, data):
    # Copy of Prereq
    orignalPrereq = '' + prereq
    if prereq in exceptions:
        return exceptions[prereq]

    prereq = preProcess(prereq, mod)

    if not prereq:
        return orignalPrereq

    interpretedResult = getInterpretedResult(prereq, data)

    if not interpretedResult or noMod(interpretedResult):
        return orignalPrereq

    evaluatedResult = evalResult(interpretedResult)

    if isinstance(evaluatedResult, dict) and len(evaluatedResult.keys()):
        postProcess(evaluatedResult)

    return evaluatedResult


preclusion_exceptions = {
    "XX3311": [
        "CM3311",
        "LSM3311",
        "MA3311",
        "PC3311",
        "QF3311",
        "ST3311",
        "ZB3311"
    ],
    "XX3312": [
        "QF3312",
        "PC3312",
        "CM3312",
        "MA3312",
        "ST3312",
        "PR3312"
    ]
}

manualPreclusions = {
    "CG1101": ["CS1010", "CS1010E"]
}


def getPreclusions(preclusion, mod, data):
    preclusions = verifyRE.findall(preclusion)
    for key in preclusion_exceptions.keys():
        if key in preclusions:
            preclusions.remove(key)
            preclusions.extend(preclusion_exceptions[key])
    if mod in preclusions:
        preclusions.remove(mod)
    if mod in manualPreclusions:
        preclusions.extend(manualPreclusions[mod])
    preclusions = set(preclusions)
    toRemove = []
    for module in preclusions:
        if module not in data:
            toRemove.append(module)
    return [pre for pre in preclusions if pre not in toRemove] if len(preclusions) != 0 else preclusion


# Not Using Coz Screwed Up Preclusion in IVLE Data,
# not safe to assume
def twoWayPreclusions(preclusion, data):
    if isinstance(preclusion, list):
        preclusion = set(preclusion)
        updates = set()
        for mod in preclusion:
            updates.update(data[mod]["Preclusion"])
        preclusion.update(updates)
        return list(preclusion)
    return preclusion
