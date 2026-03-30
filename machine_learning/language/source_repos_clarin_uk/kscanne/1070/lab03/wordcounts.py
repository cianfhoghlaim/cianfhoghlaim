import sys
import re

if __name__ == "__main__":

  freqdict = dict()
  pattern = re.compile(r"([A-Za-z]+)")
  for line in sys.stdin:   # for each line that we read in
    for word in re.findall(pattern, line):  # loop over all words on that line
      if word in freqdict:    # if we've seen the word already
        freqdict[word] += 1   #  increment its count in the dictionary
      else:
        freqdict[word] = 1    # otherwise, set its value in dictionary to 1

  # finally, print out the words and their counts in decreasing order
  for word in sorted(freqdict, key=freqdict.get, reverse=True):
    print freqdict[word], word
