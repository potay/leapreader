from classes import LeapReader, UI
import sys

def consoleInit(leapReader):
    userInput = leapReader.getUserInput("Let's analyze your hands first. Place out your right hand out flat, palm down with your fingers spread out, above the Leap Motion. Type 'go' when you are ready")
    if userInput == "go":
        leapReader.record(10)
        result = leapReader.saveFingersMetric(False)
        if (result == True):
            userInput = leapReader.getUserInput("Now let's analyze your hands left hand. Place out your left hand out flat, palm down with your fingers spread out, above the Leap Motion. Type 'go' when you are ready")
            if userInput == 'go':
                leapReader.record(10)
                result = leapReader.saveFingersMetric(False)
                if result == True:
                    leapReader.message("Yay! Let's start!")
                    console(leapReader)
                else:
                    leapReader.message("Oops! There was an error!")
                    consoleInit(leapReader)
            else:
                leapReader.message("Oops! There was an error!")
                consoleInit(leapReader)
        else:
            leapReader.message("Oops! There was an error!")
            consoleInit(leapReader)
    else:
        consoleInit(leapReader)

def console(leapReader):
    userInput = leapReader.getUserInput("Type 'record' to start recording or 'exit' to exit program.")

    if (userInput == 'record'):
        leapReader.record(10)
        userInput = leapReader.getUserInput("Would you like to save this data? Or translate it? (s/t): ", False)
        if (userInput == "s"):
            userInput = leapReader.getUserInput("What does it mean?")
            if (userInput != ""):
                result = leapReader.saveRecordData(userInput)
                if (result == True):
                    leapReader.message("Success!")
                else:
                    leapReader.message("Oops! There was an error! ): Don't worry. Your recorded data was not deleted. Here's the error report\n"+leapReader.errMsg)
        elif (userInput == "t"):
            leapReader.message("Translating...")
            result = leapReader.translateRecordData()
            leapReader.message("It means: "+str(result))
        else:
            userInput = leapReader.getUserInput("Okay! Delete recorded data? (y/n): ")
            if (userInput == "y"):
                leapReader.delTempRecordData()
        console(leapReader)
    elif (userInput == 'exit'):
        sys.exit()
    else:
        console(leapReader)

def main():
    # Main run function

    # We are going to be using the model-view-controller architecture. Because
    # I like it.
    # We are also going to be using classes to organise things. This isn't
    # really OOP per-se but it builds a foundation which can be extended into
    # OOP if necessary.

    # We first create the main LeapReader instance which is basically our model
    leapReader = LeapReader.LeapReader("leapReader.db", False)

    # Secondly we create our view class which we will pass our model into.
    view = UI.UI(leapReader, debug=False, resizable=False, fullscreen=True)

    console(leapReader)
    # And we run it.
    #view.run()

if __name__ == "__main__":
    main()

