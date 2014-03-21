#######################
## Main UI Class
##
## Credit:
## rgbString(red,green,blue) - written by Professor Kosbie
#######################

from Animation import *
from PIL import Image, ImageTk
import pyaudio, wave, threading
import time, math, copy, Struct

def rgbString(red, green, blue):
    # returns rgb color string
    return "#%02x%02x%02x" % (red, green, blue)

def getAlphaRGBString(colors, bgColors, alpha):
    colorComponents = 3
    alphaColor = [None, None, None]
    for i in xrange(colorComponents):
        alphaColor[i] = int(colors[i]+(bgColors[i]-colors[i])*(1-alpha))
    return tuple(alphaColor)

def getAlphaEffect(effect, timeElapsed, totalTime):
    if effect == 'fadeInOut':
        return -0.5*math.cos(timeElapsed/totalTime*2*math.pi)+0.5
    else:
        return 1

def getSizeEffect(effect, timeElapsed, totalTime):
    if effect == 'zoomIn':
        return -0.5*math.cos(timeElapsed/totalTime*math.pi)+0.5
    else:
        return 1

def hexToRGB(hexCode):
    numerals = '0123456789abcdefABCDEF'
    hexidermal = {v: int(v, 16) for v in (x+y for x in numerals for y in \
        numerals)}
    if hexCode[0] == "#":
        hexCode = hexCode[1:]
    return (hexidermal[hexCode[0:2]], hexidermal[hexCode[2:4]], hexidermal[hexCode[4:6]])



class UIButton(object):
    def __init__(self, canvas, x1, y1, x2, y2, text, command, data, buttonType):
        self.canvas = canvas
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.text = text
        self.button = data
        self.command = command
        self.type = buttonType
        self.drawObjects = []
        self.isClicking = False
        self.init()

    def init(self):
        if self.type == 'rect':
            self.drawObjects.append(self.canvas.create_rectangle(self.x1,
                self.y1, self.x2, self.y2,
                fill=rgbString(*self.button['color']),
                outline=rgbString(*self.button['borderColor']),
                width=self.button['border']))
            self.canvas.create_text((self.x1+self.x2)/2+\
                self.button['fontShadowOffsetX'], (self.y1+self.y2)/2+\
                self.button['fontShadowOffsetY'], text=self.text,
                font=self.button['font'],
                fill=rgbString(*self.button['fontShadowColor']))
            self.text = self.canvas.create_text((self.x1+self.x2)/2, (self.y1+self.y2)/2,
             text=self.text, font=self.button['font'],
             fill=rgbString(*self.button['fontColor']))
        elif self.type == 'circle':
            self.drawObjects.append(self.canvas.create_oval(self.x1, self.y1,
                self.x2, self.y2, fill=rgbString(*self.button['color']),
                outline=rgbString(*self.button['borderColor']),
                width=self.button['border']))
            self.canvas.create_text((self.x1+self.x2)/2+\
                self.button['fontShadowOffsetX'], (self.y1+self.y2)/2+\
                self.button['fontShadowOffsetY'], text=self.text,
                font=self.button['font'],
                fill=rgbString(*self.button['fontShadowColor']))
            self.text = self.canvas.create_text((self.x1+self.x2)/2, (self.y1+self.y2)/2,
                text=self.text, font=self.button['font'],
                fill=rgbString(*self.button['fontColor']))
        elif self.type == 'topBarButton':
            self.canvas.create_rectangle(
                self.x1-self.button['arrowPointOffsetX']+\
                self.button['shadowOffsetX'],
                self.y1+self.button['shadowOffsetY'],
                self.x2+self.button['shadowOffsetX'],
                self.y2+self.button['shadowOffsetY'],
                fill=rgbString(*self.button['shadowColor']), width=0,
                outline=None)
            self.canvas.create_polygon((
                self.x1-self.button['arrowPointOffsetX']+\
                self.button['shadowOffsetX'],
                self.y1+self.button['shadowOffsetY']),
                (self.x1-self.button['arrowPointOffsetX']+\
                self.button['shadowOffsetX'],
                self.y2+self.button['shadowOffsetY']),
                (self.x1-self.button['arrowPointOffsetX']+\
                self.button['shadowOffsetX']+self.button['arrowPointOffsetX'],
                (self.y1+self.y2)/2+self.button['shadowOffsetY']+\
                self.button['arrowPointOffsetY']),
                fill=rgbString(*self.button['shadowColor']), width=0,
                outline=None)
            self.drawObjects.append(self.canvas.create_rectangle(
                self.x1-self.button['arrowPointOffsetX'], self.y1, self.x2,
                self.y2, fill=rgbString(*self.button['color']),
                width=self.button['border'],
                outline=rgbString(*self.button['borderColor'])))
            self.drawObjects.append(self.canvas.create_polygon((
                self.x1-self.button['arrowPointOffsetX'],
                self.y1), (self.x1-self.button['arrowPointOffsetX'], self.y2),
            (self.x1-self.button['arrowPointOffsetX']+\
                self.button['arrowPointOffsetX'],
                (self.y1+self.y2)/2+self.button['arrowPointOffsetY']),
            fill=rgbString(*self.button['color']), width=self.button['border'],
            outline=rgbString(*self.button['borderColor'])))
            self.text = self.canvas.create_text(((
                self.x1-self.button['arrowPointOffsetX'])+self.x2)/2,
            (self.y1+self.y2)/2, text=self.text, font=self.button['font'],
            fill=rgbString(*self.button['fontColor']))

    def click(self):
        if self.isClicking == False:
            self.isClicking = True
            self.command()
            self.isClicking = False

    def hover(self, isHover):
        buttons = self.drawObjects
        if (isHover == True):
            for button in buttons:
                self.canvas.itemconfig(button,
                    fill=rgbString(*self.button['hoverColor']))
            self.canvas.itemconfig(self.text, fill=rgbString(*self.button['fontHoverColor']))
        else:
            for button in buttons:
                self.canvas.itemconfig(button,
                    fill=rgbString(*self.button['color']))
                self.canvas.itemconfig(self.text, fill=rgbString(*self.button['fontColor']))



class UI(Animation):

    def __init__(self, model, width=800, height=800, debug=False,
                 fullscreen=False, resizable=True):
        self.width = width
        self.height = height
        self.model = model
        self.appTitle = "LeapReader"
        self.debug = debug
        self.fullscreen = fullscreen
        self.resizable = resizable

    ###############################
    ## Controller Section
    ###############################

    def mouseMotion(self, event):
        for (x1, y1, x2, y2) in self.pageClickables:
            if ((x1 <= event.x <= x2) and (y1 <= event.y <= y2)):
                self.hoverClickable((x1, y1, x2, y2), True)
            else:
                self.hoverClickable((x1, y1, x2, y2), False)

    def leftMousePressed(self, event):
        if (len(self.pageClickables) > 0):
            for (x1, y1, x2, y2) in self.pageClickables:
                if ((x1 <= event.x <= x2) and (y1 <= event.y <= y2)):
                    self.clickClickable((x1, y1, x2, y2), True)
                    return True

    def hoverClickable(self, (x1, y1, x2, y2), isHover):
        clickable = self.pageClickables[(x1, y1, x2, y2)]
        if (isHover == True):
            clickable.hover(True)
        else:
            clickable.hover(False)

    def clickClickable(self, (x1, y1, x2, y2), isPressed):
        clickable = self.pageClickables[(x1, y1, x2, y2)]
        if (isPressed == True and self.isClicking != (x1, y1, x2, y2)):
            self.isClicking = (x1, y1, x2, y2)
            clickable.click()

    def keyPressed(self, event):
        print event.keysym
        if (event.keysym == "Escape"):
            self.root.overrideredirect(False)

    ###############################
    ## View Section
    ###############################

    # ------------------------------------
    # Individual Components Draw Functions
    # ------------------------------------

    def changePageFunction(self, page):
        #print "page:", page
        def changePage():
            self.musicOn = True
            threading.Thread(target=self.playMusic,
                args=("audio/buttonClick.wav",)).start()
            self.currPage = page
            self.redrawAll()
        return changePage

    def drawButton(self, x1, y1, x2, y2, text, data, command,
                   buttonType="rect"):
        self.pageClickables[(x1, y1, x2, y2)] = UIButton(self.canvas, x1, y1,
            x2, y2, text, command, data, buttonType)

    # -------------------------
    # Main Pages Draw Functions
    # -------------------------

    def drawTopBar(self):
        self.canvas.create_rectangle(0+self.topBar['shadowOffsetX'],
            0+self.topBar['shadowOffsetY'],
            self.width+self.topBar['shadowOffsetX'],
            self.topBar['height']+self.topBar['shadowOffsetY'],
            fill=rgbString(*self.topBar['shadowColor']), width=0)
        self.canvas.create_rectangle(0, 0, self.width, self.topBar['height'],
            fill=rgbString(*self.topBar['bgColor']), width=0)
        self.canvas.create_text(self.width/2, self.topBar['height']/2,
            text="LeapReader")
        if self.pageList[self.currPage] != 'Home':
            text = self.topBarButton['text']
            link = self.topBarButton['link']
            self.drawButton(self.topBarButton['offsetX']+\
                self.topBarButton['arrowPointOffsetX'],
                self.topBarButton['offsetY'],
                self.topBarButton['offsetX']+self.topBarButton['width'],
                self.topBarButton['offsetY']+self.topBarButton['height'],
                text, self.topBarButton, self.changePageFunction(link),
                "topBarButton")


    def playMusic(self, path):
        chunk = 1024

        #open a wav format music
        f = wave.open(path,"rb")
        #instantiate PyAudio
        p = pyaudio.PyAudio()
        #open stream
        stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
                        channels = f.getnchannels(),
                        rate = f.getframerate(),
                        output = True)
        #read data
        data = f.readframes(chunk)

        #paly stream
        while data != '':
            stream.write(data)
            data = f.readframes(chunk)

        #stop stream
        stream.stop_stream()
        stream.close()

        #close PyAudio
        p.terminate()
        self.musicOn = False

    def drawTextBackground(self):
        self.textbackground = PhotoImage(file="img/textbackground.gif")
        widthRatio = float(self.textbackground.width())/self.width
        heightRatio = float(self.textbackground.height())/self.height
        sizeRatio = max(widthRatio, heightRatio)
        maxRatio = 0.6
        if (sizeRatio > maxRatio):
            resizeRatio = int(round(sizeRatio/maxRatio))
            self.textbackground = self.textbackground.subsample(resizeRatio,resizeRatio)
        self.canvas.create_image(self.width/2, self.height/2, image=self.textbackground)

    def drawBackgroundImage(self, image):
        self.backgroundImage = PhotoImage(file=image)
        widthRatio = float(self.backgroundImage.width())/self.width
        heightRatio = float(self.backgroundImage.height())/self.height
        sizeRatio = min(widthRatio, heightRatio)
        minRatio = 1.0
        if (sizeRatio < minRatio):
            resizeRatio = int(round(minRatio/sizeRatio))
            self.backgroundImage = self.backgroundImage.zoom(resizeRatio,resizeRatio)
        self.canvas.create_image(self.width/2, self.height/2, image=self.backgroundImage)

    def drawSplashPage(self):
        self.refreshOn = True
        if self.splash.currMsg < len(self.splash.message):
            if self.musicOn == False:
                self.musicOn = True
                threading.Thread(target=self.playMusic,
                    args=("audio/intro.wav",)).start()
            # Initiate the timestamp for our timer
            if self.timestamp == None:
                self.timestamp = time.time()
            timeElapsed = time.time() - self.timestamp
            if (timeElapsed < self.splash.timeLength):
                message = self.splash.message[self.splash.currMsg][0]
                type = self.splash.message[self.splash.currMsg][1]
                alpha = getAlphaEffect(self.splash.effect, timeElapsed,
                    self.splash.timeLength)
                color = getAlphaRGBString(self.splash.color, self.bgColor,
                    alpha)
                if (type == "text"):
                    self.canvas.create_text(self.width/2, self.height/2,
                    text=message, fill=rgbString(*color), font=self.splash.font)
                elif (type == "image"):
                    self.photoimage = PhotoImage(file=message)
                    widthRatio = float(self.photoimage.width())/self.width
                    heightRatio = float(self.photoimage.height())/self.height
                    sizeRatio = max(widthRatio, heightRatio)
                    maxRatio = 0.6
                    if (sizeRatio > maxRatio):
                        resizeRatio = int(round(sizeRatio/maxRatio))
                        self.photoimage = self.photoimage.subsample(resizeRatio,resizeRatio)
                    self.canvas.create_image(self.width/2, self.height/2, image=self.photoimage)
            else:
                self.timestamp = None
                self.splash.currMsg += 1
        else:
            self.currPage = 6

    def drawMainMenuPage(self):
        self.refreshOn = True
        offsetX, offsetY = 0, 0
        if self.timestamp == None:
            self.timestamp = time.time()
            threading.Thread(target=self.playMusic,
                args=("audio/homeIntro.wav",)).start()
        timeElapsed = time.time() - self.timestamp

        # Draw Banner
        self.headerPhoto = PhotoImage(file=self.home.header['image'])
        heightRatio = float(self.headerPhoto.height())/self.home.header['height']
        maxRatio = 1.0
        if (heightRatio > maxRatio):
            resizeRatio = int(heightRatio/maxRatio)
            self.headerPhoto = self.headerPhoto.subsample(resizeRatio,resizeRatio)
        self.canvas.create_image(self.home.header['offsetX'], self.home.header['offsetY'], image=self.headerPhoto)

        for i in xrange(len(self.home.menuList)):
            cx, cy = self.home.button['setOffsetX'],\
            self.home.button['setOffsetY']
            offsetX += self.home.button[i]['intervalX']
            offsetY += self.home.button[i]['intervalY']
            width, height = self.home.button[i]['width'],\
            self.home.button[i]['height']
            color = rgbString(*self.home.button[i]['color'])
            if (timeElapsed < self.home.effects['timeLength']):
                currWidth = width*getSizeEffect('zoomIn', timeElapsed,
                    self.home.effects['timeLength'])
                currHeight = height*getSizeEffect('zoomIn', timeElapsed,
                    self.home.effects['timeLength'])
            else:
                currWidth = width
                currHeight = height
                self.timestamp = None
                self.refreshOn = False
            text = self.home.menuList[i][0] if ((currWidth >= width) and
                (currHeight >= height)) else ""
            link = self.home.menuList[i][1] if ((currWidth >= width) and
                (currHeight >= height)) else self.currPage
            self.drawButton(cx+offsetX+width/2-currWidth/2,
                            cy+offsetY+height/2-currHeight/2,
                            cx+offsetX+width/2+currWidth/2,
                            cy+offsetY+height/2+currHeight/2,
                            text, self.home.button[i],
                            self.changePageFunction(link), "circle")

    def drawTranslatePage(self):
        self.refreshOn = False
        data = dict()
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
        self.drawButton(self.width/2-100, self.height/2-200, self.width/2+100,
            self.height/2-100, "Record", data, self.recordWrapper, "rect")
        self.pageOutput = self.canvas.create_text(self.width/2, self.height/2,
            text="", width=300, font=self.style['font'],
            fill=rgbString(*self.style['fontColor']))

    def drawDatabasePage(self):
        self.refreshOn = False
        self.drawTextBackground()
        self.pageOutput = self.canvas.create_text(self.width/2, self.height/2,
            text="", width=300, font=self.style['font'])
        self.getStoredData()

    def drawHelpPage(self):
        self.refreshOn = False
        self.photoinstructions = PhotoImage(file="img/instructions.gif")
        widthRatio = float(self.photoinstructions.width())/self.width
        heightRatio = float(self.photoinstructions.height())/self.height
        sizeRatio = max(widthRatio, heightRatio)
        maxRatio = 0.6
        if (sizeRatio > maxRatio):
            resizeRatio = int(round(sizeRatio/maxRatio))
            self.photoinstructions = self.photoinstructions.subsample(resizeRatio,resizeRatio)
        self.canvas.create_image(self.width/2, self.height/2, image=self.photoinstructions)

    def drawCreditPage(self):
        self.refreshOn = False
        self.canvas.create_text(self.width/2, self.height/2,
            text="Written By:\nPaul Chun", justify=CENTER, width=300,
            font=self.style['font'], fill=rgbString(*self.style['fontColor']))

    def drawCalibrationPage(self):
        self.refreshOn = False
        data = dict()
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
        text = "Let's analyze your hands first. Place out your right hand \
out flat, palm down with your fingers spread out, above the Leap Motion. Click '\
Calibrate' when you are ready."
        self.drawButton(self.width/2-100, self.height/2-200, self.width/2+100,
            self.height/2-100, "Calibrate", data, self.calibrateWrapper, "rect")
        self.pageOutput = self.canvas.create_text(self.width/2, self.height/2,
            text=text, width=300, font=self.style['font'],
            fill=rgbString(*self.style['fontColor']))

    def redrawAll(self):
        self.canvas.delete(ALL)
        # Draw/fill the background
        self.canvas.create_rectangle(0, 0, self.width, self.height,
                                     fill=rgbString(*self.bgColor), width=0)
        self.pageClickables.clear() # Refresh the clickables

        # Splash Page
        if (self.currPage == 0):
            self.root.wm_title(self.appTitle+" - "+self.pageList[self.currPage])
            self.drawSplashPage()

        # Main Menu Page
        elif (self.currPage == 1):
            self.drawBackgroundImage(self.bgImage)
            self.root.wm_title(self.appTitle+" - "+self.pageList[self.currPage])
            self.drawMainMenuPage()
            self.drawTopBar()

        # Translate Page
        elif (self.currPage == 2):
            self.drawBackgroundImage(self.bgImage)
            self.root.wm_title(self.appTitle+" - "+self.pageList[self.currPage])
            self.drawTranslatePage()
            self.drawTopBar()

        # Database Page
        elif (self.currPage == 3):
            self.drawBackgroundImage(self.bgImage)
            self.root.wm_title(self.appTitle+" - "+self.pageList[self.currPage])
            self.drawDatabasePage()
            self.drawTopBar()

        # Help Page
        elif (self.currPage == 4):
            self.drawBackgroundImage(self.bgImage)
            self.root.wm_title(self.appTitle+" - "+self.pageList[self.currPage])
            self.drawHelpPage()
            self.drawTopBar()

        # Credit Page
        elif (self.currPage == 5):
            self.drawBackgroundImage(self.bgImage)
            self.root.wm_title(self.appTitle+" - "+self.pageList[self.currPage])
            self.drawCreditPage()
            self.drawTopBar()

        # Calibration Page
        elif (self.currPage == 6):
            self.root.wm_title(self.appTitle+" - "+self.pageList[self.currPage])
            self.drawCalibrationPage()

        # Add New Page
        elif (self.currPage == 7):
            self.root.wm_title(self.appTitle+" - "+self.pageList[self.currPage])
            self.drawAddNewPage()

        # 404 Error Page
        else:
            self.root.wm_title(self.appTitle+" - 404 Error")
            self.draw404Page()
            self.drawTopBar()

    ##############################
    ## Model Interaction Section
    ##############################

    def recordWrapper(self):
        threading.Thread(target=self.countdown, args=(5,)).start()
        threading.Thread(target=self.record).start()

    def calibrateWrapper(self):
        threading.Thread(target=self.countdown, args=(15,)).start()
        threading.Thread(target=self.calibrate).start()

    def countdown(self, timeCount):
        if self.timestamp == None:
            self.timestamp = time.time()
        self.count = 0
        timeElapsed = time.time() - self.timestamp
        while timeElapsed < timeCount:
            if (int(timeElapsed) > self.count):
                self.count += 1
                if self.debug == True: print timeCount-self.count
                self.canvas.itemconfig(self.pageOutput, text=str(timeCount-self.count))
            timeElapsed = time.time() - self.timestamp
        self.timestamp = None

    def record(self):
        self.model.record(3, 2)
        self.result = self.model.translateRecordData()
        if self.result == False: text = "Oops! We do not understand what you "+\
        "signed. Your hands might be too stubby. Just kidding! Try again? Or"+\
        " try adding it as a new word?"
        else: text = "It means: "+str(self.result)
        self.canvas.itemconfig(self.pageOutput, text=text)
        self.isClicking = False

    def calibrate(self):
        if self.calibrateCount == 0:
            isLeft = False
        else:
            isLeft = False
        print isLeft
        self.model.record(10)
        self.result = self.model.saveFingersMetric(isLeft)
        print self.result
        if self.result == False:
            text = "Oops! There was an error. Please try again."
        else:
            if self.calibrateCount == 0:
                text = "Now let's analyze your hands left hand. Place out your left\
 hand out flat, palm down with your fingers spread out, above the Leap Motion. \
 Click 'Calibrate' when you are ready."
                self.calibrateCount = 1
            else:
                self.currPage = 1
                self.refreshOn = True
        self.isClicking = False
        self.canvas.itemconfig(self.pageOutput, text=text)

    def getStoredData(self):
        result = self.model.getStoredData()
        text = "Words:\n\n"
        for i in xrange(len(result)):
            text += str(i+1)+": "+result[i][0]+"\n"
            if self.debug == True: print result[i]
        self.canvas.itemconfig(self.pageOutput, text=text)

    ###########################
    ## Initiation Section
    ###########################

    def init(self):
        self.timestamp = None
        self.timerFiredDelay = 20 # milliseconds
        self.refreshOn = True
        self.musicOn = False

        self.bgColor = (30,30,30)
        self.bgImage = "img/background.gif"

        self.pageList = {0: 'Splash', 1: 'Home', 2: 'Translate', 3: 'Dictionary',
         4: 'Instructions', 5: 'Credit', 6: 'Calibrate', 7: 'Add a New Word'}
        self.currPage = 0
        self.pageClickables = dict()
        self.isClicking = False

        self.style = dict()
        self.style['fontColor'] = hexToRGB("#ffffff")
        self.style['font'] = ("helvetica", "16", "normal")

        self.splash = Struct
        self.splash.timeLength = 4
        self.splash.color = (255,255,255)
        self.splash.currMsg = 0
        self.splash.font = "Arial 50"
        self.splash.effect = 'fadeInOut'
        self.splash.message = [("Hello", "text"),
                               ("Welcome to", "text"),
                               ("img/banner.gif", "image"),
                               ("We are glad you are here (:", "text")]

        self.topBar = dict()
        self.topBar['height'] = 50
        self.topBar['bgColor'] = hexToRGB("#cccccc")
        self.topBar['shadowColor'] = hexToRGB("#666666")
        self.topBar['shadowOffsetX'] = 5
        self.topBar['shadowOffsetY'] = 5
        self.topBarButton = dict()
        self.topBarButton['text'] = "Back Home"
        self.topBarButton['link'] = 1
        self.topBarButton['width'] = 75
        self.topBarButton['height'] = 30
        self.topBarButton['offsetX'] = 20
        self.topBarButton['offsetY'] = (self.topBar['height']-\
            self.topBarButton['height'])/2
        self.topBarButton['arrowPointOffsetX'] = -10
        self.topBarButton['arrowPointOffsetY'] = 0
        self.topBarButton['color'] = hexToRGB("#bbbbbb")
        self.topBarButton['shadowColor'] = hexToRGB("#999999")
        self.topBarButton['shadowOffsetX'] = 2
        self.topBarButton['shadowOffsetY'] = 2
        self.topBarButton['border'] = 0
        self.topBarButton['borderColor'] = hexToRGB("#bbbbbb")
        self.topBarButton['hoverColor'] = hexToRGB("#b9b9b9")
        self.topBarButton['font'] = ("Helvetica", "12", "normal")
        self.topBarButton['fontColor'] = hexToRGB('#ffffff')
        self.topBarButton['fontHoverColor'] = hexToRGB('#aaaaaa')

        self.home = Struct
        self.home.effects = dict()
        self.home.effects['timeLength'] = 1
        self.home.menuList = [('TRANSLATE', 2),
                              ('DICTIONARY', 3),
                              ('INSTRUCTIONS', 4),
                              ('CREDIT', 5)]
        self.home.header = dict()
        self.home.header['bottomPadding'] = 60
        self.home.header['height'] = int(round(0.2*self.height))
        self.home.header['image'] = "img/header.gif"
        self.home.button = dict()
        self.home.button[0] = dict()
        self.home.button[0]['color'] = hexToRGB('#62c3ff')
        self.home.button[0]['hoverColor'] = hexToRGB('#336699')
        self.home.button[0]['borderColor'] = hexToRGB('#336699')
        self.home.button[0]['width'] = 200
        self.home.button[0]['height'] = 200
        self.home.button[0]['padding'] = 20
        self.home.button[0]['intervalX'] = 0
        self.home.button[0]['intervalY'] = 0
        self.home.button[0]['border'] = 10
        self.home.button[0]['font'] = ("Arial", "26", "bold")
        self.home.button[0]['fontColor'] = hexToRGB('#ffffff')
        self.home.button[0]['fontHoverColor'] = hexToRGB('#aaaaaa')
        self.home.button[0]['fontShadowOffsetX'] = 2
        self.home.button[0]['fontShadowOffsetY'] = 2
        self.home.button[0]['fontShadowColor'] = hexToRGB('#113355')

        self.home.button[1] = dict()
        self.home.button[1]['color'] = hexToRGB('#c3ff62')
        self.home.button[1]['hoverColor'] = hexToRGB('#669933')
        self.home.button[1]['borderColor'] = hexToRGB('#669933')
        self.home.button[1]['width'] = 200
        self.home.button[1]['height'] = 200
        self.home.button[1]['padding'] = 20
        self.home.button[1]['intervalX'] = self.home.button[1]['width']+\
        self.home.button[1]['padding']
        self.home.button[1]['intervalY'] = 0
        self.home.button[1]['border'] = 10
        self.home.button[1]['font'] = ("Arial", "26", "bold")
        self.home.button[1]['fontColor'] = hexToRGB('#ffffff')
        self.home.button[1]['fontHoverColor'] = hexToRGB('#aaaaaa')
        self.home.button[1]['fontShadowOffsetX'] = 2
        self.home.button[1]['fontShadowOffsetY'] = 2
        self.home.button[1]['fontShadowColor'] = hexToRGB('#335511')

        self.home.button[2] = dict()
        self.home.button[2]['color'] = hexToRGB('#ffc362')
        self.home.button[2]['hoverColor'] = hexToRGB('#996633')
        self.home.button[2]['borderColor'] = hexToRGB('#996633')
        self.home.button[2]['width'] = 200
        self.home.button[2]['height'] = 200
        self.home.button[2]['padding'] = 20
        self.home.button[2]['intervalX'] = -self.home.button[2]['width']-\
        self.home.button[2]['padding']
        self.home.button[2]['intervalY'] = self.home.button[2]['height']+\
        self.home.button[2]['padding']
        self.home.button[2]['border'] = 10
        self.home.button[2]['font'] = ("Arial", "26", "bold")
        self.home.button[2]['fontColor'] = hexToRGB('#ffffff')
        self.home.button[2]['fontHoverColor'] = hexToRGB('#aaaaaa')
        self.home.button[2]['fontShadowOffsetX'] = 2
        self.home.button[2]['fontShadowOffsetY'] = 2
        self.home.button[2]['fontShadowColor'] = hexToRGB('#553311')

        self.home.button[3] = dict()
        self.home.button[3]['color'] = hexToRGB('#c362ff')
        self.home.button[3]['hoverColor'] = hexToRGB('#663399')
        self.home.button[3]['borderColor'] = hexToRGB('#663399')
        self.home.button[3]['width'] = 200
        self.home.button[3]['height'] = 200
        self.home.button[3]['padding'] = 20
        self.home.button[3]['intervalX'] = self.home.button[3]['width']+\
        self.home.button[3]['padding']
        self.home.button[3]['intervalY'] = 0
        self.home.button[3]['border'] = 10
        self.home.button[3]['font'] = ("Arial", "26", "bold")
        self.home.button[3]['fontColor'] = hexToRGB('#ffffff')
        self.home.button[3]['fontHoverColor'] = hexToRGB('#aaaaaa')
        self.home.button[3]['fontShadowOffsetX'] = 2
        self.home.button[3]['fontShadowOffsetY'] = 2
        self.home.button[3]['fontShadowColor'] = hexToRGB('#331155')

        self.home.button['setOffsetX'] = (self.width-\
            self.home.button[0]['padding'])/2-self.home.button[0]['width']
        self.home.button['setOffsetY'] = (self.height-\
            self.home.button[0]['padding'])/2-self.home.button[0]['height']+\
        self.home.header['height']/2+self.home.header['bottomPadding']/2
        self.home.header['offsetX'] = self.width/2
        self.home.header['offsetY'] = (self.height-\
            self.home.button[0]['padding'])/2-self.home.button[0]['height']-\
        (self.home.header['bottomPadding'])/2

        self.calibrateCount = 0
