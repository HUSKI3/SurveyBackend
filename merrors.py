import time
point = "•"
class merrors:
  def __init__(self):
    self.errors = []
  def error(self,msg):
    print("\u001b[31m",point,f"[KALM] {msg}")
    self.errors+=["Error",msg,time.strftime("%H:%M:%S", time.localtime())]
  def bigpanik(self): 
    print("\u001b[31m",point,f"[PANIK] The program could not handle the request")
    self.errors+=["Panik",time.strftime("%H:%M:%S", time.localtime())]
  def getall(self):
    return self.errors
#USAGE
#error("Could not load anything oopsie")