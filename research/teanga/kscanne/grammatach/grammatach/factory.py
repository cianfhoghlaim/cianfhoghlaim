from ga import GAToken
from gd import GDToken
from gv import GVToken

class TokenFactory:

  def __init__(self, languageCode):
    self._languageCode = languageCode

  def createToken(self, lineNumber=None, line=None):
    return globals()[self._languageCode+'Token'](lineNumber, line)
