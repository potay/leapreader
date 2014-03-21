## This file contains functions which belonged to previous versions of the
## software or are under construction

## main.py

# Console or GUI?
    userInput = leapReader.getUserInput("Console or GUI? (c/g)")
    if userInput == "g":
        # And we run it.
        view.run()
    elif userInput == "c":
        consoleInit(leapReader)

## UI.py

## Under construction

    def drawAddNewPage(self):
        self.refreshOn = False
        self.drawTextBackground()
        self.pageOutput = self.canvas.create_text(self.width/2, self.height/2,
            text="", width=300, font=self.style['font'])
        self.textInput = Entry(self.canvas, textvariable="hello", bd=0,
                highlightthickness=0,)
        self.canvas.create_window(self.width/2, self.height/2, window=self.textInput)
        self.textInput.focus_set()
        self.canvas.update()

    ## Add New button for database page
    """data = dict()
        data['color'] = hexToRGB('#62c3ff')
        data['hoverColor'] = hexToRGB('#c2e3ff')
        data['borderColor'] = hexToRGB('#c2e3ff')
        data['width'] = 200
        data['height'] = 200
        data['padding'] = 20
        data['intervalX'] = 0
        data['intervalY'] = 0
        data['border'] = 10
        data['font'] = ("Helvetica", "26", "normal")
        data['fontColor'] = hexToRGB('#ffffff')
        data['fontHoverColor'] = hexToRGB('#aaaaaa')
        data['fontShadowOffsetX'] = 1
        data['fontShadowOffsetY'] = 1
        data['fontShadowColor'] = hexToRGB('#666666')
        buttonWidth = 200
        buttonHeight = 50
        vertOffset = -200
        link = 7
        text = "Add New"
        x1, y1 = (self.width-buttonWidth)/2, self.height/2+vertOffset
        x2, y2 = (self.width+buttonWidth)/2, self.height/2+vertOffset+buttonHeight
        self.drawButton(x1, y1, x2, y2, text, data,
            self.changePageFunction(link), "rect")"""

## LeapReader.py

## Old Algorithms

    ### Mapping Algorithm v2 ###

    ### This did not work for some reason... ###

    '''
    def mapFingersToHand(fingersList):
        # Finding the best possible fingers to finger spots map.
        fingerCount = len(fingersList)

        if (fingerCount > 2):
            # We first find the average finger tip position.
            if (fingerCount > 2):
                fingerTipAverage = [0, 0, 0]
                for finger in fingersList:
                    fingerTipAverage[0] += finger.tip_position.x
                    fingerTipAverage[1] += finger.tip_position.y
                    fingerTipAverage[2] += finger.tip_position.z
                for i in xrange(len(fingerTipAverage)):
                    fingerTipAverage[i] /= fingerCount
            for finger in fingersList:
                print (int(finger.tip_position.x), int(finger.tip_position.y), int(finger.tip_position.z)), (int(finger.tip_position.x-fingerTipAverage[0])**2+int(finger.tip_position.y-fingerTipAverage[1])**2+int(finger.tip_position.z-fingerTipAverage[2])**2)**0.5
            print (int(fingerTipAverage[0]), int(fingerTipAverage[1]), int(fingerTipAverage[2])), (int(fingerTipAverage[0])**2+int(fingerTipAverage[1])**2+int(fingerTipAverage[2])**2)**0.5

            # We characterize a thumb as being the finger which is furthest
            # from the average in the opposite direction the fingers are
            # pointing. Furthermore, it should be much further than the
            # distance from the average point to any other fingers. We
            # shall assume it should at least be two times the distance.

            # So first we find the average direction the fingers are
            # pointing

            fingerDirAverage = [0, 0, 0]
            for finger in fingersList:
                fingerDirAverage[0] += finger.direction.x
                fingerDirAverage[1] += finger.direction.y
                fingerDirAverage[2] += finger.direction.z
            for i in xrange(len(fingerDirAverage)):
                fingerDirAverage[i] /= fingerCount

            # Now let's try to find the thumb
            thumb = None
            secondFurthestFinger = None
            thumbDistance = 0
            secondFingerDistance = 0
            for finger in fingersList:
                fingerDistance = (abs(finger.tip_position.x-fingerTipAverage[0])**2+abs(finger.tip_position.y-fingerTipAverage[1])**2+abs(finger.tip_position.z-fingerTipAverage[2])**2)**0.5
                print fingerDistance
                if ((finger.direction.x/abs(finger.direction.x)*fingerTipAverage[0] > finger.direction.x/abs(finger.direction.x)*finger.tip_position.x) or
                    (finger.direction.y/abs(finger.direction.y)*fingerTipAverage[1] > finger.direction.y/abs(finger.direction.y)*finger.tip_position.y) or
                    (finger.direction.z/abs(finger.direction.z)*fingerTipAverage[2] > finger.direction.z/abs(finger.direction.z)*finger.tip_position.z)):
                    print fingerDistance, thumbDistance
                    if fingerDistance > thumbDistance:
                        thumb = finger
                        thumbDistance = fingerDistance
                    elif (fingerDistance > secondFingerDistance):
                        secondFurthestFinger = finger
                        secondFingerDistance = fingerDistance
                elif (fingerDistance > secondFingerDistance):
                    secondFurthestFinger = finger
                    secondFingerDistance = fingerDistance

            otherFingersAvgDistance = 0
            for finger in fingersList:
                if finger != thumb:
                    otherFingersAvgDistance += (abs(finger.tip_position.x-fingerTipAverage[0])**2+abs(finger.tip_position.y-fingerTipAverage[1])**2+abs(finger.tip_position.z-fingerTipAverage[2])**2)**0.5
            otherFingersAvgDistance


            # Check if the distance is at least two times the second and
            # then we will know if we have a thumb or not.
            distanceRatio = 1.5
            if (thumbDistance > distanceRatio*secondFingerDistance):
                # We find out if the thumb is on the right or left. If on
                # the right then it belongs to the left hand. If on the
                # left then it belongs to the right hand.
                thumbIndex = fingersList.index(thumb)
                #print thumbIndex
                if (thumbIndex == fingerCount-1):
                    isLeft = True
                    print isLeft
                elif (thumbIndex == 0):
                    isLeft = False
                    print isLeft
                else:
                    print "Algorithm Error!!!!!!!!"
            else:
                print "No Thumb", thumbDistance, secondFingerDistance, fingerTipAverage

        return {1: None, 2: None, 3: None, 4: None, 5: None}
    '''

    ### Mapping Algorithm v3 ###

    ## For this algorithm, we are going to project all the direction
    ## vectors of all the fingers on the plane of the palm (determined
    ## by its normal). Following which, we shall then sort the fingers
    ## according to their angles. We will then detect the thumb using
    ## the palm position and find out which of the two end fingers
    ## are the furthest back in the direction of the palm direction.
    ##

    #def mapFingersToHand(fingersList):
        #pass
