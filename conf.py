import os
import json

try:
  import merrors
  mer = True
except:
  print("For better error checking and functionability please install merrors")

def star(func):
    def inner(*args, **kwargs):
        print("*" * 30)
        func(*args, **kwargs)
        print("*" * 30)
    return inner

class config:

  def __init__(self):
    self.name = ""
    self.version = ""
    self.run_script = ""
    self.author = ""
    self.license = ""
    self.datajson = None

  def read(self):
    """
    Reads the config file and saves the values
    :return: 
    """
    with open("config.json","r") as f:
      data = f.read()
      #check if the loaded file is json
      try:
        datajson = json.loads(data)
      except Exception as e:
        if mer == True:
          merrors.error("could not load config.json. Python error: "+str(e))
        else:
          print(e)
      self.name = datajson["name"]
      self.version = datajson["version"]
      self.run_script = datajson["run_script"]
      self.author = datajson["author"]
      self.license = datajson["license"]
      self.datajson = datajson

  def get(self,var):
    """
    Return a variable
    :param var: variable to get
    :return var_val:
    """
    try:
      var_val = self.datajson[str(var)]
    except Exception as e:
      if mer == True:
        merrors.error("could not get variable ["+str(var)+"] does it exist in config.json? Python error: "+str(e))
      else:
        print(e)
    if var_val == None:
      merrors.error("could not get variable ["+str(var)+"]. It equals to None, is there a python problem?")
    else:
      return var_val