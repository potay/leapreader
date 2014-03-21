import lib.Leap as Leap
import DB
import LeapReader
import time
import random
from Struct import Struct

class LeapReader(object):
    # Main class of the program. Contains all the data in the model.

    ########################
    ## Controller Methods
    ########################

    def getUserInput(self, msg, nextLine=True):
        # Basic raw input controller method.
        nl = "\n" if (nextLine == True) else ""
        userInput = raw_input(msg+nl)
        return userInput

    ########################
    ## Viewer Methods
    ########################

    def message(self, msg="", nextLine=True):
        # Just a normal generic print for now.
        print msg,
        if nextLine == True: print

    #########################
    ## Database Model Methods
    #########################

    def dbStore(self, table, data, isInstanceVariable=True):
        # Data can either be locally stored in instance's data structure, or
        # passed from an an external source. However, it must be a list of
        # values or variable names.
        if (isInstanceVariable == True):
            values = []
            for name in data:
                values.append(eval("self.data."+name))
        else:
            values = data

        self.db = DB.Database(self.database, self.debug)

        result = self.db.store(table, values)
        self.db.close()
        return result


    #########################
    ## Model Methods
    #########################

    def getStoredData(self):
        self.db = DB.Database(self.database, self.debug)
        result = self.db.get(["*"], "data")
        self.db.close()
        return result

    def record(self, duration, countdown=5):
        startTime = time.time()
        count = 0

        # Commences the countdown to let user get ready.
        while ((countdown - count) > 0):
            if ((time.time() - startTime) > count):
                count += 1
                if self.debug == True: self.message(countdown - count + 1,
                    False)
        if self.debug == True: self.message()

        # Start recording
        if self.debug == True: self.message("Recording...")
        result = self.getFrameData(duration)

        # Data handing
        if self.debug: self.message(result)
        self.data.tempRecordData = result

    def delTempRecordData(self):
        self.data.tempRecordData = dict()
        return True

    def saveRecordData(self, word):
        data = self.data.tempRecordData
        data["word"] = word
        dataList = []
        for data in self.dataFields:
            dataList.append("tempRecordData['"+data[0]+"']")
        self.db = DB.Database(self.database, self.debug)
        result = self.dbStore("data", dataList)
        if (result == False):
            self.errMsg = self.db.errMsg
            self.db.close()
            return False
        else:
            self.errMsg = ""
            data = dict()
            self.db.close()
            return True

    def saveFingersMetric(self, isLeft):
        data = self.data.tempRecordData
        if ((data['finger15Length'] <= 0) or (data['finger15Width'] <= 0) or
           (data['finger14Length'] <= 0) or (data['finger14Width'] <= 0) or
           (data['finger13Length'] <= 0) or (data['finger13Width'] <= 0) or
           (data['finger12Length'] <= 0) or (data['finger12Width'] <= 0) or
           (data['finger11Length'] <= 0) or (data['finger11Width'] <= 0)):
           return False
        if (isLeft == True):
            print "Thumb:", data['finger15Length'], data['finger15Width'], data['finger15Length']/data['finger15Width']
            print "Index:", data['finger14Length'], data['finger14Width'], data['finger14Length']/data['finger14Width']
            print "Middle:", data['finger13Length'], data['finger13Width'], data['finger13Length']/data['finger13Width']
            print "Ring:", data['finger12Length'], data['finger12Width'], data['finger12Length']/data['finger12Width']
            print "Pinky:", data['finger11Length'], data['finger11Width'], data['finger11Length']/data['finger11Width']
            if (self.data.det['fingerRatios'][0] != 0):
                self.data.det['fingerRatios'] = [(data['finger15Length']/data['finger15Width']+self.data.det['fingerRatios'][0])/2,
                                                 (data['finger14Length']/data['finger14Width']+self.data.det['fingerRatios'][0])/2,
                                                 (data['finger13Length']/data['finger13Width']+self.data.det['fingerRatios'][0])/2,
                                                 (data['finger12Length']/data['finger12Width']+self.data.det['fingerRatios'][0])/2,
                                                 (data['finger11Length']/data['finger11Width']+self.data.det['fingerRatios'][0])/2]
            else:
                self.data.det['fingerRatios'] = [(data['finger15Length']/data['finger15Width']),
                                                 (data['finger14Length']/data['finger14Width']),
                                                 (data['finger13Length']/data['finger13Width']),
                                                 (data['finger12Length']/data['finger12Width']),
                                                 (data['finger11Length']/data['finger11Width'])]
            return True
        else:
            print "Thumb:", data['finger11Length'], data['finger11Width'], data['finger11Length']/data['finger11Width']
            print "Index:", data['finger12Length'], data['finger12Width'], data['finger12Length']/data['finger12Width']
            print "Middle:", data['finger13Length'], data['finger13Width'], data['finger13Length']/data['finger13Width']
            print "Ring:", data['finger14Length'], data['finger13Width'], data['finger14Length']/data['finger14Width']
            print "Pinky:", data['finger15Length'], data['finger14Width'], data['finger15Length']/data['finger15Width']
            if (self.data.det['fingerRatios'] != 0):
                self.data.det['fingerRatios'] = [(data['finger11Length']/data['finger11Width']+self.data.det['fingerRatios'][0])/2,
                                                 (data['finger12Length']/data['finger12Width']+self.data.det['fingerRatios'][0])/2,
                                                 (data['finger13Length']/data['finger13Width']+self.data.det['fingerRatios'][0])/2,
                                                 (data['finger14Length']/data['finger14Width']+self.data.det['fingerRatios'][0])/2,
                                                 (data['finger15Length']/data['finger15Width']+self.data.det['fingerRatios'][0])/2]
            else:
                self.data.det['fingerRatios'] = [(data['finger11Length']/data['finger11Width']),
                                                 (data['finger12Length']/data['finger12Width']),
                                                 (data['finger13Length']/data['finger13Width']),
                                                 (data['finger14Length']/data['finger14Width']),
                                                 (data['finger15Length']/data['finger15Width'])]
            return True

    def translateRecordData(self):
        # Translates the recorded data by finding the best match.
        # Right now we are merely using SQL queries with range conditions as
        # filters. Can be improved with a smarter matching algorithm using
        # heuristics.

        # We start out by doing an exact search. Which will most probably fail.
        where = []
        for data in self.data.tempRecordData:
            where.append("("+str(data)+"="+\
                str(self.data.tempRecordData[data])+")")
        self.db = DB.Database(self.database, self.debug)
        result = self.db.get(["word"], "data", where)

        # If exact search fails, we do a ranged search. The margin of lenience
        # is defined in init.
        if (result == []):
            where = []
            for data in self.data.tempRecordData:
                if (data not in self.data.det['translateExclude']):
                    lowerLimit = max(0,
                        self.data.tempRecordData[data]-self.data.epsilon[data])
                    upperLimit = max(lowerLimit,
                        self.data.tempRecordData[data]+self.data.epsilon[data])
                    where.append("("+str(data)+" BETWEEN "+str(lowerLimit)+\
                        " AND "+str(upperLimit)+")")
            result = self.db.get(["word"], "data", where)
            if (result == []):
                self.errMsg = self.db.errMsg
                self.db.close()
                return False
            else:
                self.errMsg = ""
                data = dict()
                self.db.close()
                return random.choice(result)[0]
        else:
            self.errMsg = ""
            data = dict()
            self.db.close()
            return random.choice(result)[0]

    def getFrameData(self, duration):
        startTime = time.time()
        count = 0
        result = dict()
        dataDict = dict()
        for data in self.dataFields:
            dataDict[data[0]] = []

        # We collect the data for a certain duration and store data in our dict
        while (time.time() - startTime < duration):
            if ((time.time() - startTime) > count):
                count += 1
                if self.debug == True: self.message(duration - count + 1, False)

            frame = self.controller.frame()

            # First we are going to get the two hands and their corresponding
            # number of fingers

            def getLeftAndRightHands(hands):
                if isinstance(hands, Leap.HandList):
                    if hands.is_empty:
                        return False, False
                    elif(len(hands) < 2):
                        return hands[0], False
                    else:
                        leftHand = hands[0]
                        rightHand = hands[1]
                        for i in range(1, len(hands)):
                            if(hands[i].palm_position.x<\
                                leftHand.palm_position.x):
                                leftHand = hands[i]
                                rightHand = hands[(i+1)%2]
                        return leftHand, rightHand
                else:
                    self.errMsg = "There wasn't a list of hands???"
                    return False, False

            def getHandFingers(hand, isLeft):
                fingers = hand.fingers
                if not fingers.is_empty:
                    # Calculate the hand's average finger tip position
                    #fingersDict = {1:False, 2:False, 3:False, 4:False, 5:False}
                    fingersList = []
                    direction = -1 if (isLeft == True) else 1
                    #direction = 1
                    for finger in fingers:
                        i = 0
                        while ((len(fingersList) != 0) and
                            (len(fingersList) <= i) and
                            (finger.tip_position.x*direction < \
                            fingersList[i].tip_position.x*direction)):
                            i += 1
                        fingersList = fingersList[:i]+[finger]+fingersList[i:]
                        #fingersList.append(finger)
                    if self.debug: print fingersList
                    #totalFingerCount = 5
                    #if (len(fingersList) <= totalFingerCount):
                    fingersDict = mapFingersToHand(fingersList)
                    if self.debug: print fingersDict
                    return fingersDict
                else:
                    return dict()

            ### Mapping Algorithm v1 ###

            def mapFingersToHand(fingersList):
                # Finding the best possible fingers to finger spots map.
                # If we have 5 fingers, we assume that the x-axis distribution
                # is accurate as we are limiting this software to flat signs.
                # As such we just return that in a map.
                if (len(fingersList) == 5):
                    fingersDict = dict()
                    i = 1
                    for finger in fingersList:
                        fingersDict[i] = finger
                        i += 1
                    return fingersDict
                else:
                    # If not we have to map the fingers to the best possible
                    # spots. We do this by calculating the arrangement which
                    # would give us the least error according to our heuristic.
                    totalFingers = 5
                    numOfFingers = len(fingersList)
                    emptySpots = (totalFingers-numOfFingers)
                    initCombi = "0"*emptySpots
                    # Getting all combinations
                    combinations = getFingerCombinations(initCombi,
                        numOfFingers)
                    fingerErrDict = dict()
                    for combination in combinations:
                        # Our current heuristic is based on the length/width
                        # ratio of fingers. We find the best combination such
                        # that its length/width ratio is the closest match
                        # to the model length/width ratio for that combination.
                        accuracyError = 0
                        i = 0
                        for j in xrange(len(combination)):
                            if (combination[j] == str(1)):
                                accuracyError += abs((fingersList[i].length/\
                                    fingersList[i].width) - \
                                self.data.det['fingerRatios'][j])
                                i += 1
                        fingerErrDict[combination] = accuracyError
                    bestMap = min(fingerErrDict, key=fingerErrDict.get)
                    # Now we map it out and return the map.
                    fingersDict = dict()
                    j = 0
                    for i in xrange(len(bestMap)):
                        if (bestMap[i] == str(1)):
                            fingersDict[i+1] = fingersList[j]
                            j += 1
                        else:
                            fingersDict[i+1] = False
                    return fingersDict

            def getFingerCombinations(combination, numOfFingers):
                # Recursive function which finds all the possible combinations
                # that a number of fingers can position themselves on a hand
                if (numOfFingers < 1):
                    return [combination]
                else:
                    spots = len(combination)+1
                    combinations = []
                    for i in xrange(spots):
                        newCombi = combination[:i]+"1"+combination[i:]
                        combinations += getFingerCombinations(newCombi,
                            numOfFingers-1)
                    return set(combinations)


            leftHand, rightHand = getLeftAndRightHands(frame.hands)
            # Left shall always be 1, Right shall be 2.
            def addData(dataDict, hand, leftHand):
                handFingers = getHandFingers(hand, leftHand)
                i = 1 if leftHand else 2
                dataDict["hand"+str(i)].append(float(sum(1 for value in \
                    handFingers.values() if value)))
                dataDict["palm"+str(i)+"PositionX"].append(hand.palm_position.x)
                dataDict["palm"+str(i)+"PositionY"].append(hand.palm_position.y)
                dataDict["palm"+str(i)+"PositionZ"].append(hand.palm_position.z)
                dataDict["palm"+str(i)+"NormalX"].append(hand.palm_normal.x)
                dataDict["palm"+str(i)+"NormalY"].append(hand.palm_normal.y)
                dataDict["palm"+str(i)+"NormalZ"].append(hand.palm_normal.z)
                dataDict["palm"+str(i)+"DirectionX"].append(hand.direction.x)
                dataDict["palm"+str(i)+"DirectionY"].append(hand.direction.y)
                dataDict["palm"+str(i)+"DirectionZ"].append(hand.direction.z)
                for finger in handFingers:
                    if handFingers[finger]:
                        dataDict["finger"+str(i)+str(finger)+"Length"].\
                        append(handFingers[finger].length)
                        dataDict["finger"+str(i)+str(finger)+"Width"].\
                        append(handFingers[finger].width)
                        dataDict["finger"+str(i)+str(finger)+"DirectionX"].\
                        append(handFingers[finger].direction.x)
                        dataDict["finger"+str(i)+str(finger)+"DirectionY"].\
                        append(handFingers[finger].direction.y)
                        dataDict["finger"+str(i)+str(finger)+"DirectionZ"].\
                        append(handFingers[finger].direction.z)
                        dataDict["finger"+str(i)+str(finger)+"TipPosX"].\
                        append(handFingers[finger].tip_position.x)
                        dataDict["finger"+str(i)+str(finger)+"TipPosY"].\
                        append(handFingers[finger].tip_position.x)
                        dataDict["finger"+str(i)+str(finger)+"TipPosZ"].\
                        append(handFingers[finger].tip_position.x)

            if(leftHand):
                addData(dataDict, leftHand, True)

            if(rightHand):
                addData(dataDict, rightHand, False)

        if self.debug == True: self.message()

        # For each data type, we find the average.
        for data in dataDict:
            if len(dataDict[data]) > 0:
                result[data] = round(reduce(lambda x, y: x + y, dataDict[data])\
                 / float(len(dataDict[data])))
            else:
                result[data] = 0

        # Return the rresult
        return result

    def mainInit(self):
        # Model Data Initiation

        # Define the controller
        self.controller = Leap.Controller()
        if self.database == None:
            self.database = "leapReader.db"

        if (self.database != None):
            # Start out database connection
            self.db = DB.Database(self.database, self.debug)

            # Check to see if required tables are there. If not we create them.
            self.dataFields = [
                                ("word", "TEXT"),
                                ("hand1", "INT"),
                                ("hand2", "INT"),
                                ("palm1PositionX", "REAL"),
                                ("palm1PositionY", "REAL"),
                                ("palm1PositionZ", "REAL"),
                                ("palm2PositionX", "REAL"),
                                ("palm2PositionY", "REAL"),
                                ("palm2PositionZ", "REAL"),
                                ("palm1NormalX", "REAL"),
                                ("palm1NormalY", "REAL"),
                                ("palm1NormalZ", "REAL"),
                                ("palm2NormalX", "REAL"),
                                ("palm2NormalY", "REAL"),
                                ("palm2NormalZ", "REAL"),
                                ("palm1DirectionX", "REAL"),
                                ("palm1DirectionY", "REAL"),
                                ("palm1DirectionZ", "REAL"),
                                ("palm2DirectionX", "REAL"),
                                ("palm2DirectionY", "REAL"),
                                ("palm2DirectionZ", "REAL"),
                                ("finger11Length", "REAL"),
                                ("finger12Length", "REAL"),
                                ("finger13Length", "REAL"),
                                ("finger14Length", "REAL"),
                                ("finger15Length", "REAL"),
                                ("finger21Length", "REAL"),
                                ("finger22Length", "REAL"),
                                ("finger23Length", "REAL"),
                                ("finger24Length", "REAL"),
                                ("finger25Length", "REAL"),
                                ("finger11Width", "REAL"),
                                ("finger12Width", "REAL"),
                                ("finger13Width", "REAL"),
                                ("finger14Width", "REAL"),
                                ("finger15Width", "REAL"),
                                ("finger21Width", "REAL"),
                                ("finger22Width", "REAL"),
                                ("finger23Width", "REAL"),
                                ("finger24Width", "REAL"),
                                ("finger25Width", "REAL"),
                                ("finger11DirectionX", "REAL"),
                                ("finger11DirectionY", "REAL"),
                                ("finger11DirectionZ", "REAL"),
                                ("finger12DirectionX", "REAL"),
                                ("finger12DirectionY", "REAL"),
                                ("finger12DirectionZ", "REAL"),
                                ("finger13DirectionX", "REAL"),
                                ("finger13DirectionY", "REAL"),
                                ("finger13DirectionZ", "REAL"),
                                ("finger14DirectionX", "REAL"),
                                ("finger14DirectionY", "REAL"),
                                ("finger14DirectionZ", "REAL"),
                                ("finger15DirectionX", "REAL"),
                                ("finger15DirectionY", "REAL"),
                                ("finger15DirectionZ", "REAL"),
                                ("finger21DirectionX", "REAL"),
                                ("finger21DirectionY", "REAL"),
                                ("finger21DirectionZ", "REAL"),
                                ("finger22DirectionX", "REAL"),
                                ("finger22DirectionY", "REAL"),
                                ("finger22DirectionZ", "REAL"),
                                ("finger23DirectionX", "REAL"),
                                ("finger23DirectionY", "REAL"),
                                ("finger23DirectionZ", "REAL"),
                                ("finger24DirectionX", "REAL"),
                                ("finger24DirectionY", "REAL"),
                                ("finger24DirectionZ", "REAL"),
                                ("finger25DirectionX", "REAL"),
                                ("finger25DirectionY", "REAL"),
                                ("finger25DirectionZ", "REAL"),
                                ("finger11TipPosX", "REAL"),
                                ("finger11TipPosY", "REAL"),
                                ("finger11TipPosZ", "REAL"),
                                ("finger12TipPosX", "REAL"),
                                ("finger12TipPosY", "REAL"),
                                ("finger12TipPosZ", "REAL"),
                                ("finger13TipPosX", "REAL"),
                                ("finger13TipPosY", "REAL"),
                                ("finger13TipPosZ", "REAL"),
                                ("finger14TipPosX", "REAL"),
                                ("finger14TipPosY", "REAL"),
                                ("finger14TipPosZ", "REAL"),
                                ("finger15TipPosX", "REAL"),
                                ("finger15TipPosY", "REAL"),
                                ("finger15TipPosZ", "REAL"),
                                ("finger21TipPosX", "REAL"),
                                ("finger21TipPosY", "REAL"),
                                ("finger21TipPosZ", "REAL"),
                                ("finger22TipPosX", "REAL"),
                                ("finger22TipPosY", "REAL"),
                                ("finger22TipPosZ", "REAL"),
                                ("finger23TipPosX", "REAL"),
                                ("finger23TipPosY", "REAL"),
                                ("finger23TipPosZ", "REAL"),
                                ("finger24TipPosX", "REAL"),
                                ("finger24TipPosY", "REAL"),
                                ("finger24TipPosZ", "REAL"),
                                ("finger25TipPosX", "REAL"),
                                ("finger25TipPosY", "REAL"),
                                ("finger25TipPosZ", "REAL"),
                                #("gestures", "INT")
                              ]
            tablesDict = {"data":self.dataFields}
            self.db.initDB(tablesDict)
            self.db.close()

        # Define required data.
        self.data = Struct

        self.data.errMsg = ""
        self.data.tempRecordData = dict()

        # Deterministic guidelines
        self.data.det = dict()
        self.data.det['translateExclude'] = ['word']
        # Let's exclude the position and direction data for now because they
        # are making us fail all the time...
        for i in xrange(1,3):
            for j in xrange(1,6):
                self.data.det['translateExclude'].\
                append("finger"+str(i)+str(j)+"TipPosX")
                self.data.det['translateExclude'].\
                append("finger"+str(i)+str(j)+"TipPosY")
                self.data.det['translateExclude'].\
                append("finger"+str(i)+str(j)+"TipPosZ")
                self.data.det['translateExclude'].\
                append("finger"+str(i)+str(j)+"DirectionX")
                self.data.det['translateExclude'].\
                append("finger"+str(i)+str(j)+"DirectionY")
                self.data.det['translateExclude'].\
                append("finger"+str(i)+str(j)+"DirectionZ")
            self.data.det['translateExclude'].append("palm"+str(i)+"PositionX")
            self.data.det['translateExclude'].append("palm"+str(i)+"PositionY")
            self.data.det['translateExclude'].append("palm"+str(i)+"PositionZ")
            self.data.det['translateExclude'].append("palm"+str(i)+"DirectionX")
            self.data.det['translateExclude'].append("palm"+str(i)+"DirectionY")
            self.data.det['translateExclude'].append("palm"+str(i)+"DirectionZ")
            self.data.det['translateExclude'].append("palm"+str(i)+"NormalX")
            self.data.det['translateExclude'].append("palm"+str(i)+"NormalY")
            self.data.det['translateExclude'].append("palm"+str(i)+"NormalZ")
        if self.debug: print self.data.det['translateExclude']

        # Finger length/width ratios
        self.data.det['fingerRatios'] = [0,0,0,0,0]

        # Epsilon refers to the margin of error we are allowing when we filter
        # data.
        self.data.epsilon = dict()
        for data in self.dataFields:
            self.data.epsilon[data[0]] = 50
        self.data.epsilon['hand1'] = 1
        self.data.epsilon['hand2'] = 1

    def __init__(self, database=None, debug=False):
        self.database = database
        self.debug = debug
        self.mainInit()
