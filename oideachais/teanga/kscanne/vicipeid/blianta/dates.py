import sys
import pywikibot
import time
import re
import difflib

def _unidiff_output(expected, actual):
  expected=expected.splitlines(1)
  actual=actual.splitlines(1)
  diff=difflib.unified_diff(expected, actual)
  return ''.join(diff)

months = ['Eanáir', 'Feabhra', 'Márta', 'Aibreán', 'Bealtaine', 'Meitheamh', 'Iúil', 'Lúnasa', 'Meán Fómhair', 'Deireadh Fómhair', 'Samhain', 'Nollaig']
altmonths = ['Mí Eanáir', 'Mí Feabhra', 'Mí an Mhárta', 'Mí Aibreáin', 'Mí na Bealtaine', 'Mí an Mheithimh', 'Mí Iúil', 'Mí Lúnasa', 'Mí Mheán Fómhair', 'Mí Dheireadh Fómhair', 'Mí na Samhna', 'Mí na Nollag']

# argument is "YYYY-MM-DD" format
# return pair (1970, "11 Bealtaine") or whatever
def date2readable(d):
  pieces = d.split('-')
  if pieces[2][0]=='0':
    pieces[2] = pieces[2][1]
  return (int(pieces[0]), pieces[2] + ' ' + months[int(pieces[1])-1])

# d is "11 Bealtaine", yr is "1970" or whatever; returns "1970-05-11"
def readable2date(d, yr):
  if not d[0].isdigit():  # [[Márta]], e.g. Anne Frank in 1945
    d = '0 '+d
  pieces = d.split(' ',1)
  if len(pieces) != 2:
    print("WARNING: bad date string: "+d)
    exit(1)
  if pieces[1] in months:
    month = months.index(pieces[1]) + 1
  else:
    if pieces[1] in altmonths:
      month = altmonths.index(pieces[1]) + 1
    else:
      print("WARNING: bad month name: "+pieces[1])
      exit(1)
  ans = str(yr)+'-'
  if month < 10:
    ans += '0'
  ans += str(month) + '-'
  if int(pieces[0])<10:
    ans += '0'
  ans += pieces[0]
  return ans

# pass whatever's in the first link on a line,
# either "1970" or "11 Bealtaine", and convert into something sortable...
# years become ints, and days become strings of form "05-11"
def readable2sortable(str):
  if re.match('^[0-9]+$', str):
    return int(str)
  elif re.match('^[0-9]+ RC$', str):
    return -1*int(str[:-3])
  else:
    full = readable2date(str, 2000)
    return full[5:]

# same goal as previous function, but input is a string "YYYY-MM-DD"
# and it depends on global setting "blianta" or "laethanta"...
def date2sortable(d):
  if pagetype == 'blianta':
    return d[-5:]
  elif pagetype == 'laethanta':
    return int(d.split('-')[0])
  else:
    print("WARNING: unknown pagetype: "+pagetype)

# pass a tuple with date, pagename, label, descr
def wikitext_line(t):
  ans = '* [['
  yr, day = date2readable(t[0])
  if pagetype == 'blianta':
    ans += day
  elif pagetype == 'laethanta':
    ans += str(yr)
  ans += ']] — [['
  ans += t[1]
  if t[1] != t[2]:
    ans += '|'+t[2]
  ans += ']], '+t[3]
  return ans

def print_usage():
  print("Usage: python dates.py [blianta|laethanta] [breith|bas] [dryrun|live]")
  sys.exit(1)

if len(sys.argv)!=4:
  print_usage()

startpatt = {'breith+blianta': '== *Breitheanna *==',
             'bas+blianta': '== *Básanna *==',
             'breith+laethanta': '== *Daoine a rugadh (ar )?an lá seo *==',
             'bas+laethanta': '== *Daoine a fuair bás (ar )?an lá seo *=='}
message = {'breith': 'Breitheanna á nuashonrú', 'bas': 'Básanna á nuashonrú'}
pagetype = sys.argv[1]
if pagetype not in ['blianta', 'laethanta']:
  print_usage()
lifeevent = sys.argv[2]
if lifeevent not in message:
  print_usage()
runmode = sys.argv[3]
if runmode not in ['dryrun', 'live']:
  print_usage()

bigdict = dict()
fp = open(lifeevent+'.tsv', encoding='UTF-8')
for line in fp:
  line = line.rstrip('\n')
  fields = line.split('\t')
  yr, day = date2readable(fields[0])
  if pagetype == 'blianta':
    key = str(yr)
  else:
    key = day
  if key not in bigdict:
    bigdict[key] = list()
  # date (YYYY-MM-DD), page name on WP, Wikidata label, Wikidata descr
  if fields[4] != 'NONE':
    bigdict[key].append((fields[0],fields[2],fields[3],fields[4]))

site = pywikibot.Site('ga', 'wikipedia')
for k in bigdict.keys():
  if runmode=='dryrun':
    print("Checking page: "+k)
  page = pywikibot.Page(site, k)
  orig_text = page.text
  lines = page.text.split('\n')
  newlines = list()
  in_list_p = False
  ever_in_list_p = False
  sortablelist = list() # list of tuples
  for line in lines:
    if in_list_p:
      results = re.search('^[*] *\[\[([^]]*)\]\] *[—–-] *\[\[([^]]*)\]\]', line)
      if results:
        sortkey = readable2sortable(results.group(1)) # int 1970 or str "05-11"
        secondarykey = results.group(2)   # Kevin Scannell
        line = re.sub('[—–-]', '—', line, count=1)
        sortablelist.append((sortkey, secondarykey, line))
      else:
        in_list_p = False
        # append stuff from bigdict
        for toople in bigdict[k]:
          if toople[1] not in orig_text:
            sortablelist.append((date2sortable(toople[0]), toople[1], wikitext_line(toople)))
        sortablelist.sort()
        for entry in sortablelist:
          newlines.append(entry[2])
        newlines.append(line)
    else:
      newlines.append(line)
      if re.match(startpatt[lifeevent+'+'+pagetype], line):
        in_list_p = True
        ever_in_list_p = True

  if not ever_in_list_p:
    print("WARNING: never found births/deaths section on page...")
  new_text = '\n'.join(newlines)
  if new_text != orig_text:
    if runmode == 'dryrun':
      print('\n\nDifferences between old and new for article: '+k)
      print(_unidiff_output(orig_text, new_text))
    else:
      page.text = new_text
      page.save(message[lifeevent])
