import re
import gadata
from goidelic import GoidelicToken
from rules import Constraint

class GAToken(GoidelicToken):

  def __init__(self, lineNumber=None, line=None):
    super().__init__(lineNumber, line)

  # don't want these as constraints since then a word mutated for no
  # linguistic reason wouldn't get flagged...
  # Irish-specific since gd only uses Form=Emp
  def autosetFeatures(self):
    if self.isLenited():
      self.addFeature('Form','Len')
    else:
      self.killFeature('Form','Len')
    if self.isEclipsed():
      self.addFeature('Form','Ecl')
    else:
      self.killFeature('Form','Ecl')
    if self.hasPrefixH():
      self.addFeature('Form','HPref')
    else:
      self.killFeature('Form','HPref')
    # pseudo-features
    if self.hasPrefixT():
      self.addFeature('XForm','TPref')

  def __getitem__(self, arg):
    answer = super().__getitem__(arg)
    if arg == 'deprel' and answer == 'compound':
      return 'nmod'
    else:
      return answer

  # others we're not bothering trying to predict:
  # Abbr, Dialect, Foreign, Typo
  def checkableFeatures(self):
    return [
            'Aspect',
            'Case',
            'Definite',
            'Degree',
            'Form',
            'Gender',   # same as Number...
            'NounType',
            'Number',   # go léir, dhá X móra, chomh X...
            'NumType',
            'Mood',
            #'PartType',
            'Person',
            'Polarity',
            'Poss',
            'PrepForm',  # in ann, i gcomhair, faoi réir
            'PronType',
            'Reflex',
            'Tense',
            'VerbForm',
            'XForm'
           ]

  def predictFeatureValue(self, feat):
    return getattr(GAToken, 'predict'+feat+self['upos'], GAToken.noConstraint)(self)

  ####################### BOOLEAN METHODS ##########################

  # ok on Foreign=Yes b/c of gd words
  def isLenitable(self):
    return re.match(r'([bcdfgmpt]|sh?[lnraeiouáéíóú])', self['token'], flags=re.IGNORECASE)

  # ok on Foreign=Yes b/c of gd words
  def isLenited(self):
    return re.match(r'([bcdfgmpt]h[^f]|sh[lnraeiouáéíóú])', self['token'], flags=re.IGNORECASE) and re.match(r'(.[^h]|bheith)', self['lemma'], flags=re.IGNORECASE)

  def isEclipsable(self):
    return re.match(r'[aeiouáéíóúbcdfgpt]', self.demutatedToken(), flags=re.IGNORECASE)

  # permits mBriathar, MBRIATHAR, but not Mbriathar (to avoid "Ndugi", etc.)
  # allowed on Foreign=Yes too (ón bpier, ón dTower)
  # allowed on Abbr=Yes ("gCo.")
  def isEclipsed(self):
    return re.match(r'(n-?[AEIOUÁÉÍÓÚ]|n-[aeiouáéíóú]|m[Bb]|MB|g[Cc]|GC|n[DdGg]|N[DG]|bh[Ff]|BHF|b[Pp]|BP|d[Tt]|DT)', self['token'])

  # "lemmas" is a tuple of lemmas to match
  # lemma of self should be the last in the tuple
  def isInPhrase(self, lemmas):
    curr = self
    for i in range(len(lemmas)):
      if curr['lemma'] != lemmas[-1-i]:
        return False
      curr = curr.getPredecessor()
      if curr==None:
        return False
    return True

  def hasInitialF(self):
    return re.match(r'[fF]', self['lemma'])

  def hasInitialBMP(self):
    return re.match(r'[bmpBMP]', self['lemma'])

  def hasInitialDental(self):
    return re.match(r'[dntlsDNTLS]', self['lemma'])

  def hasFinalDental(self):
    return re.search(r'[dntls]$', self['token'].lower())

  # can't use lemma because of déarfainn/abair, measa/olc, etc.
  def hasInitialVowel(self):
    return re.match(r'[aeiouáéíóúAEIOUÁÉÍÓÚ]', self.demutatedToken())

  def hasLenitableS(self):
    return re.match(r's[lnraeiouáéíóú]', self['lemma'], flags=re.IGNORECASE)

  # this means must end in a consonant
  def hasSlenderFinalConsonant(self):
    return re.search('([^a]e|[éií])[^aeiouáéíóú]+$', self['token'].lower())

  # this means must end in a consonant
  def hasBroadFinalConsonant(self):
    return re.search('([aáoóuú]|ae)[^aeiouáéíóú]+$', self['token'].lower())

  def admitsPrefixT(self):
    return self.hasInitialVowel() or self.hasLenitableS()

  def hasPrefixT(self):
    return re.match(r't(-[aeiouáéíóú]|[AEIOUÁÉÍÓÚsS])', self['token'])

  def admitsPrefixH(self):
    return self.hasInitialVowel()

  # ag, as, de, do, gan, etc. but not "don", "lena", "leo"
  # Also includes first part of compound preps... "faoi" in "faoi bhráid", etc.
  def isSimplePreposition(self):
    return self['upos']=='ADP' and not self.has('Poss','Yes') and self['Person']==None and self['Foreign']==None and self['PronType']==None

  def hasPrefixH(self):
    return re.match(r'h-?[aeiouáéíóúAEIOUÁÉÍÓÚ]', self['token']) and self.admitsPrefixH()

  def hasPrecedingDependent(self):
    return any(t['index']<self['index'] and t['deprel'] not in ['case','cc'] for t in self.getDependents())

  def precedingCen(self):
    head = self.getHead()
    return head['index']==self['index']-1 and head['token'].lower()=='cén'

  # this really means preceding "sa", "san", "den", "don"
  # These must lenite a following noun according to C.O.
  def precedingLenitingPrepPlusArticle(self):
    pr = self.getRealPredecessor()
    # TODO: don't need any of these None checks... use pr.isRoot() ...
    if pr==None:
      return False
    return pr['lemma'] in ['i', 'de', 'do'] and self.anyPrecedingDefiniteArticle()

  # this really means "an" or variants, not "na"
  def precedingDefiniteArticle(self):
    pr = self.getRealPredecessor()
    if pr==None:
      return False
    tok = pr['token'].lower()
    return tok in ['an', "'n", 'a', "a'"] and self.anyPrecedingDefiniteArticle()

  # preceding an/na but also sa, san, den, don, ón, faoin, etc.
  # used primarily for propagating definiteness
  def anyPrecedingDefiniteArticle(self):
    pr = self.getRealPredecessor()
    if pr==None:
      return False
    return pr.has('PronType','Art')

  def isVerbalNounWithAg(self):
    pr = self.getRealPredecessor()
    if pr==None:
      return False
    return pr['lemma']=='ag' and self.has('VerbForm','Vnoun')

  # "dúnadh an dorais" but not "an doras a dhúnadh"
  def isObjectFollowingVerbalNoun(self):
    hd = self.getHead()
    return self.isNominal() and self['deprel']=='obj' and hd['index']<self['index'] and hd.has('VerbForm','Vnoun')

  def isPossessed(self):
    return any(t.has('Poss','Yes') for t in self.getDependents())

  def hasGachDependent(self):
    return any(t['lemma'] in ['gach', 'gach_uile'] and t['upos']=='DET' for t in self.getDependents())

  def isQualifiedNoun(self):
    return self.isNominal() and any((t.isNominal() and t.has('Case','Gen')) or (t['upos']=='ADJ' and t['deprel']=='amod') for t in self.getDependents())

  def isGodti(self):
    return self['lemma']=='go' and self.has('PrepForm','Cmpd') and any(t['lemma']=='dtí' for t in self.getDependents())

  def isObjectOfGenitivePrepHelp(self):
    genPreps = ['chun','cois','dála','fearacht','timpeall','trasna']
    return self.isNominal() and self['VerbForm']==None and any(t['upos']=='ADP' and t.getDeprel()=='case' and not t.isGodti() and (t.has('PrepForm','Cmpd') or t['lemma'] in genPreps) for t in self.getDependents())

  def isObjectOfGenitivePrep(self):
    return self.isObjectOfGenitivePrepHelp() or (self['deprel']=='conj' and self.getHead().isObjectOfGenitivePrep())

  # First any is for "Airteagal III" or "rang 5"
  # Second any is for stuff like "bus a dó", "rang a 5"
  def hasNumberSpecifier(self):
    return any(t['upos']=='NUM' and t['index']==self['index']+1 and t['deprel']=='nmod' for t in self.getDependents()) or any(t['lemma']=='a' and t['upos']=='PART' and t.has('PartType','Num') and t['index']==self['index']+1 and t.getHead()['upos']=='NUM' and t.getHead()['deprel']=='nmod' and t.getHead()['index']==self['index']+2 for t in self.getDependents())

  # nouns governing a definite noun in the genitive should be definite
  # *except* for cases like "rang Gaeilge", "leabhar Béarla", etc.
  def hasPropagatingDefiniteDependent(self, after=-1):
    if after==-1:
      after=self['index']
    return any(t['index']>after and t.isGenitiveOfHead() and t['deprel']!='conj' and t.has('Definite','Def') and (t['lemma'] not in gadata.languages or t.anyPrecedingDefiniteArticle()) for t in self.getDependents())

  # not necessarily preceding; e.g. "sa dá chogadh"
  def anyDependentDefiniteArticle(self):
    return any(t.has('PronType','Art') for t in self.getDependents())

  # verbal particles that lenite following verb as in C.O. 10.4.2
  def isLenitingVerbalParticle(self):
    t = self['token'].lower()
    # handle "cha"?
    if t not in ['ní',"n'"] and t[-1]!='r':
      return False
    return (self['upos']=='PART' and self.has('PartType','Vb')) or \
           (self['upos']=='PART' and t=='nár') or \
           (self['upos']=='ADV' and t=='cár') or \
           (self['upos']=='SCONJ' and t in ['munar','murar','sarar','sular'])

  # a, ina, lena, etc. but *not* past tense ar, inar, lenar, etc.
  # Also includes the PRON case: "sin a bhfuil agam" and the PRON case
  # when fused with a preposition (tagged ADP) "eolas faoina bhfuil ar siúl";
  # note we can't use self.has('Tense','Past') to discard
  # "duine ar chuir..." b/c of PRON case
  def isEclipsingRelativizer(self):
    return self.has('PronType','Rel') and not re.search('r$', self['token'].lower()) and (self.has('Form','Indirect') or self['upos'] in ['ADP','PRON'])

  # Eclipsed forms after "ní": "ní bhfuair", "ní bhfaighidh", "ní bhfaighfeá"...
  def isEclipsedFaigh(self):
    return self['lemma']=='faigh' and \
      ((self.has('Mood','Ind') and self.has('Tense','Past')) or \
       self.has('Tense','Fut') or self.has('Mood','Cnd'))

  # "go" will be "go dtí" in fixed expression
  # CO also specifies prepositions that do take the dative as an alternative:
  # a, ag, ar, as, chuig, dar, de, do, faoi, fara,
  # go, i, ionsar, le, ó, roimh, trí, um
  def isInDativePP(self):
    nominativePrepositions = ['ach','amhail','gan','go','idir','mar','murach','ná','seachas']
    return self.isInPP() and not any(t['lemma'] in nominativePrepositions and t['deprel']=='case' for t in self.getDependents())

  # upos is 'NUM' and value is between 2 and 19 (though doesn't check "déag")
  def is2Thru19(self):
    if self['upos'] != 'NUM':
      return False
    if re.search('^[1-9][0-9]*$', self['lemma']):
      val = int(self['lemma'])
      return (val >= 2 and val <= 19)
    else:
      return self['lemma'] in ['dó','trí','ceathair','cúig','sé','seacht','ocht','naoi','deich']

  def has2Thru19(self):
    pr = self.getRealPredecessor()
    if pr==None:
      return False
    return pr['deprel']=='nummod' and pr.is2Thru19()

  def is3Thru6(self):
    if self['upos'] != 'NUM':
      return False
    return re.search('^[3-6]$', self['lemma']) or self['lemma'] in ['trí','ceathair','cúig','sé']

  def has3Thru6(self):
    pr = self.getRealPredecessor()
    if pr==None:
      return False
    return pr['deprel']=='nummod' and pr.is3Thru6()

  def is7Thru10(self):
    return self['lemma'] in ['seacht','7','ocht','8','naoi','9','deich','10']

  def has7Thru10(self):
    pr = self.getRealPredecessor()
    if pr==None:
      return False
    return pr['deprel']=='nummod' and pr.is7Thru10()

  # checking for "AUX" or lemma "is" does not suffice; there are some
  # with tag SCONJ ("más", "murar", etc.), or PART ("ba" in "ba mhó")
  def isCopula(self):
    return self.has('VerbForm','Cop')

  # at Goidelic level, basically checks for amod of a nominal
  # with some exceptions; Irish-specific exceptions added here
  def isAttributiveAdjective(self):
    pr = self.getRealPredecessor()
    if pr==None:
      return False
    return super().isAttributiveAdjective() and \
           not self.has('VerbForm','Part')  and \
           not (pr['lemma']=='go' and self['lemma']=='léir') and \
           pr['lemma']!='sách' and pr['lemma']!='chomh'

  # nmod of something but not in a PP
  # less general than isGenitivePosition, which also includes
  # genitives that follow compound prepositions like "in aghaidh", etc.
  # where the head points somewhere other than "aghaidh"
  # Also note this doesn't imply the word is genitive in form, e.g. if it
  # is definite ("seoladh" in "dáta sheoladh an leabhair")
  def isGenitiveOfHeadHelp(self):
    return self.isNominal() and self['deprel']=='nmod' and not self.isInPP()

  def isGenitiveOfHead(self):
    return self.isGenitiveOfHeadHelp() or (self['deprel']=='conj' and self.getHead().isGenitiveOfHead())

  def isGenitivePosition(self):
    return self.isGenitiveOfHead() or self.isObjectOfGenitivePrep()

  def isIndefinitePROPN(self):
    #return self['lemma'] in gadata.daysOfTheWeek or \
    #       self['lemma'] in gadata.months or \
    #       self['lemma'] in gadata.languages or \
    return self['lemma'] in gadata.logainmWithArticle or \
           self['lemma'] in gadata.abbrWithArticle or \
           self['lemma'] in gadata.indefiniteSurnames or \
           self['lemma'] in gadata.people or \
           self['lemma'] in gadata.properButIndefinite

  ####################### END BOOLEAN METHODS ##########################

  def noConstraint(self):
    return [Constraint('None', 'This feature is incompatible with this part-of-speech tag')]

  # TODO: ar an gcéad dul síos, mar aon leis an gcaisleán (fixed),
  #
  # also called for NUM's that precede the NOUN they modify
  def predictNounEclipsis(self):
    if not self.isEclipsable():
      return [Constraint('!Ecl', '10.6: Not an eclipsable initial letter')]
    noun = self.getHead() if self['upos']=='NUM' else self
    pr = self.getRealPredecessor()
    if pr==None:
      return [Constraint('!Ecl', '10.6: Never eclipse a noun or number at the beginning of a sentence')]
    prToken = pr['token'].lower()
    if self.isInPhrase(('mar','an','céanna')) or \
       self.isInPhrase(('thar','ais')) or \
       self.isInPhrase(('um','an','taca')):
      return [Constraint('Ecl', '10.6.1.a: Should be eclipsed in set phrase')]
    if pr.has('PronType','Art') and pr.has('Number','Sing') and \
         pr['lemma'] not in ['de','do','i'] and \
         not self.hasInitialDental() and not self.hasInitialVowel() and \
         noun.isInDativePP() and noun.has('Case','Nom'):
      return [Constraint('Ecl|Len', '10.6.1.a: Should be eclipsed or lenited by the preceding definite article')]
    # NB. gpl noun can be Number=Sing: "seolta na dtrí bhád"
    if prToken=='na' and noun.has('Case','Gen') and pr.has('Number','Plur'):
      return [Constraint('Ecl', '10.6.1.b: Should be eclipsed by preceding “na” in genitive plural')]
    if self['token'].lower()=='dhá':  # bhur dhá mbád; in dhá bhád
      return [Constraint('!Ecl', '10.6.2.e1: Do not eclipse “dhá”')]
    if pr.isPluralPossessive():
      if self['lemma']=='céile' and self.isInPP() and pr.has('Person','3'):
        # TODO: change IDT annotation?
        return [Constraint('Len','Lenite “chéile” in various prepositional phrases')]
      else:
        return [Constraint('Ecl','10.6.2: Should be eclipsed by preceding plural possessive')]
    if prToken=='dhá' and pr.getRealPredecessor()!=None and pr.getRealPredecessor().isPluralPossessive():
      return [Constraint('Ecl','10.6.2.e2: Should be eclipsed by plural possessive + dhá')]
    if pr['deprel']=='nummod' and pr.is7Thru10():
      if self['lemma'] in ['cent', 'euro', 'déag']:
        return [Constraint('!Ecl', '10.6.3.e1: Never eclipse “cent”, “euro”, or “déag”')]
      else:
        return [Constraint('Ecl', '10.6.3: Should be eclipsed by number 7-10')]
    if prToken=='i' and (pr['deprel']=='case' or self['deprel']=='fixed'):
      return [Constraint('Ecl', '10.6.4.a: Should be eclipsed by preceding “i”')]
    if prToken=='ar' and pr['upos']=='ADP':
      if self['lemma']=='diaidh': # i ndiaidh ar ndiaidh
        return [Constraint('Ecl', '10.6.4.b: Should be eclipsed in set phrase')]
      # ar dhóigh, ar ndóigh, ar dóigh are all possible!
      if self['lemma']=='dóigh':
        return [Constraint('Ecl|!Ecl', '10.6.4.b: Optionally eclipsed in set phrase')]
      if self['lemma'] in ['cúl','tús']:
        return [Constraint('Ecl|Len', '10.6.4.b: Can be eclipsed in set phrase')]
    if prToken=='dar' and self['lemma'] in ['dóigh']:
      return [Constraint('Ecl', '10.6.4.b: Should be eclipsed in set phrase')]
    if re.match('d[aá]r$', prToken) and self.demutatedToken().lower()=='cionn':
      return [Constraint('Ecl', '10.6.4.b: Should be eclipsed in set phrase')]
    if prToken=='fá' and pr['upos']=='ADP' and self['lemma']=='taobh':
      return [Constraint('Ecl|Len', '10.6.4.b: Can be eclipsed in set phrase')]
    if prToken=='go' and self['lemma'] in ['cuimhin', 'díth', 'dtí', 'fios']:
      return [Constraint('Ecl', '10.6.4.b: Should be eclipsed in set phrase')]
    if prToken=='cá' and self['lemma']=='fios':
      return [Constraint('Ecl', '10.6.5: Should be eclipsed in set phrase “cá bhfios”')]
    return [Constraint('!Ecl','10.6: Not sure why this is eclipsed')]

  # unlike other "predict" functions, this will return an "Ecl" constraint
  # even in case the word starts with m/s/n/l/r since we want that
  # info to block lenition on initial m/s.
  def predictVerbEclipsis(self):
    #if not self.isEclipsable():
    #  return [Constraint('!Ecl', '10.8: Not an eclipsable initial letter')]
    pr = self.getRealPredecessor()
    if pr==None:
      return [Constraint('!Ecl', '10.8: Sentence initial verb cannot be eclipsed')]
    prToken = pr['token'].lower()
    # TODO: ADP "faoina ndearna", "gáire faoina ndúirt sé", 'dá bhfuil agam'
    if pr.isEclipsingRelativizer():
      return [Constraint('Ecl', '10.8.1: Should be eclipsed by preceding verbal particle introducting a relative clause')]
    if (pr.has('PartType','Vb') and prToken in ['go','gu','nach']) or \
       (pr.has('PartType','Cmpl') and prToken in ['go','gu','nach']) or \
       (pr['upos']=='ADV' and prToken=='cá') or \
       (pr['upos']=='SCONJ' and \
           prToken in ['dá','go','gu','mara','muna','mura','sula']):
      return [Constraint('Ecl', '10.8.2.a: Should be eclipsed by preceding verbal particle')]
    if pr.has('PartType','Vb') and prToken=='an':
      if self.hasInitialVowel():
        return [Constraint('!Ecl', '10.8.2.a.e1: Do not eclipse an initial vowel after interrogative particle “an”')]
      else:
        return [Constraint('Ecl', '10.8.2.a: Should be eclipsed by preceding interrogative particle “an”')]

    if self.isEclipsedFaigh() and prToken=='ní':
      return [Constraint('Ecl', '10.8.2.b: Special forms of the verb “faigh” should be eclipsed following “ní”')]
    return [Constraint('!Ecl','10.8: Not sure why this verb is eclipsed')]

  def predictAdjectiveLenition(self):
    if not self.isLenitable():
      return [Constraint('!Len', '10.3: Cannot lenite an unlenitable letter')]
    # 10.3.1
    if self.isAttributiveAdjective():
      # Need ultimate head here: "príosúnaigh Bheilgeacha agus Fhrancacha"
      h = self.getUltimateHead()
      # TODO: exception "saor in aisce", "cothrom le dáta", srl. 10.3.1.e1
      # TODO: tuairisc réasúnta cuimsitheach... ADV blocks lenition?
      #   or "cuma chomh socair" (train 2554)
      # TODO: "idir bheag agus mhór (not in CO... CB+corpus only)
      # TODO: "tír mór"; set phrase in FGB, NEID, etc.
      # TODO: "Inis Mór"
      # TODO: after beirt+gpl? CB+corpus
      if h.has('Gender','Fem') and h.has('Number','Sing'):
        if h.has('Case','Nom') or h.has('Case','Dat') or h.has('Case','Voc'):
          return [Constraint('Len', '10.3.1.a: Adjective is lenited after a feminine noun in the nominative, dative, or vocative singular')]
      elif h.has('Gender','Masc') and h.has('Number','Sing'):
        if h.has('Case','Gen') or h.has('Case','Voc'):
          return [Constraint('Len', '10.3.1.b: Adjective is lenited after genitive or vocative singular masculine noun')]
      elif h.has('Number','Plur') and h.has('Case','Nom') and \
           h.hasSlenderFinalConsonant():
        if h['lemma'].lower()=='caora':
          return [Constraint('!Len', '10.3.1.c.e1: Do not lenite adjectives after “caoirigh”')]
        else:
          return [Constraint('Len', '10.3.1.c: Adjective is lenited after a nominative plural noun ending in a slender consonant')]
      hpr = h.getRealPredecessor()
      if hpr!=None:
        if h.has('Number','Sing'):
          if re.search(r'^dh?á$', hpr['token'].lower()):
            return [Constraint('Len', '10.3.1.d.i: Adjective is lenited after a noun preceded by “dá” or “dhá”')]
          if hpr.is3Thru6() or hpr.is7Thru10():
            return [Constraint('Len', '10.3.1.d.ii: Adjective is lenited after a noun preceded by numbers 3–10')]
        if h.demutatedToken().lower()=='cinn': # "chinn" itself an error
          if hpr.is3Thru6() or hpr.is7Thru10():
            return [Constraint('Len', '10.3.1.d.iii: Adjective is lenited after plural noun “cinn” preceded by numbers 3–10')]
      if h.isInDativePP() and h.has('Gender','Masc') and h.has('Number','Sing'):
        return [Constraint('Len|!Len', '10.3.1.e: Lenition is optional on adjectives following masculine nouns in the dative')]
    # 10.3.3 dhá agus dháréag... tagged as NUM and NOUN resp in UD (see FGB)
    # 10.3.4 déag agus fichead... tagged as NOUN in UD
    # 10.3.5 in compounds (ollmhór, etc.)

    # note case lemma=='ba'; that's current annotation for "ní ba" (fixed)
    # 10.3.6 After copula:
    pr = self.getRealPredecessor()
    if pr!=None:
      if (pr.isCopula() and (pr.has('Tense','Past') or pr.has('Mood','Cnd'))) or pr['lemma']=='ba':
        return [Constraint('Len', '10.3.6: Adjective is lenited after past or conditional copula')]
    return [Constraint('!Len', '10.3: Not sure why this adjective is lenited')]

  # also called for NUM's that precede the NOUN they modify
  def predictNounLenition(self):
    if not self.isLenitable():
      return [Constraint('!Len', 'Cannot lenite an unlenitable letter')]
    if self['lemma']=='bheith':
      return [Constraint('Len', 'Verbal noun “bheith” always gets Form=Len')]
    noun = self.getHead() if self['upos']=='NUM' else self
    pr = self.getRealPredecessor()
    prToken = pr['token'].lower()

    # 10.2.1
    if pr!=None and (self.anyPrecedingDefiniteArticle() or self.precedingCen()) and pr.has('Number','Sing') and prToken!='na':
      if self.hasInitialDental():
        return [Constraint('!Len', '10.2.1.e1: Do not lenite a noun or number beginning with d, t, or s after the definite article')]
      if self.precedingDefiniteArticle() or self.precedingCen(): # an/cén only
        if noun.has('Case','Gen') and noun.has('Gender','Masc') and \
           noun.has('Number','Sing'):
          return [Constraint('Len', '10.2.1.b: Must lenite a masculine singular noun in the genitive after the definite article')]
        elif noun.isInDativePP():
          if self.isEclipsable():  # i.e. not initial "m"
            return [Constraint('Ecl', '10.2.1.c (An Córas Lárnach): Should eclipse in the dative after the definite article'), Constraint('Len', '10.2.1.c (Córas an tSéimhithe): Should lenite in the dative after the definite article')]
          else:
            return [Constraint('!Len', '10.2.1.c (An Córas Lárnach): Should not lenite an initial m in the dative after the definite article'), Constraint('Len', '10.2.1.c (Córas an tSéimhithe): Should lenite an initial m in the dative after the definite article')]
        elif noun.has('Case','Nom') and noun.has('Gender','Fem') and \
           noun.has('Number','Sing'):
          return [Constraint('Len', '10.2.1.a: Must lenite feminine singular after the definite article')]
      elif self.precedingLenitingPrepPlusArticle(): # san, sa, den, don
        return [Constraint('Len', '10.2.1.c: Always lenite after sa, san, den, or don')]
      else: # remainder are examples like "faoin", "fén", "ón"
        if self.isEclipsable():  # i.e. not initial "m"
          return [Constraint('Ecl', '10.2.1.c (An Córas Lárnach): Should eclipse after faoin, ón, etc.'), Constraint('Len', '10.2.1.c (Córas an tSéimhithe): Should lenite after faoin, ón, etc.')]
        else:
          return [Constraint('!Len', '10.2.1.c (An Córas Lárnach): Should not lenite an initial m after faoin, ón, etc.'), Constraint('Len', '10.2.1.c (Córas an tSéimhithe): Should lenite an initial m after faoin, ón, etc.')]

    # 10.2.2
    if self.has('Case', 'Voc') and any(t.has('PartType','Voc') for t in self.getDependents()):
      return [Constraint('Len', '10.2.2: Always lenite after vocative particle')]

    # 10.2.3
    if pr.has('Poss','Yes'):
      # don't use lemma=='mo' because of stuff like lem', im' (ADPs)
      if pr.has('Number','Sing') and pr.has('Person','1'):
        return [Constraint('Len','10.2.3.a: Always lenite after possessive “mo”')]
      elif pr.has('Number','Sing') and pr.has('Person','2'):
        return [Constraint('Len','10.2.3.a: Always lenite after possessive “do”')]
      elif pr.has('Gender','Masc'):
        return [Constraint('Len','10.2.3.a: Always lenite after singular masculine possessive “a”')]
      elif pr.has('Gender','Fem'):
        return [Constraint('!Len','10.2.3.a: Never lenite after feminine possessive')]
    if pr['lemma'] in ['gach_uile', 'uile'] and pr['head']==self['index']:
      return [Constraint('Len','10.2.3.b: Always lenite after the adjective “uile”')]
    if pr['lemma'] in ['achan', 'aon', 'céad', 'gach_aon']:
      if self.hasInitialDental():
        return [Constraint('!Len', '10.2.3.c.e1: Do not lenite a noun or number beginning with d, t, or s after “aon” or “céad”')]
      else:
        if pr['upos']=='DET':
          return [Constraint('Len', '10.2.3.c: Lenite a noun or number after “aon”')]
        elif pr['upos']=='NUM':
          if pr.has('NumType','Ord') or pr['lemma']=='aon':
            return [Constraint('Len', '10.2.4.a: Lenite a noun or number after “aon” or ordinal “céad”')]

    # 10.2.4 following numbers
    if pr['upos']=='NUM' and pr['head']==self['index']:
      if prToken in ['dá','dhá','2']:
        prpr = pr.getRealPredecessor()
        if prpr.has('Poss','Yes') and (prpr.has('Gender','Fem') or prpr.has('Number','Plur')):
          return [Constraint('!Len', '10.2.4.b.e1: Do not lenite after “dhá” if preceded by plural or feminine possessive')]
        return [Constraint('Len', '10.2.4.b: Lenite after numbers “dá” or “dhá”')]
      elif self.has3Thru6():
        if self['lemma'] in ['cent', 'bliain', 'seachtain', 'ceann', 'cloigeann', 'fiche', 'pingin', 'trian', 'troigh', 'uair']:
          return [Constraint('!Len', '10.2.4.c.e1: Do not lenite certain special plural forms after numbers 3-6')]
        else:
          return [Constraint('Len', '10.2.4.c: Lenite after numbers 3-6')]

    # 10.2.5 following prepositions
    if pr['upos']=='PART' and pr.has('PartType','Inf') and pr['lemma'] in ['a','do'] and self.has('VerbForm','Inf'):
      return [Constraint('Len', '10.2.5.a: Always lenite a verbal noun after the preposition “a”')]
    if pr.isSimplePreposition():
      if pr['lemma'] in ['de', 'do', 'a', 'ionsar', 'mar', 'ó', 'roimh', 'trí']:
        return [Constraint('Len', '10.2.5.a: Always lenite after certain simple prepositions')]
      elif self.isInPhrase(('go','céile')) or self.isInPhrase(('le','céile')):
        if len(self.getDependents())>1:  # m.sh. le céile colscartha
          return [Constraint('!Len', 'Do not lenite “céile” here since it does not look like an adverbial phrase')]
        else: # one dependent (the ADP le or go)
          return [Constraint('Len', 'Lenite “céile” in certain adverbial phrases')]
      elif pr['lemma']=='faoi':
        if self['lemma'] in ['deara', 'seach']:
          return [Constraint('!Len', '10.2.5.a.e2: Do not lenite in set phrase “faoi deara”')]
        else:
          return [Constraint('Len', '10.2.5.a: Should lenite after simple preposition “faoi”')]
      elif pr['lemma']=='um':
        if self.hasInitialBMP():
          return [Constraint('!Len', '10.2.5.a.e1: Do not lenite words starting with b, m, or p after “um”')]
        else:
          return [Constraint('Len', '10.2.5.a: Always lenite after certain simple prepositions')]
      elif pr['lemma']=='ar':
        if self.demutatedToken().lower() in gadata.unlenitedAfterAr:
          # TODO: two exceptions in CO: "ar ball loinge", "ar ball beag"
          if self.isQualifiedNoun():
            return [Constraint('Len', '10.2.5.b.e1: Lenite a noun after “ar” when it has an adjective or genitive noun dependent')]
          else:
            return [Constraint('Len|!Len', '10.2.5.b.e2: Noun may be unlenited after “ar” when used in an adverbial phrase')]
        else:
          return [Constraint('Len', '10.2.5.b: Typically we lenite a noun or number after “ar”')]
      elif pr['lemma']=='gan':
        if self.isQualifiedNoun():
          return [Constraint('!Len', '10.2.5.c.e1: Do not lenite a noun after “gan” when it has an adjective or genitive noun dependent')]
        elif pr['head']!=self['index']:
          return [Constraint('!Len', '10.2.5.c.e2: Do not lenite a noun after “gan” when it is the object of a verbal noun')]
        elif self.hasInitialDental() or self.hasInitialF():
          if self['lemma']=='fios':
            return [Constraint('Len', '10.2.5.c.e3: Lenite after “gan” in the set phrase “gan fhios”')]
          else:
            return [Constraint('!Len', '10.2.5.c.e4: Do not lenite a word after “gan” when it starts with d, t, s, or f')]
        elif self['VerbForm']!=None:
          return [Constraint('!Len', '10.2.5.c.e5: Do not lenite a verbal noun after “gan”')]
        elif self['upos']=='PROPN':
          return [Constraint('!Len', '10.2.5.c.e6: Do not lenite a proper name after “gan”')]
        else:
          return [Constraint('Len', '10.2.5.c: Should lenite after “gan”')]
      elif pr['lemma']=='thar':
        if self['lemma'] in gadata.unlenitedAfterThar:
          return [Constraint('Len|!Len', '10.2.5.e.e2: Noun may be unlenited after “thar” when used in an adverbial phrase')]
        else:
          return [Constraint('Len', '10.2.5.e: Lenite a noun or number after “thar”')]

    # TODO: le thine, le thinidh, otherwise None (see "le chéile" above)
    # TODO: add explicit rules for no lenition after ag, etc.
    # for better error message
    # handle idir separately since we need to check coordination, no "pr"

    # 10.2.6 - similar to 10.2.10 below
    if self.has('Definite','Def') and self.has('Number','Sing') and not self.hasPrecedingDependent():
      if self.isObjectOfGenitivePrep():
        if pr['lemma']=='chun':
          return [Constraint('!Len','10.2.6.e1: Normally lenite definite noun after a preposition that triggers the genitive, but not after “chun”')]
        else:
          # not noted in 10.2.6, but see 10.2.10
          if self.demutatedToken() in ['San','Dé']:
            return [Constraint('!Len','10.2.10.e1: Never lenite this token despite being definite in genitive position')]
          else:
            return [Constraint('Len','10.2.6: Should lenite a definite noun after a preposition that triggers genitive position')]

    # 10.2.7; use head not predecessor for "tuairisc pharlaiminte agus phobail"
    hd = self.getHead()
    if hd.isNominal() and hd.has('Case','Nom') and hd.has('Gender','Fem') and hd.has('Number','Sing') and self.has('Case','Gen') and not self.has('Definite','Def'):
      if hd.hasFinalDental() and self.hasInitialDental():
        return [Constraint('!Len', '10.2.7.a: Do not lenite an initial dental after a feminine noun ending in a dental')]
      if self.hasInitialF():
        if hd['lemma'] in ['beirt', 'dís']:
          return [Constraint('Len', '10.2.7.b.e1: Lenite an initial f after “beirt” or “dís”')]
        else:
          return [Constraint('!Len', '10.2.7.b: Do not lenite an initial f after a feminine noun')]
      if self.has('Number','Plur'):
        if hd['lemma'] in ['beirt', 'dís']:
          return [Constraint('Len', '10.2.7.c.e1: Lenite a genitive plural after “beirt” or “dís”')]
        elif hd['lemma']=='clann' and self['lemma']=='mac':
          return [Constraint('Len', '10.2.7.c.e2: Lenite a genitive plural in the set phrase “clann mhac”')]
        else:
          return [Constraint('!Len', '10.2.7.c: Do not lenite a genitive plural noun after a feminine noun')]
      if hd['lemma'] in ['barraíocht', 'breis', 'cuid', 'díobháil', 'díth', 'easpa', 'éagmais', 'iomarca', 'roinnt', 'uireasa']:
        return [Constraint('!Len', '10.2.7.d: Do not lenite a genitive noun after a feminine noun that expresses an indefinite quantity')]
      # TODO 10.2.7.e,f :(  Need big lists....

      if hd['lemma'] in gadata.abstractFeminine:
        return [Constraint('!Len', '10.2.7.g: Do not lenite a genitive noun after an abstract feminine noun that is based on an adjective')]

      # 10.2.7.h handled after this block since verbal noun has no Case

      # TODO 10.2.7.i  Might need a list, even then tricky to tell
      # whether word is being used as common or verbal noun (e.g. lorg)

      if hd['lemma'] in gadata.feminineGroups:
        return [Constraint('!Len', '10.2.7.j: Do not lenite a genitive noun after various feminine noun for groups or organizations')]

      if self['lemma'] in ['dlí', 'sí']:
        return [Constraint('!Len', '10.2.7.k: Do not lenite “dlí” or “sí” after a feminine noun')]

      if self['lemma'] in ['bliain', 'coicís', 'mí', 'seachtain']:
        return [Constraint('!Len', '10.2.7.l: Do not lenite various units of time after a feminine noun')]

      if self.isQualifiedNoun():
        if hd['lemma'] in ['beirt', 'dís']:
          return [Constraint('Len', '10.2.7.m.e1: Lenite nouns after “beirt” or “dís” even if the genitive noun is modified by an adjective or another noun')]
        return [Constraint('!Len', '10.2.7.m: Do not lenite after a feminine noun if the genitive noun is modified by an adjective or another noun')]

      return [Constraint('Len', '10.2.7: Lenite a genitive singular noun following a feminine noun')]

    if hd.isVerbalNounWithAg() and self['deprel']=='obj' and self.has('Case','Gen'):
      if hd['lemma']=='fáil' and self['lemma']=='bás':
        return [Constraint('Len', '10.2.7.h.e1: Lenite the object of a feminine verbal noun in set phrase “ag fáil bháis”')]
      elif hd['lemma']=='gabháil' and self['lemma']=='fonn':
        return [Constraint('Len', '10.2.7.h.e2: Lenite the object of a feminine verbal noun in set phrase “ag gabháil fhoinn”')]
      else:
        return [Constraint('!Len', '10.2.7.h: Do not lenite the object of a feminine verbal noun following “ag”')]


    # 10.2.8 following slender plurals
    if hd.isNominal() and hd.has('Case','Nom') and hd.has('Number','Plur') and hd.hasSlenderFinalConsonant() and self.has('Case','Gen') and self.has('Number','Sing') and not self.anyPrecedingDefiniteArticle():
      if hd.hasFinalDental() and self.hasInitialDental():
        return [Constraint('!Len', '10.2.8.a: Do not lenite an initial dental after a plural noun ending in a slender dental')]
      if self.hasInitialF():
        return [Constraint('!Len', '10.2.8.b: Do not lenite an initial f after a plural noun ending in a slender consonant')]
      # 10.2.8.d,e need lists :(
      if self.isQualifiedNoun():
        if self['lemma']=='beirt':
          return [Constraint('Len', '10.2.8.f.e1: Lenite “beirt” following a plural noun ending in a slender consonant even when it is followed by a genitive')]
        else:
          return [Constraint('!Len', '10.2.8.f: Do not lenite a genitive singular noun following a plural noun ending in a slender consonant if it is modified by an adjective or another genitive noun')]

      return [Constraint('Len', '10.2.8: Lenite a genitive singular noun following a plural ending in a slender consonant')]

    # 10.2.9; include just for clearer error message
    if pr.isNominal() and pr.has('Case','Gen') and not self.has('Definite','Def') and hd['index']==self['index']-1:
      return [Constraint('!Len','10.2.9: Do not lenite following a genitive')]

    # 10.2.10 Nom. in form, genitive in function
    if self.has('Definite','Def') and self.has('Number','Sing') and not self.hasPrecedingDependent():
      if (self.isGenitiveOfHead() and hd['index']<self['index']) or self.isObjectFollowingVerbalNoun():
        if self.demutatedToken() in ['San','Dé']:
          return [Constraint('!Len','10.2.10.e1: Never lenite this token despite being definite in genitive position')]
        else:
          if hd['lemma'] != 'Dé' and self['lemma'] not in ['Béarla', 'Fál', 'Feirste', 'Fómhar', 'Gaeilge', 'Gaeltacht']:
            return [Constraint('Len','10.2.10: Should lenite a definite noun in genitive position')]

    # 10.2.11 Surnames
    if pr.has('PartType','Pat'):
      if pr['lemma'] in ['ní', 'uí']:
        return [Constraint('Len','10.2.11: Lenite surname after “ní” or “uí”')]
      elif re.search('^(mh?|n)[ai][cg]$', prToken):
        if self['lemma'].lower()[0] in ['c','g']:
          return [Constraint('!Len','10.2.11.e1: Should not lenite after Mhic, Nic, etc. when surname starts with C or G')]
        elif self['lemma'] in ['Treana']:
          return [Constraint('!Len','10.2.11.e2: Should not lenite after Mhic, Nic, etc. in certain special cases')]
        else:
          if prToken in ['mac', 'mag']:
            return [Constraint('Len|!Len','10.2.11: Some surnames lenite following “Mac” or “Mag”, others do not')]
          else:
            return [Constraint('Len','10.2.11: Lenite surname after Mhic, Nic, etc.')]

    # 10.2.12 Compound words; not relevant for us
    # 10.2.13 After copula
    if pr.has('VerbForm','Cop'):
      if pr.has('Tense','Past') or pr.has('Mood','Cnd'):
        return [Constraint('Len','10.2.13: Should lenite after past tense or conditional copula')]
      else:
        return [Constraint('!Len','10.2.13.e1: Should only lenite after a copula if it is past tense or conditional')]

    # TODO: Outside of C.O.
    # FGB is clear that degree particle PartType=Deg lenites

    return [Constraint('!Len','10.2: Not sure why this word is lenited')]

  def predictVerbLenition(self):
    if not self.isLenitable():
      return [Constraint('!Len', 'Cannot lenite an unlenitable letter')]
    lemma = self['lemma']
    if lemma=='abair':
      return [Constraint('!Len', '10.4.2.b: Forms of the verb “abair” are never lenited')]
    if lemma=='bí' and self['token'][0].lower()=='t':
      return [Constraint('!Len', '10.4: Do not lenite “tá”, “táimid”, etc.')]
    if self.has('Tense','Past') and self.has('Mood','Ind'):
      if self.has('Person','0'):
        if lemma in ['bí','clois','feic','tar','téigh']:
          return [Constraint('Len', '10.4.1.i.e1: Past autonomous verbs “bhíothas”, “chonacthas”, “chualathas”, “chuathas”, “thángthas” must be lenited')]
        else:
          return [Constraint('!Len', '10.4.1.i: Past autonomous verbs are normally not lenited')]
      else:
        if lemma=='faigh':  # abair handled above
          return [Constraint('!Len', '10.4.1.ii: Never lenite past tense forms of “faigh”')]
        else:
          return [Constraint('Len', '10.4.1.a: This past tense verb should be lenited')]
    if self.has('Aspect','Imp') and self.has('Tense','Past'):
      return [Constraint('Len', '10.4.1.a: This imperfect verb should be lenited')]
    if lemma=='faigh' and self.has('Tense','Fut') and self['token'].lower()[0]=='g':
      return [Constraint('Len', 'Independent future of “faigh” is lenited')]
    if self.has('Mood','Cnd'):
      return [Constraint('Len', '10.4.1.a: This conditional verb should be lenited')]
    pr = self.getRealPredecessor()
    if pr==None:
      return [Constraint('!Len', '10.4: This verb could only be lenited by a preceding particle')]
    # also "do" e.g. train line 1467?
    if pr['lemma']=='a' and pr['upos']=='PART' and pr.has('Form','Direct'):
      return [Constraint('Len', '10.4.1.b+c: Lenite after the direct relative particle “a”')]
    if pr['lemma'].lower() in ['má','ó'] and pr['upos']=='SCONJ' and not pr.has('VerbForm','Cop'):
      return [Constraint('Len', '10.4.1.b: Lenite after the conjunction “má” or “ó”')]
    if pr.isLenitingVerbalParticle():
      return [Constraint('Len', '10.4.2: Verb is lenited after this verbal particle')]
    return [Constraint('!Len','10.4: Not sure why this verb is lenited')]

  # TODO: ní haitheanta do (10.11.8.b)
  def predictAdjectivePrefixH(self):
    if not self.admitsPrefixH():
      return [Constraint('!HPref', '10.12: Can only have a prefix h before initial vowel')]
    pr = self.getRealPredecessor()
    if pr==None:
      return [Constraint('!HPref', '10.12: Cannot have a prefix h on an adjective at the start of a sentence')]
    prToken = pr['token'].lower()
    if prToken=='chomh':
      return [Constraint('HPref', '10.12.1: Adjective should have a prefix h after “chomh”')]
    if prToken=='go' and pr.has('PartType','Ad'):
      return [Constraint('HPref', '10.12.1: Adjective should have a prefix h after “go”')]
    if prToken=='ní' and pr['upos']=='AUX':
      # ní haon is NUM
      if self['lemma'] in ['amháin', 'annamh', 'eagal', 'ionann', 'iondúil', 'oircheas']:
        return [Constraint('HPref', '10.12.2.e1: Certain adjectives should have a prefix h after “ní”')]
      else:
        return [Constraint('!HPref', '10.12.2: Most adjectives do not take a prefix h after “ní”')]
    # "le haon" handled in predictFormDET
    # a haon, a hocht are in PredictFormNUM
    return [Constraint('!HPref', '10.12: Not sure why this adjective has a prefix h')]

  def predictNounPrefixH(self):
    if not self.admitsPrefixH():
      return [Constraint('!HPref', 'Can only have a prefix h before initial vowel')]
    pr = self.getRealPredecessor()
    if pr==None:
      return [Constraint('!HPref', 'Cannot have a prefix h at the start of a sentence')]
    prToken = pr['token'].lower()
    if prToken=='na' and self.has('Gender','Fem') and \
          self.has('Case','Gen') and self.has('Number','Sing'):
      return [Constraint('HPref', '10.11.1.a: Should have prefix h following “na” in the genitive')]
    if prToken in ['na','sna'] and self.has('Case','Nom') and \
          self.has('Number','Plur'):
      return [Constraint('HPref', '10.11.1.b: Should have prefix h following plural “na” or “sna”')]
    if pr.has('NumType','Ord') and pr['head']==self['index'] and pr['lemma']!='céad':
      return [Constraint('HPref', '10.11.2.a: Should have prefix h following an ordinal')]
    if pr.is3Thru6() and self.demutatedToken().lower()=='uaire':
      return [Constraint('HPref', '10.11.2.b: Should have prefix h on “uaire” following numbers 3-6')]
    # handles fixed "le hais" too
    if prToken in ['go','le'] and pr['upos']=='ADP':
      return [Constraint('HPref', '10.11.3: Should have prefix h after preposition “go” or “le”')]
    if prToken=='cá' and pr['upos']=='ADV':
      return [Constraint('HPref', '10.11.4: Should have prefix h following interrogative “cá”')]
    if prToken=='ó' and pr.has('PartType','Pat'):
      return [Constraint('HPref', '10.11.5: Surnames should have prefix h after “Ó”')]
    if pr['lemma']=='Dé' and self['lemma']=='Aoine':
      return [Constraint('HPref', '10.11.6: Should have prefix h in phrase “Dé hAoine”')]
    if pr.has('Poss','Yes') and pr.has('Gender','Fem'):
      return [Constraint('HPref', '10.11.7: Should have prefix h following feminine possessive')]
    if prToken=='dhá':
      prpr = pr.getRealPredecessor()
      if prpr!=None:
        if prpr.has('Poss','Yes') and prpr.has('Gender','Fem'):
          return [Constraint('HPref','10.11.7: Should have prefix h after feminine possessive + dhá')]
    if prToken=='ní' and pr['upos']=='AUX':
      if self['lemma'] in ['áibhéil','ionadh','iontas','ualach']:
        return [Constraint('HPref','10.11.8.a: Certain nouns get a prefix h after copula “ní”')]
      if self['lemma'] in ['áil','éadáil']:
        if any(t['lemma']=='le' for t in self.getDependents()):
          return [Constraint('HPref','10.11.8.b: There is a prefix h after “ní” in certain set copular phrases')]
      if self['lemma'] in ['acmhainn','aithnid','ealaín','éigean','eol']:
        if any(t['lemma']=='do' for t in self.getDependents()):
          return [Constraint('HPref','10.11.8.b: There is a prefix h after “ní” in certain set copular phrases')]
      # TODO: 10.11.8.c two set phrases
    if prToken=='de' and self['lemma']=='Íde':
      return [Constraint('HPref', 'Should have prefix h in “de hÍde”')]
    return [Constraint('!HPref', '10.11: Not sure why this noun has a prefix h')]

  def predictVerbPrefixH(self):
    if not self.admitsPrefixH():
      return [Constraint('!HPref', 'Can only have a prefix h before initial vowel')]
    pr = self.getRealPredecessor()
    if pr!=None and pr['token'].lower()=='ná' and pr.has('Mood','Imp'):
      return [Constraint('HPref', '10.14.1: Should have prefix h after “ná”')]
    return [Constraint('!HPref', '10.14: Not sure why this verb has a prefix h')]

  def predictEmphasis(self):
    # TODO: draw on lexicon to make iff prediction of Emp
    if re.search("([sn][ea]|se?an)$", self['token'].lower()):
      return [Constraint('Emp|!Emp', 'Could possibly be an emphatic ending but not certain')]
    return [Constraint('!Emp', 'Word does not have an emphatic ending')]

  # called from AUX, PART, PRON, SCONJ
  def predictVowelForm(self):
    if self['lemma']!='sibh' and re.search("b[’'h]?$", self['token'].lower()):
      return [Constraint('VF', 'Copula before vowel or f must have Form=VF')]
    return [Constraint('!VF', 'Form=VF not allowed without initial vowel or f')]

##################### predictFeatureUPOS methods #####################

  def predictAspectVERB(self):
    if self.has('Mood','Ind') and self.has('Tense','Pres') and \
        self['lemma']=='bí' and re.match('m?bh?í', self['token'].lower()):
      return [Constraint('Hab', 'Present habitual needs feature Aspect=Hab')]
    if self.has('Tense','Past') and self['Mood']==None:
      return [Constraint('Imp', 'Past tense but no Mood needs Aspect=Imp')]
    return [Constraint('None', 'Only imperfect and habitual present of “bí” have the Aspect feature')]

  def predictCaseADJ(self):
    return super().predictCaseADJ()

  # only Case=Gen
  def predictCaseDET(self):
    head = self.getUltimateHead()
    # TODO: exception if genitive head noun is nummod of a cardinal
    # "dúshlán na seacht dtúr"
    if head.isNominal() and self['lemma']=='an':
      if head.has('Case','Gen'):
        return [Constraint('Gen', 'Article before any genitive noun should have Case=Gen')]
    return [Constraint('None', 'Not sure why this determiner has the Case feature')]

  def predictCaseNOUN(self):
    return [Constraint('Nom|Gen|Dat|Voc|None', 'placeholder...')]
    if self.getUltimateDeprel()=='vocative':
      return [Constraint('Voc', 'Should have feature Case=Voc')]

    if self.has('Abbr','Yes') or self.has('Foreign','Yes'):
      return [Constraint('None', 'Abbreviations and foreign words generally do not have a Case feature')]

    # some have Gen; are these true vns
    if self['VerbForm']!=None:
      return [Constraint('None', 'Verbal nouns generally do not have a Case feature')]

    if self['lemma'] in ['ann', 'dála', 'foláir', 'leor', 'márach', 'scan', 'scun', 'seach', 'té', 'tólamh', 'uile']:
      return [Constraint('None', 'This is one of a small number of nouns that are not marked for Case')]

    # before we get into Gen after compound preps, mark noun after "go dtí"
    if any(t.isGodti() and t['deprel']=='case' for t in self.getDependents()):
      return [Constraint('Nom', 'Noun should be nominative after “go dtí”')]

    # nominative in form after numbers, even in genitive case
    if any(t['upos']=='NUM' and t['deprel']=='nummod' and t['index']<self['index'] for t in self.getDependents()):
      return [Constraint('Nom', 'Noun should be nominative after a number')]

    if self.isObjectOfGenitivePrep():
      if self.hasPropagatingDefiniteDependent():
        return [Constraint('Nom', 'Noun should be nominative in form despite being in genitive position after this preposition')]
      else:
        return [Constraint('Gen', 'Noun should be in the genitive case after this preposition')]

    if self.isInPP():
      return [Constraint('Nom|Dat', 'Noun should be in nominative or dative case after this preposition')]

    # propagate these Dat/Gen through coordinations: "gan ord ná eagar"?

    if self['lemma']=='déag':
      return [Constraint('Nom', 'The word “déag” always gets Case=Nom')]

    if self.isGenitiveOfHead():
      if self.hasPropagatingDefiniteDependent():
        return [Constraint('Nom', 'Noun should be nominative in form despite being genitive in function')]
      else:
        if self.getHead()['lemma'] == 'cúpla':
          return [Constraint('Nom', 'Noun should be in nominative following “cúpla”')]
        else:
          return [Constraint('Gen', 'This noun modifies another noun and should therefore be in the genitive case')]

    # then set genitives if it's an object of VN
    if self.getHead().isVerbalNounWithAg() and self['deprel']=='obj':
      if self.hasPropagatingDefiniteDependent():
        return [Constraint('Nom', 'Noun should be nominative in form despite being genitive in function')]
      else:
        return [Constraint('Gen', 'The object of a verbal noun with “ag” should be in the genitive case')]

    return [Constraint('Nom', 'Noun should be in nominative by default')]

  def predictCasePROPN(self):
    return [Constraint('Nom|Gen|Dat|Voc|None', 'placeholder...')]
    #return self.predictCaseNOUN()

  def predictDefiniteDET(self):
    lemma = self['lemma']
    if lemma=='an' or re.search('^(an|gach.*|achan)$', lemma):
      return [Constraint('Def', 'This determiner should have Definite=Def')]
    return [Constraint('None', 'Not sure why this word has the Definite feature')]

  def predictDefiniteNOUN(self):
    if self.precedingCen() or self.anyDependentDefiniteArticle():
      return [Constraint('Def', '3.1.2.b: Needs Definite=Def because of preceding article')]
    if self.isPossessed():
      return [Constraint('Def', '3.1.2.c: Needs Definite=Def because of preceding possessive adjective')]
    if self.hasGachDependent():
      return [Constraint('Def', '3.1.2.d: Needs Definite=Def because of “gach”')]
    if self.hasNumberSpecifier():
      return [Constraint('Def', '3.1.2.e: Needs Definite=Def because of the number that follows')]
    if self.hasPropagatingDefiniteDependent():
      return [Constraint('Def', '3.1.2.f: Needs Definite=Def because of definite nominal dependent')]
    hd = self.getHead()
    if self.has('PrepForm','Cmpd') and self['lemma']!='dtí' and hd['deprel']=='case' and hd.getHead().has('Definite','Def'):
      return [Constraint('Def', '3.1.2.f: Noun in compound preposition needs Definite=Def because of definite nominal dependent')]
    # ceol agus litríocht na Gaeltachta => litríocht needs Definite=Def too
    if self['deprel']=='conj' and hd.hasPropagatingDefiniteDependent(self['index']):
      return [Constraint('Def', '3.1.2.f: Needs Definite=Def because of definite nominal dependent')]
    if self.has('Case','Voc') or self['deprel']=='vocative':
      return [Constraint('Def', '3.1.2.g: All vocatives need Definite=Def')]
    return [Constraint('None', '3.1: Not sure why this has the Definite feature')]

  def predictDefinitePROPN(self):
    if self.isIndefinitePROPN():
      return self.predictDefiniteNOUN()
    else:
      return [Constraint('Def', '3.1.2.a: Most proper nouns need Definite=Def')]

  def predictDegreeADJ(self):
    # if it's amod and not comp/sup, it gets features from NOUN => no Degree
    if self.isAttributiveAdjective():
      return [Constraint('None', 'Attributive adjectives should not have the Degree feature')]
    pr = self.getRealPredecessor()
    if pr==None:
      return [Constraint('Pos', 'Must be Degree=Pos at start of sentence')]
    prToken = pr['token'].lower()
    if pr['lemma'] in ['ba','níos'] and pr.has('PartType','Comp'):
      return [Constraint('Cmp', 'Must have Degree=Cmp after “níos” or “ba”'),
              Constraint('Sup', 'Must have Degree=Sup after “níos” or “ba”')]
    # TODO: really should be abstract noun following "a" — retag?
    if pr['lemma']=='a' and pr.has('PartType','Deg'):
      return [Constraint('Cmp', 'Must have Degree=Cmp after degree particle “a”'),
              Constraint('Sup', 'Must have Degree=Sup after degree particle “a”')]
    # "is" only other word preceding ADJ with Degree=Cmp,Sup; mixed tags
    if pr['lemma']=='is':
      if pr.has('PartType','Comp') or pr.has('PartType','Sup'):
        return [Constraint('Cmp', 'Must have Degree=Cmp after copula'),
                Constraint('Sup', 'Must have Degree=Sup after copula')]
      # Should we change tags when it's AUX to distinguish "is ard é" from
      # comparatives like "is airde sliabh ná cnoc"
      if pr['upos']=='AUX':
        return [Constraint('Cmp|Pos|Sup', 'Unsure which Degree tag after copula')]

    # Cmp,Sup is possible ("níos réitithe"), but caught with rules above
    if self.has('VerbForm','Part'):
      return [Constraint('None', 'No degree for verbal adjectives unless comparative')]

    # go leor, but as an adverbial "maith go leor"...
    # "leor" is tagged NOUN in "go leor cainte"
    if self['lemma']=='leor' and self['deprel']=='fixed':
      return [Constraint('None', 'No Degree feature in fixed adverbial phrase')]

    return [Constraint('Pos', 'Should default to Degree=Pos')]

  def predictFormADJ(self):
    ans = self.predictAdjectiveLenition()
    ans.extend(self.predictAdjectivePrefixH())
    return ans

  def predictFormADP(self):
    pr = self.getRealPredecessor()
    if pr==None:
      return [Constraint('None', 'Prepositions usually do not have a Form')]
    prToken = pr['token'].lower()
    # annoying fixed phrases...
    if self['deprel']=='fixed' and \
       ((prToken=='go' and self['token'].lower()=='dtí') or \
        (prToken=='i' and self['token'].lower() in ['bhfeighil','dteannta','dtrátha','dtús','gceann','gcionn','gcoinne','gcóir','gcoitinne','mbun','ndiaidh'])):
      return [Constraint('Ecl', 'Should be eclipsed in set phrase')]
    else:
      return [Constraint('None', 'Prepositions usually do not have a Form')]

  # just in one set phrase; get rid of fixed or retag components?
  # TODO: ní hamhlaidh  10.12.2?
  def predictFormADV(self):
    if self['lemma']=='bheith' and self['deprel']=='fixed' and \
         self.getHead()['lemma']=='thar':
      return [Constraint('Len', 'Need Form=Len on “bheith” in this set phrase')]
    return [Constraint('None', 'Adverbs usually do not have a Form')]

  # VF, Ecl, Len (a few have both Ecl and VF)
  def predictFormAUX(self):
    ans = self.predictVowelForm()
    # Eclipsis: go mba, dá mba, etc.
    if self.isEclipsable() and self.getRealPredecessor()['lemma'] in ['dá','go']:
      ans.append(Constraint('Ecl', 'Should be eclipsed by preceding particle'))
    else:
      ans.append(Constraint('!Ecl', 'Copula is sometimes eclipsed, but not here'))
    if self['token'].lower()[:3]=='cha':
      ans.append(Constraint('Len', 'Copula “chan” requires the Form=Len feature'))
    else:
      ans.append(Constraint('!Len', 'Not sure why this copula has Form=Len'))
    return ans

  # Ecl, Len, HPref, e.g. i ngach, chuile, haon (10.12.1)
  def predictFormDET(self):
    if self['token'].lower() in ['chaon', 'chuile']:
      return [Constraint('Len', 'Certain abbreviated determiners are lenited')]
    pr = self.getRealPredecessor()
    if pr==None:
      return [Constraint('None', 'No Form feature for sentence initial determiners')]
    if self['lemma']=='gach':
      if pr['token'].lower()=='i':
        return [Constraint('Ecl', 'Should be eclipsed by preceding “i”')]
      else:
        return [Constraint('None', '10.3.2.eii: The determiner “gach” is only mutated after “i”')]
    if pr['token'].lower()=='le' and self['lemma']=='aon':
      return [Constraint('HPref', '10.12.1: Should have prefix h in phrase “le haon”')]
    if pr['token'].lower()=='na' and pr.has('Case','Gen') and self['lemma']=='uile':
      return [Constraint('Ecl', 'Should be eclipsed in genitive plural')]
    if self['lemma'] in ['cibé', 'do', 'mo', 'pé']:
      return [Constraint('None', '10.3.2.eii/10.7.a: Certain determiners are never mutated')]
    return [Constraint('None', 'Determiners usually do not have a Form')]

  # Ecl, Len, HPref, Emp
  def predictFormNOUN(self):
    if self.has('Abbr','Yes'):
      return [Constraint('None', '3.2.1.a: Abbreviations should never be mutated')]
    if self.has('Foreign','Yes'):
      return [Constraint('None', 'Non-Irish words should never be mutated')]
    ans = self.predictEmphasis()
    ans.extend(self.predictNounLenition())
    ans.extend(self.predictNounEclipsis())
    ans.extend(self.predictNounPrefixH())
    return ans

  # Ecl, Len, HPref
  def predictFormNUM(self):
    ans = []
    tok = self['token'].lower()
    pr = self.getRealPredecessor()
    if pr==None:
      return [Constraint('None', 'Sentence-initial numbers should not have the Form feature')]
    prToken = pr['token'].lower()

    # Ecl, Len
    if self['lemma']=='céad' and self.has('NumType','Ord') and \
       self.anyPrecedingDefiniteArticle() and not self.getHead().isInDativePP():
      ans.append(Constraint('Len', '10.3.2.ei: Lenite “céad” when it is an ordinal'))
    elif prToken=='faoin' and self['lemma'].lower()=='céad':
      ans.append(Constraint('Ecl', 'Should be eclipsed in set phrase'))
    elif tok in ['dá', 'dhá']:
      if self.anyPrecedingDefiniteArticle() and pr.has('Number','Sing') and prToken!='na':
        ans.append(Constraint('None', 'Use form “dá” after definite article'))
      else:
        ans.append(Constraint('Len', 'Use form “dhá” unless following definite article'))
    elif self['head']==self['index']+1:  # 10.7 => just like nouns
      ans.extend(self.predictNounEclipsis())
      ans.extend(self.predictNounLenition())

    # HPref
    if self.admitsPrefixH():
      # le haon (10.12.1) handled in predictFormDET
      if prToken == 'a' and pr.has('PartType','Num'):
        ans.append(Constraint('HPref', '10.12.3: Number should have a prefix h after counting particle “a”'))
      elif prToken == 'na' and pr.has('Number','Plur'):
        ans.append(Constraint('HPref', '10.12.3: Number should have a prefix h after plural article “na”'))
      else:
        ans.append(Constraint('!HPref', '10.12: Not sure why this number has a prefix h'))
    else:
      ans.append(Constraint('!HPref', 'Can only have a prefix h before initial vowel'))

    return ans

  # Direct, Indirect, and (rarely) Len, VF, Ecl (le n-a mbaineann)
  def predictFormPART(self):
    ans = self.predictVowelForm()
    if self.has('PronType','Rel'):
      ans.append(Constraint('Direct|Indirect', 'Relative particles must have Form feature'))
    else:
      ans.append(Constraint('!Direct', 'Only relative particles can have Form=Direct'))
      ans.append(Constraint('!Indirect', 'Only relative particles can have Form=Indirect'))
    if self.has('PartType','Pat') and self['token'] in ['Mhac', 'Mhic']:
      ans.append(Constraint('Len', 'This patronymic requires Form=Len'))
    else:
      ans.append(Constraint('!Len', 'Patronymics Mhac and Mhic are only lenited particles'))
    ans.append(Constraint('!Ecl', 'No particles are eclipsed in the standard language'))
    return ans

  def predictFormPRON(self):
    # Form=VF (rare — just "cérbh"?)
    ans = self.predictVowelForm()
    pr = self.getRealPredecessor()

    if self.admitsPrefixH():
      if pr==None:
        ans.append(Constraint('!HPref', '10.13: Cannot have prefix h on a sentence-initial pronoun'))
      else:
        # "pé" not in C.O. explicitly, but in FGB
        if pr['token'].lower() in ['cé', 'cia', 'ní', 'pé'] and self['lemma'] in ['é', 'í', 'ea', 'iad']:
          ans.append(Constraint('HPref', '10.13.1: Should have a prefix h on this pronoun following “cé” or “ní”'))
        elif pr['token'].lower()=='ní' and self['lemma'] in ['éard', 'eo', 'in', 'iúd']:
          ans.append(Constraint('HPref', '10.13.2: Should have a prefix h on this demonstrative pronoun following “ní”'))
        elif pr['token'].lower()=='le' and self['lemma'] in ['é', 'í', 'iad']:
          ans.append(Constraint('HPref', '10.13.3: Should have a prefix h on this pronoun following “le”'))
        else:
          ans.append(Constraint('!HPref', 'Not sure why we would have a prefix h on this pronoun'))
    else:
      ans.append(Constraint('!HPref', 'Can only have a prefix h before initial vowel'))

    # Form=Len; non-standardly "fhéin"
    if self['lemma']=='tú' and self['deprel']=='obj':
      ans.append(Constraint('Len', 'Should be lenited form “thú” when it is an object'))
    elif self['lemma']=='ceachtar':
      ans.extend(self.predictFormNOUN())
    elif self['lemma']=='sin' and pr!=None and pr['token'].lower() in ['o','ó']:
      ans.append(Constraint('Len', 'Should be lenited in set phrase “ó shin”, or else should be “uaidh sin”'))
    else:
      ans.append(Constraint('!Len', 'Not sure why this pronoun is lenited'))
    return ans

  # Ecl, Len, HPref
  def predictFormPROPN(self):
    return self.predictFormNOUN()

  # (rarely) VF (murab, arb), 1x Len (dhá for dá)
  def predictFormSCONJ(self):
    ans = self.predictVowelForm()
    return ans

  # Ecl, Len, HPref, Emp, plus some with Direct (atá + relative forms)
  def predictFormVERB(self):
    ans = []
    tempans = self.predictVerbEclipsis()
    if any(c.isSatisfied(['Ecl']) for c in tempans):
      ans.append(Constraint('!Len', 'Should not lenite in an eclipsis context'))
    else:
      ans.extend(self.predictVerbLenition())
    if self.isEclipsable():
      ans.extend(tempans)
    else:
      ans.append(Constraint('!Ecl', '10.8: Not an eclipsable initial letter'))

    ans.extend(self.predictEmphasis())
    if self.has('PronType','Rel') and re.match(r'at[aá]',self['token'].lower()):
      ans.append(Constraint('Direct', 'Anything resembling atá should have direct relative feature Form=Direct'))
    ans.extend(self.predictVerbPrefixH())
    return ans

  def predictGenderADP(self):
    if self.has('Number','Sing') and self.has('Person','3'):
      return [Constraint('Fem|Masc', '3rd person singular ADP must be marked for Gender')]
    return [Constraint('None', 'Not sure why this preposition has a Gender')]

  def predictGenderADJ(self):
    return super().predictGenderADJ()

  # only in non-standard combined forms
  def predictGenderAUX(self):
    mapping = {'sé': 'Masc', 'sí': 'Fem'}
    if self['token'].lower() in mapping:
      return [Constraint(mapping[self['token'].lower()], 'Combined copula requires correct Gender feature')]
    return [Constraint('None', 'Copula generally does not permit a Gender feature')]

  def predictGenderDET(self):
    if self.has('Number','Sing'):
      if self.has('Poss','Yes') and self.has('Person','3'):
        return [Constraint('Fem|Masc', '3rd person singular possessive must be marked for Gender')]
      if self.has('PronType','Art') and self.has('Case','Gen'):
        if re.match("'?[Nn]", self['token']):
          return [Constraint('Fem', 'Article before genitive singular feminine noun must be marked for Gender')]
        if re.match("'?[Aa]", self['token']):
          return [Constraint('Masc', 'Article before genitive singular masculine noun must be marked for Gender')]
    return [Constraint('None', 'Not sure why this determiner has a Gender')]

  # could have a list of exceptions but doesn't add much value
  # since missing genders would be picked up by lexicon check
  def predictGenderNOUN(self):
    return [Constraint('Fem|Masc|None', 'Allow anything for now...')]

  def predictGenderPROPN(self):
    return self.predictGenderNOUN()

  def predictGenderPRON(self):
    pronouns = {'é': 'Masc', 'eisean': 'Masc', 'í': 'Fem', 'ise': 'Fem', 'sé': 'Masc', 'seisean': 'Masc', 'sí': 'Fem', 'sise': 'Fem'}
    if self['lemma'] in pronouns:
      return [Constraint(pronouns[self['lemma']], 'Personal pronouns require correct Gender feature')]
    else:
      return [Constraint('None', 'Not sure why this pronoun has a gender')]

  # TODO: gur
  def predictMoodAUX(self):
    tok = self.demutatedToken().lower()
    if tok in ["b'", 'ba']:
      if self.has('Tense','Past'):
        return [Constraint('None', 'Past copula “ba” is not conditional; should not have a Mood feature')]
      else:
        return [Constraint('Cnd', 'Copula “ba”, if not past tense, is conditional, requiring Mood=Cnd')]
    elif tok=='gur':
      if self['Tense']!=None:
        return [Constraint('None', 'Present or past copula “gur” is not conditional; should not have a Mood feature')]
      else:
        return [Constraint('Cnd', 'Copula “gur”, if not present or past tense, is conditional, requiring Mood=Cnd')]
    elif tok=='an':
      return [Constraint('Int', 'Copula “an” is an interrogative; requires Mood=Int')]
    elif tok=='nach':
      return [Constraint('Int|None', 'Might or might not be an interrogative')]
    elif tok in ['ar', 'arbh', 'nár', 'nárbh']:
      return [Constraint('Cnd|Int|None', 'Might or might not be an interrogative; might or might not be conditional')]
    else:
      return [Constraint('None', 'Not sure why this copula has a Mood feature')]

  def predictMoodPART(self):
    head = self.getHead()
    if self['lemma']=='ná' and head.has('Mood','Imp'):
      return [Constraint('Imp', 'Negative imperative particle requires feature Mood=Imp')]
    if self['lemma'] in ['go', 'nár'] and head.has('Mood','Sub'):
      return [Constraint('Sub', 'Subjunctive particle requires feature Mood=Sub')]
    return [Constraint('None', 'Not sure why this particle has a Mood feature')]

  def predictMoodVERB(self):
    # distinguishing the moods is a lexical thing; handle with dict lookup
    if self.has('Aspect','Imp'):
      return [Constraint('None', 'Imperfect verbs should not have a Mood')]
    else:
      return [Constraint('Cnd|Imp|Ind|Int|Sub', 'All non-imperfect verbs must have the Mood feature')]

  # Strong|Weak|Slender|NotSlender
  def predictNounTypeADJ(self):
    # include deprel nmod here because of coordinations through gen. sing nouns
    if self.has('Number','Plur') and self.getUltimateDeprel() in ['amod','nmod']:
      head = self.getUltimateHead()
      if head.has('Case','Nom'):
        if head.hasSlenderFinalConsonant():
          return [Constraint('Slender', 'Plural adjective modifying noun with slender ending; needs NounType=Slender feature')]
        else:
          return [Constraint('NotSlender', 'Plural adjective modifying noun ending in broad consonant or vowel needs NounType=NotSlender feature')]
      elif head.has('Case','Gen'):
        if head['NounType']!=None:
          val = head['NounType'][0]
          return [Constraint(val, 'Plural adjective must have NounType=Strong or Weak matching the noun it modifies')]
    return [Constraint('None', 'Not sure why this adjective has a NounType')]

  def predictNounTypeNOUN(self):
    # NB nouns don't take Slender/NotSlender feature, only their dependent adjs
    if self.has('Number','Plur') and self.has('Case','Gen'):
      # distinction is a lexical thing; almost true that you could
      # compare demutatedToken with lemma, but there are exceptions b/c of
      # non-standard tokens, typos, and examples like "ealaíon"
      return [Constraint('Strong|Weak', 'Genitive plural nouns need NounType=Strong or Weak')]
    return [Constraint('None', 'Not sure why this noun has a NounType feature')]

  def predictNounTypePROPN(self):
    return self.predictNounTypeNOUN()

  def predictNumberAUX(self):
    if self['token'].lower() in ['sé','sí']:
      return [Constraint('Sing', 'Combined copula requires Number feature')]
    else:
      return [Constraint('None', 'Copula normally does not permit a Number feature')]

  # TODO: beirt
  def predictNumberADJ(self):
    if self.isAttributiveAdjective():
      head = self.getUltimateHead()
      if head.has2Thru19():
        return [Constraint('Plur', 'Should be plural adjective after 2-19')]
      if head['Number']!=None:
        theNumber = head['Number'][0]
        return [Constraint(theNumber, 'Adjective number should match noun it modifies')]
      else:
        return [Constraint('None', 'Modified noun has no Number feature so this adjective should not either')]
    else:
      return [Constraint('None', 'Non-attributive adjectives do not take the Number feature')]

  def predictNumberADP(self):
    if self.has('PronType','Art'):
      if re.search('na$', self['token'].lower()): # "sna" only std example
        return [Constraint('Plur', 'Should be Number=Plur since combined with plural article')]
      else:
        return [Constraint('Sing', 'Should be Number=Sing since combined with singular article')]
    if self.has('Poss','Yes'):
      return [Constraint('Sing|Plur', 'All possessives should have a Number feature')]
    if self['Person']!=None:
      tok = self.deemphasizedToken().lower()
      if re.search('(bh|[ií]nn$|[auú]b?$|le[oó]$)', tok):
        return [Constraint('Plur', 'Appears to be a plural pronomial so requires Number=Plur')]
      else:
        return [Constraint('Sing', 'Appears to be a singular pronomial so requires Number=Sing')]
    return [Constraint('None', 'Not sure why this word has a Number feature')]

  def predictNumberDET(self):
    possessives = {'ár': 'Plur', 'bhur': 'Plur', 'do': 'Sing', 'mo': 'Sing'}
    if self['lemma'] in possessives:
      return [Constraint(str(possessives[self['lemma']]), 'Possessives should have the correct Number feature')]
    if self['lemma']=='an':
      if self['token'].lower() in ['an','a',"'n","a'","un"]:
        return [Constraint('Sing', 'Singular article requires Number=Sing')]
      else:
        return [Constraint('Sing|Plur', 'Article “na” requires a Number feature, either singular or plural')]
    if self['lemma']=='a':
      return [Constraint('Sing|Plur', 'Possessive “a” must be annotated either singular or plural')]
    return [Constraint('None', 'Not sure why this determiner has a Number feature')]

  def predictNumberNOUN(self):
    if self['Abbr']!=None:
      return [Constraint('Sing|Plur|None', 'Abbreviations may or may not have a Number feature')]
    elif self['Foreign']!=None:
      return [Constraint('Sing|Plur|None', 'Foreign words may or may not have a Number feature')]
    elif self['VerbForm']!=None:
      return [Constraint('None', 'Verbal nouns cannot have a Number feature')]
    elif self['lemma'] in ('dtí', 'leor'):
      return [Constraint('None', 'By convention, there is no Number feature in set phrases “go dtí” or “go leor”')]
    else:
      return [Constraint('Sing|Plur', 'All nouns except verbal nouns, abbreviations, and foreign words must have a Number feature')]

  def predictNumberPRON(self):
    # cén is Sing, but cé, céard have no Number
    if self['lemma']=='cé':
      if self['token'].lower()=='cén':
        return [Constraint('Sing', 'Pronoun “cén” must be Number=Sing')]
      else:
        return [Constraint('None', 'Pronouns “cé” and “céard” should have no Number feature')]
    pronouns = {'é': 'Sing', 'ea': 'Sing', 'eisean': 'Sing', 'í': 'Sing', 'iad': 'Plur', 'ise': 'Sing', 'mé': 'Sing', 'mise': 'Sing', 'muid': 'Plur', 'sé': 'Sing', 'seisean': 'Sing', 'sí': 'Sing', 'siad': 'Plur', 'sibh': 'Plur', 'sinn': 'Plur', 'sise': 'Sing', 'tú': 'Sing', 'tusa': 'Sing'}
    if self['lemma'] in pronouns:
      return [Constraint(pronouns[self['lemma']], 'Pronouns should have the correct Number feature')]
    else:
      return [Constraint('None', 'Not sure why this pronoun has a Number feature')]

  def predictNumberPROPN(self):
    return self.predictNumberNOUN()

  def predictNumberVERB(self):
    return [Constraint('Sing|Plur|None', 'Some verbs have Number feature')]

  def predictNumTypeNUM(self):
    # optional cases usually contain numbers or parens
    # Card vs. Ord mostly detectable with token?
    return [Constraint('Card|Ord|None', 'Numbers have optional NumType feature')]

  def predictPartTypePART(self):
    if self['lemma'] in ['an','ar','cha','chan','gur','ná','níor']:
      return [Constraint('Vb', 'This particle should always be PartType=Vb')]
    if self['lemma'] in ['de','mac','mag','nic','o','ó','uí']:
      return [Constraint('Pat', 'This particle should always be PartType=Pat')]
    if self['lemma']=='a':
      return [Constraint('Cop|Deg|Inf|Num|Vb|Voc', 'If the word “a” is a particle, it must be one of these particle types')]
    if self['lemma']=='ba':
      return [Constraint('Comp', 'If “ba” is a particle, it must be PartType=Comp')]
    if self['lemma']=='do':
      if self.getHead()['upos']=='NOUN':
        return [Constraint('Inf', 'Here, “do” should be PartType=Inf')]
      if self.getHead()['upos']=='VERB' and not self.has('Form','Indirect'):
        return [Constraint('Vb', 'Here, “do” should be PartType=Vb')]
    # go => Cmpl, Ad, Vb
    if self['lemma']=='go':
      if self.getHead()['upos']=='ADJ':
        return [Constraint('Ad','Should have PartType=Ad in adverbial phrase')]
      if self.has('Mood','Sub'):
        return [Constraint('Vb','Subjunctive particle should have PartType=Vb')]
      # TODO: handle go+AUX  (go mba shólás leis sin); copula isn't the head!
      if self.getHead()['upos'] in ['VERB']:
        return [Constraint('Cmpl','Here, “go” should have PartType=Cmpl')]
    if self['lemma']=='is':
      return [Constraint('Comp|Sup', 'The particle “is” should have PartType=Comp or Sup')]
    if self['lemma'] in ['nach', 'nár'] and self.getHead()['upos']=='VERB':
      # Form=Direct or Direct, also Mood=Sub (nár lige Dia é) => Vb
      if self['Form']!=None: # Direct or Indirect
        return [Constraint('Vb', 'Relative particle needs PartType=Vb')]
      else:
        return [Constraint('Cmpl', 'Here, complementizer needs PartType=Cmpl')]
    if self['lemma']=='ní':
      return [Constraint('Comp|Pat|Vb', 'The particle “ní” is one of these types')]
    if self['lemma']=='níos':
      return [Constraint('Comp', 'The particle “níos” needs PartType=Comp')]
    # indirect relativizers are the only PART tokens without a PartType
    if self.has('Form', 'Indirect'):
      return [Constraint('None', 'Indirect relativizers do not have a PartType feature')]
    return [Constraint('None', 'Not sure why this has a PartType feature')]

  def predictPersonADP(self):
    if self.has('Poss','Yes'):
      # could add ár$ => 1, a$=>3, etc.
      return [Constraint('1|2|3', 'All possessives should have a Person feature')]
    if self['Number']!=None and not self.has('PronType','Art'):
      # final m => 1, final t => 2, ann=>3, other final nn=>1, etc.?
      return [Constraint('1|2|3', 'All pronomials should have a Person feature')]
    return [Constraint('None', 'Not sure why this word has a Person feature')]

  def predictPersonAUX(self):
    if self['token'].lower() in ['sé','sí']:
      return [Constraint('3', 'Combined copula requires Person feature')]
    return [Constraint('None', 'Copula usually does not have a Person feature')]

  def predictPersonDET(self):
    if self.has('Poss','Yes'):
      possessives = { 'a': 3, 'ár': 1, 'bhur': 2, 'do': 2, 'mo': 1 }
      if self['lemma'] in possessives:
        return [Constraint(str(possessives[self['lemma']]), 'Possessives should have the correct Person feature')]
    return [Constraint('None', 'Not sure why this determiner has a Person feature')]

  def predictPersonPRON(self):
    pronouns = {'é': 3, 'ea': 3, 'eisean': 3, 'í': 3, 'iad': 3, 'ise': 3, 'mé': 1, 'mise': 1, 'muid': 1, 'sé': 3, 'seisean': 3, 'sí': 3, 'siad': 3, 'sibh': 2, 'sinn': 1, 'sise': 3, 'tú': 2, 'tusa': 2}
    if self['lemma'] in pronouns:
      return [Constraint(str(pronouns[self['lemma']]), 'Pronouns should have the correct Person feature')]
    return [Constraint('None', 'Not sure why this pronoun has a Person feature')]

  def predictPersonVERB(self):
    return [Constraint('0|1|2|3|None', 'Verbs sometimes have the Person feature')]

  def predictPolarityAUX(self):
    if re.match('(n|cha)', self['token'].lower()):
      return [Constraint('Neg', 'Negative copula should have Polarity=Neg')]
    return [Constraint('None', 'Not sure why this copula has a Polarity feature')]

  def predictPolarityPART(self):
    if not self.has('PartType','Comp') and not self.has('PartType','Pat') and \
          re.match('(n[^-]|cha)', self['token'].lower()):
      return [Constraint('Neg', 'Negative particle should have Polarity=Neg')]
    return [Constraint('None', 'Not sure why this particle has a Polarity feature')]

  def predictPolarityVERB(self):
    pr = self.getRealPredecessor()
    if re.match('níl',self['token'].lower()) or \
        (pr!=None and pr.has('Polarity','Neg')):
      return [Constraint('Neg', 'Verb following negative particle must have Polarity=Neg feature')]
    return [Constraint('None', 'Not sure why this verb has a Polarity feature')]

  def predictPossADP(self):
    return [Constraint('Yes|None', 'ADP could have Poss=Yes')]

  def predictPossDET(self):
    if self['PronType']!=None:  # Art, Dem, Ind
      return [Constraint('None', 'Determiner with a PronType cannot have Poss=Yes')]
    if self.has('Definite','Def'): # gach, chuile, etc.
      return [Constraint('None','Determiners like “gach” do not have Poss=Yes')]
    if self.has('Foreign','Yes'):
      return [Constraint('None','Foreign words do not have Poss=Yes')]
    return [Constraint('Yes', 'This determiner should have Poss=Yes')]

  # Deprel is Usually case in PPs, but can be mark ("go dtí go mbeidh...")
  def predictPrepFormADP(self):
    if self['deprel'] in ['case','mark'] and self['head']>self['index']+1 and \
          any(t['index']==self['index']+1 and t['upos']=='NOUN' and t['deprel']=='fixed' for t in self.getDependents()):
      return [Constraint('Cmpd', 'First part of compound preposition should have feature PrepForm=Cmpd')]
    return [Constraint('None', 'Does not appear to need PrepForm=Cmpd feature')]

  # second halves tagged NOUN as of April 2021
  # note the check that head of the ADP isn't "self"
  def predictPrepFormNOUN(self):
    pr = self.getRealPredecessor()
    cmpd = pr['token'].lower()+' '+self['token'].lower()
    if self['deprel']=='fixed':
      h = self.getHead()
      if (cmpd in gadata.compoundPrepositions  or cmpd == 'go dtí') and\
           h['upos']=='ADP' and h['deprel'] in ['case','mark'] and \
           h['head']>self['index'] and self['head']==self['index']-1:
        return [Constraint('Cmpd', 'Second part of compound preposition should have feature PrepForm=Cmpd')]
    else:
      if (cmpd in gadata.compoundPrepositions or cmpd == 'go dtí') and \
          any(t.isGenitivePosition() for t in self.getDependents()):
        return [Constraint('Cmpd', 'This should be fixed and PrepForm=Cmpd')]
    return [Constraint('None', 'Does not appear to need PrepForm=Cmpd feature')]

  def predictPronTypeADP(self):
    tok = self['token'].lower()
    # values: Art, Emp, Prs, Rel (rare)
    if tok in ['á', 'dhá'] and self['lemma']=='do' and \
        self.getDeprel()=='case' and self.getHead().has('VerbForm','Inf'):
      return [Constraint('Prs', 'Particle “á” before verbal noun needs PronType=Prs feature')]
    if re.match('(dá|(faoi|i|le|ó|trí)nar?)$',tok) and \
        not self.has('Poss','Yes') and self.getDeprel() != 'case':
      return [Constraint('Rel', 'Appears to be combined preposition with “a” (all that) and need PronType=Rel feature')]
    if tok=='insa':  # do this first since it looks emphatic by regex
      return [Constraint('Art', 'The word “insa” takes PronType=Art')]
    if re.search('..(s[ae]|ne|se?an)$', tok):
      return [Constraint('Emp', 'This appears to be an emphatic form, requiring PronType=Emp')]
    if tok in gadata.prepositionsWithArticle:
      return [Constraint('Art', 'This word should have PronType=Art')]
    return [Constraint('None', 'Not sure why this has feature PronType')]

  def predictPronTypeADV(self):
    # includes surface form "cár"
    if self['lemma'] in ['cá', 'conas']:
      return [Constraint('Int', 'These interrogatives require PronType=Int')]
    return [Constraint('None', 'Not sure why this adverb has feature PronType')]

  def predictPronTypeAUX(self):
    # Rel or Dem (rare)
    if self['token'].lower() in ['seo','sin']:
      return [Constraint('Dem', 'Feature PronType=Dem is required here')]
    else:
      return [Constraint('Rel|None', 'Some copulas are PronType=Rel')]

  # Art, Dem, Ind, and possessives+gach don't have this feature at all
  def predictPronTypeDET(self):
    if self['lemma']=='an':
      return [Constraint('Art', 'Definite article requires PronType=Art')]
    if self['lemma'] in ['eile','s','seo','sin','siúd','úd']:
      return [Constraint('Dem', 'Demonstratives require PronType=Dem')]
    if self['lemma'] in ['aon','cibé','uile']:
      return [Constraint('Ind', 'Indef. determiner requires PronType=Ind')]
    if self.has('Poss','Yes') or self.has('Definite','Def') or \
       self.has('Foreign','Yes'):
      return [Constraint('None', 'Should not have feature PronType')]
    return [Constraint('ERR', 'Unrecognized determiner; unsure about the PronType feature')]

  # Rel only
  def predictPronTypePART(self):
    # lemmas: a, ar, do, faoi, i, le, nach, nár, trí
    if self.has('Form','Direct') or self.has('Form','Indirect') or \
        self.has('PartType','Cop'):
      return [Constraint('Rel', 'Relativizing particles must have feature PronType=Rel')]
    return [Constraint('None', 'Not sure why this particle has feature PronType')]

  # possible values: Dem, Int, Emp, Rel, Ind (or none)
  def predictPronTypePRON(self):
    # lemma of emphatics is a bit inconsistent at present; use token
    if self['token'].lower() in ['eisean', 'iadsan', 'ise', 'mise', 'muide', 'muidne', 'seisean', 'siadsan', 'sinne', 'sise', 'tusa']:
      return [Constraint('Emp', 'Emphatic pronouns require PronType=Emp')]
    if self['lemma'] in ['é', 'ea', 'féin', 'í', 'iad', 'mé', 'muid', 'sé', 'séard', 'sí', 'siad', 'sibh', 'sinn', 'tú']:
      return [Constraint('None', 'Basic personal pronouns do not take the PronType feature')]
    if self['lemma'] in ['cad', 'cad_é', 'cé', 'céard']:
      return [Constraint('Int', 'Interrogative pronouns require PronType=Int')]
    if self['lemma'] in ['iúd', 'seo', 'sin', 'siúd']:
      return [Constraint('Dem', 'Demonstrative pronouns require PronType=Dem')]
    if self['lemma'] in ['a', 'ar']:
      return [Constraint('Rel', 'Relativizing pronouns require PronType=Rel')]
    if self['lemma'] in ['ceachtar', 'cibé', 'pé']:
      return [Constraint('Ind', 'Indefinite pronouns require PronType=Ind')]
    return [Constraint('ERR', 'Unrecognized pronoun; unsure of PronType feature in this case')]

  # only Rel
  def predictPronTypeVERB(self):
    tok = self['token'].lower()
    # atá, atáthar, atáim, atáimse, atáid, etc.
    if re.match('at[aá]',tok):
      return [Constraint('Rel', 'Forms like “atá” require the feature PronType=Rel')]
    # oibríonns, but not "chlis", "fuarthas", "fhásas", "dhéanfaidís", ...
    if re.search('s$',tok) and not self.has('Tense','Past') and \
        not self.has('Number','Plur') and not self.has('Aspect','Hab'):
      return [Constraint('Rel', 'This verb form ending in s likely requires PronType=Rel')]
    return [Constraint('None', 'Not sure why this verb has feature PronType')]

  def predictReflexPRON(self):
    if self['lemma']=='féin':
      return [Constraint('Yes', 'The word “féin” needs feature Reflex=Yes')]
    return [Constraint('None', 'Only the lemma “féin” takes the feature Reflex=Yes')]

  # Sinn Féin
  def predictReflexPROPN(self):
    if self['lemma']=='Féin':
      return [Constraint('Yes', 'The word “Féin” in “Sinn Féin” needs feature Reflex=Yes')]
    return [Constraint('None', '“Féin” in “Sinn Féin” is the only proper noun with the feature Reflex=Yes')]

  def predictTenseADV(self):
    if self['token'].lower()=='cár':
      return [Constraint('Past', 'Past tense interrogative “cár” should have Tense=Past before a regular verb')]
    return [Constraint('None', 'Adverbs do not normally take a Tense feature')]

  def predictTenseAUX(self):
    if self.has('Mood','Cnd'):
      return [Constraint('None', 'Conditional copulas do not take a Tense feature')]
    else:
      tok = self['token'].lower()
      if re.search('(^[am]?b|bh$|^níor)', tok):
        return [Constraint('Past', 'Appears to be a past tense copula requiring Tense=Past')]
      elif tok in ['an', 'nach', 'ní', 'gurb'] or re.search('^i?s', tok):
        return [Constraint('Pres', 'Appears to be a present tense copula requiring Tense=Pres')]
      else:  # gur, ar
        return [Constraint('Past|Pres', 'Copulas that are not conditional must be marked as present or past tense')]

  # only Tense=Past is possible
  # easier than AUX since stuff like "gur" is unambiguously Tense=Past
  def predictTensePART(self):
    tok = self['token'].lower()
    # iff ends in r, except for one negative subjunctive "nár" in IUDT training
    if re.search('r$',tok) and not self.has('Mood','Sub'):
      return [Constraint('Past', 'Special past tense particles ending in -r should have Tense=Past feature')]
    # same condition as in predictVerbFormPART
    if self['lemma']=='is' and re.search('b',tok) and \
       (self.has('PartType','Comp') or self.has('PartType','Sup')):
      return [Constraint('Past', "Particle ”ba” or “ab” in comparative or superlative constructions must have Tense=Past feature")]
    return [Constraint('None', 'Not sure why this particle has Tense feature')]

  # Pres or Past
  def predictTenseSCONJ(self):
    tok = self['token'].lower()
    if tok in ['murar','sarar','sular']:
      if self.has('VerbForm','Cop'):
        return [Constraint('Past|Pres', 'This copula form should be tagged with Tense=Past or Tense=Pres, depending on context')]
      else:
        return [Constraint('Past', 'Special past tense conjunctions should have Tense=Past before a regular verb')]
    elif tok in ['mura','murab','sularb']:
      if self.has('VerbForm','Cop'):
        return [Constraint('Pres', 'These copular conjunctions should have feature Tense=Pres')]
      else:
        return [Constraint('None', 'These conjunctions do not take the Tense feature before a present tense verb')]
    return [Constraint('None', 'Not sure why this conjunction has Tense feature')]

  # just checks if it's there when appropriate
  # could check it in presence of certain verb particles/conjunctions?
  def predictTenseVERB(self):
    return super().predictTenseVERB()

  # only VerbForm=Part on some adjectives
  def predictVerbFormADJ(self):
    if self.has('Degree','Pos'):
      return [Constraint('None', 'We do not use VerbForm=Part with Degree=Pos')]
    if self['Case']!=None:
      return [Constraint('None', 'We do not use VerbForm=Part with attributive adjectives having Case, etc.')]
    # remainder are comparative/superlative; these are rarely
    # verbal adjectives, but may be, so we will allow it:
    return [Constraint('Part|None', 'Adjectives can have VerbForm=Part feature')]

  def predictVerbFormAUX(self):
    return [Constraint('Cop', 'Copulas must have VerbForm=Cop feature')]

  # Inf, Vnoun, or nothing
  # plenty of overlap with Case, etc. so might need review of guidelines
  def predictVerbFormNOUN(self):
    return super().predictVerbFormNOUN()

  # only Cop (and rarely)
  def predictVerbFormPART(self):
    # same condition as in predictTensePART
    if self['lemma']=='is' and re.search('b',self['token'].lower()) and \
       (self.has('PartType','Comp') or self.has('PartType','Sup')):
      return [Constraint('Cop', 'Some comparative/superlative particles have VerbForm=Cop feature')]
    return [Constraint('None', 'Not sure why this particle has a VerbForm')]

  # Cop only
  def predictVerbFormPRON(self):
    # rare: cérbh, cér currently
    if self['token'].lower() in ['cér', 'cérbh']:
      return [Constraint('Cop', 'Interrogative pronouns “cér” and “cérbh” take the VerbForm=Cop feature')]
    return [Constraint('None', 'Not sure why this pronoun has a VerbForm')]

  # Cop only
  def predictVerbFormSCONJ(self):
    if self['token'].lower() in ['arb', 'dar', 'más', 'murab', 'murarbh', 'ós', 'sularb']:
      return [Constraint('Cop', 'This conjunction requires the VerbForm=Cop feature')]
    if self['token'].lower() in ['mura', 'murar', 'sular']:
      return [Constraint('Cop|None', 'This conjunction is sometimes a copula with VerbForm=Cop, othertimes not')]
    return [Constraint('None', 'Not sure why this conjunction has a VerbForm')]

  # none in current version of treebank!
  # but see CO 10.9.1.b (aon, aonú, ochtó, ochtódú, ochtú)
  # (and no ts- if it's séú, seachtú, seascadú, etc.... 10.10.2.a)
  def predictXFormADJ(self):
    return [Constraint('TPref|None', 'placeholder...')]

  # only case here is "(an) t-aon X"
  def predictXFormDET(self):
    if self['lemma']=='aon':
      if (self.precedingDefiniteArticle() or self.precedingCen()) and \
           not self.getHead().isInDativePP():
        return [Constraint('TPref', '10.9.1.b: Should be “t-aon” after definite article')]
    return [Constraint('None', '10.9: Not sure why this determiner has a prefix t')]

  def predictXFormNOUN(self):
    if self.hasInitialVowel():
      # Exceptions in CO for oiread/iomad but these are genderless in treebank
      # so including here just for clearer message and CO reference
      if self['lemma'] in ['oiread', 'iomad', 'euro']:
        return [Constraint('None', '10.9.1.b: Should never add prefix t to “euro”, “iomad”, or “oiread”')]
      elif self.has('Number','Sing') and self.has('Gender','Masc') and \
           self.has('Case','Nom') and not self.isInDativePP() and \
          (self.precedingDefiniteArticle() or self.precedingCen()):
        return [Constraint('TPref', '10.9.1.a: Should have prefix t before masculine noun after an article')]
      else:
        return [Constraint('None', '10.9.1: Not sure why this noun has a prefix t')]
    elif self.hasLenitableS():
      pr = self.getRealPredecessor()
      prToken = pr['token'].lower()
      if self.has('Number','Sing') and self.has('Gender','Fem') and \
           self.has('Case','Nom') and \
          (self.anyPrecedingDefiniteArticle() or self.precedingCen()):
        return [Constraint('TPref', '10.10.1: Should have prefix t before feminine noun after an article')]
      elif self.has('Number','Sing') and self.has('Gender','Masc') and \
           self.has('Case','Gen') and self.precedingDefiniteArticle():
        return [Constraint('TPref', '10.10.1: Should have prefix t before genitive masculine noun after an article')]
      elif self.anyPrecedingDefiniteArticle() and self.has('Case','Nom') and self.has('Gender','Masc') and self.isInDativePP() and pr.has('Number','Sing') and prToken!='na':
        return [Constraint('!TPref', '1.4.2 (An Córas Lárnach): Should not add prefix t to a masculine noun with an initial s'), Constraint('TPref', '1.7.4 (Córas an tSéimhithe): Should add prefix t to a masculine noun with an initial s in the dative')]
      else:
        if pr['lemma'] in ['aon','céad']:
          return [Constraint('None', '10.10.2.b: No prefix t following “aon” or “céad”')]
        else:
          return [Constraint('None', '10.10: Not sure why this noun has a prefix t')]
    else:
      return [Constraint('None', '10.9/10: Prefix t on a word that cannot admit one')]

  def predictXFormNUM(self):
    if self.hasInitialVowel():
      hd = self.getHead()
      if hd.has('Number','Sing') and hd.has('Case','Nom') and \
          not hd.isInDativePP() and \
          (self.precedingDefiniteArticle() or self.precedingCen()):
        return [Constraint('TPref', '10.9.1.b: Should have prefix t before nominative singular noun after an article')]
      else:
        return [Constraint('None', '10.9.1.b: Not sure why this number has a prefix t')]
    elif self.hasLenitableS():
      return [Constraint('None', '10.10.2.a: Numbers beginning with s do not take a prefix t')]
    else:
      return [Constraint('None', '10.9/10: Prefix t on a word that cannot admit one')]

  def predictXFormPROPN(self):
    return self.predictXFormNOUN()

  ########################################################################

  def lowerToken(self):
    s = self['token']
    if len(s) > 1 and (s[0]=='t' or s[0]=='n') and s[1] in 'AEIOUÁÉÍÓÚ':
      return s[0]+'-'+s[1:].lower()
    else:
      return s.lower()

  # TODO: handle (h)acmhainní or p(h)obal?
  def demutatedToken(self):
    s = self['token']
    if s[:2] in ['n-','t-']:
      return s[2:]
    if re.match('[nt][AEIOUÁÉÍÓÚ]',s):
      return s[1:]
    if re.match('h[aeiouáéíóú]',s,flags=re.IGNORECASE) and re.match('[aeiouáéíóú]',self['lemma'],flags=re.IGNORECASE):
      return s[1:]
    if re.match('bhf',s,flags=re.IGNORECASE):
      return s[2:]
    if re.match('(mb|gc|n[dg]|bp|ts|dt)',s,flags=re.IGNORECASE):
      return s[1:]
    if re.match('[bcdfgmpst]h',s,flags=re.IGNORECASE):
      return s[0]+s[2:]
    return s

  def deemphasizedToken(self):
    s = self['token']
    if self.has('Form', 'Emp') or self.has('PronType', 'Emp'):
      if s.lower()[-3:]=='nne':
        return s[:-1]   # againne -> againn, etc.
      else:
        return re.sub('-?[ns][ea]n?$', '', s, flags=re.IGNORECASE)
    else:
      return s
