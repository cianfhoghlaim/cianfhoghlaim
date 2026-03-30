from bs4 import BeautifulSoup
import requests
import sys

enterm = sys.argv[1]
html = requests.get('https://en.wikipedia.org/wiki/'+enterm).text
soup = BeautifulSoup(html, 'html5lib')

interwiki = [a for a in soup('a') if a.get('hreflang')]
for a in interwiki:
  print a.get('title')
