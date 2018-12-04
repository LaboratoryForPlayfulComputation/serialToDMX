import array
import time
import serial
from ola.ClientWrapper import ClientWrapper

class Universe:
  def __init__(self, number):
    self.number = number
    self.fixtures = []

class Fixture:
  def __init__(self, name, number, numChannels):
    self.name = name
    self.number = number
    self.startingAddr = 0
    self.numChannels = numChannels
    self.channels = [Channel() for i in range (numChannels)]

class Channel:
  def __init__(self):
    self.value = 0
 
def parseCommand(serialLine):
  print(serialLine)
  
  if "updateChannels" in serialLine:
    if (len(universe.fixtures) > 0):
      sendDmx(generateDmxCommand())
    return

  if (":" not in serialLine):
    return

  info = serialLine.split(":")
  commandType = info[0]
  commandVal = info[1]
  if (len(commandVal) <= 0): # no values were sent, likely an error with serial write
    return

  if commandType == "addFixture":
    moreInfo = commandVal.split(",")
    if (len(moreInfo) == 2):
      fixtureName = moreInfo[0]
      numChannels = int(moreInfo[1])
      fixtureNum = len(universe.fixtures)
      fixture = Fixture(fixtureName, fixtureNum, numChannels)
      universe.fixtures.append(fixture)
  elif commandType == "setChannelValue":
    moreInfo = commandVal.split(",")
    if (len(moreInfo) == 3):
      fixtureName = moreInfo[0]
      channelNumber = int(moreInfo[1])
      newChannelVal = int(moreInfo[2])
      fixture = getFixtureByName(fixtureName)
      if (fixture):
        fixture.channels[channelNumber].value = newChannelVal 

def getFixtureByNumber(number):
  for i in range (0, len(universe.fixtures)):
    fixture = universe.fixtures[i]
    if fixture.number == number:
      return fixture

def getFixtureByName(name):
  for i in range (0, len(universe.fixtures)):
    fixture = universe.fixtures[i]
    if fixture.name == name:
      return fixture      

def DmxSent(state):
  wrapper.Stop()

def generateDmxCommand():
  values = []
  for i in range (0, len(universe.fixtures)):
    fixture = universe.fixtures[i]
    for j in range (0, len(fixture.channels)):
      channel = fixture.channels[j]
      values.append(channel.value)
  formattedValues = array.array('B', values)
  print(formattedValues)
  return formattedValues

def sendDmx(command):
  print("sending dmx")
  client.SendDmx(universe.number, command, DmxSent)
  wrapper.Run()

def initSerial(portName, baud):
  serialPort = None
  try:
    serialPort = serial.Serial(
    port = portName, 
    baudrate = baud,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
    )
  except serial.SerialException as e:
    print(e)
    return None
  else:
    return serialPort

if __name__ == "__main__":
  ser = None
  ser = initSerial('/dev/ttyACM0', 115200) # port is '/dev/tty.usbmodem1422' on mac

  counter=0
  universeNum = 1
  universe = Universe(universeNum)
  wrapper = ClientWrapper()
  client = wrapper.Client()

  while 1:
    if (ser == None):
      ser = initSerial('/dev/ttyACM0', 115200)
    else:
      try:
        x=str(ser.readline()) # read data from microbit
      except Exception as e:
      #except SerialException:
        print("error reading from serial port")
        try:
          ser.close()
        except SerialException:
          print("error closing serial port")
        finally:
          ser = None 
      else:
        parseCommand(x)

  ser.close()