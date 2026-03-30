import re
from goidelic import GoidelicToken
from rules import Constraint

class GVToken(GoidelicToken):
  
  def __init__(self, lineNumber=None, line=None):
    super().__init__(lineNumber, line)

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

  # don't bother with Abbr, Foreign, Typo
  def checkableFeatures(self):
    return [
            'Case',
            'Definite',
            'Degree',
            'Form',
            'Gender',
            'Mood',
            'Number',
            'PartType',
            'Person',
            'Polarity',
            'Poss',
            'PronType',
            'Reflex',
            'Tense'
           ]

  def predictFeatureValue(self, feat):
    return getattr(GVToken, 'predict'+feat+self['upos'], GVToken.noConstraint)(self)

####################### BOOLEAN METHODS ##########################

  # houney/sauin
  def isLenited(self):
    tok = self['token'].lower()
    lem = self['lemma'].lower()
    # Practical Manx p. 19
    return (re.match('[bm][^w]',lem) and tok[:1]=='v' and tok!='vel') or \
           (re.match('([bm]w|f.|s[ln]|[çcst]h).',lem) and tok[:2]==lem[1:3]) or\
           (re.match('[bm].',lem) and tok[:2]=='w'+lem[1]) or \
           (re.match('[ck][^h]',lem) and tok[:2] == 'ch') or \
           (re.match('f.',lem) and tok[:2]=="'"+lem[1]) or\
           (lem[:1] in 'gp' and tok[:2] == lem[0]+'h') or \
           (lem[:2]=='gi' and tok[:2]=='yi') or \
           (lem[:2]=='qu' and tok[:2]=='wh') or \
           (re.match('[st][^h]',lem) and tok[:2]=='h'+lem[1]) or \
           (lem[:3]=='shl' and tok[:1]=='l') or \
           (lem[:2]=='sl' and tok[:2]=="'l") or \
           (lem[:3]=='str' and tok[:2]=='hr') or \
           (lem[:1]=='d' and tok[:2]=='gh') or \
           (lem[:1]=='d' and tok[:3]=='w'+lem[1:3]) or \
           (re.match('j.', lem) and tok[:2]=='y'+lem[1]) or \
           (lem=='abbyr' and re.match('yi?ar',tok)) or \
           (lem=='cur' and tok[:3]=='hug') or \
           (lem=='faik' and re.match('(hee|honnick)',tok)) or \
           (lem=='fow' and re.match('(hooar|yio)',tok)) or \
           (lem=='gow' and re.match('h[ie]',tok)) or \
           (lem=='jean' and tok[:3]=='yin') or \
           (lem=='tar' and tok[:3]=='hig') or \
           (lem=='olk' and tok[:3]=='ves') or \
           tok=='houney'

  def isEclipsed(self):
    tok = self['token'].lower()
    lem = self['lemma'].lower()
    return (lem[:1]=='b' and tok[:1]=='m' and lem[:3]!='ben') or \
           (lem=='bee' and tok=='vel') or \
           (lem[:1] in 'ck' and tok[:1]=='g') or \
           (lem[:2]=='çh' and tok[:1]=='j') or \
           (lem[:1] in 'dgj' and tok[:1]=='n' and lem!='jean') or \
           (lem[:1]=='f' and tok[:1] in 'nv') or \
           (lem[:1]=='p' and tok[:1]=='b') or \
           (lem[:1]=='t' and tok[:1]=='d') or \
           (lem=='abbyr' and tok[:1]=='n') or \
           (lem=='bee' and tok=='vel') or \
           (lem=='cur' and re.match('(ver|dug)',tok)) or \
           (lem=='fow' and tok=='dooar') or \
           (lem=='gow' and tok[:2]=='je') or \
           (lem=='tar' and tok[:3]=='jig')

  def hasPrefixT(self):
    tok = self['token'].lower()
    lem = self['lemma'].lower()
    return (lem[:1]=='s' and tok[:1]=='t') or \
           (lem[:2]=='sh' and re.match('[cç]h',tok)) or \
           (lem[:2]=='sl' and tok[:2]=='cl')

  def hasPrefixH(self):
    tok = self['token'].lower()
    lem = self['lemma'].lower()
    return re.match('h-?[aeiou]',tok) and re.match('[aeiou]',lem)

####################### END BOOLEAN METHODS ##########################

  # TODO: PM p.21
  def predictNounEclipsis(self):
    pr = self.getPredecessor()
    if pr.isPluralPossessive():
      return [Constraint('Ecl','Should be eclipsed by preceding possessive')]
    return []

  def predictNounHPref(self):
    return []

  def predictNounLenition(self):
    return []

  # TODO: PM p.21
  def predictVerbEclipsis(self):
    return []

  # TODO: PM p.5
  def predictVerbLenition(self):
    return []

  # any POS really, but aimed at NOUN/VERB
  def predictEmphatic(self):
    tok = self['token'].lower()
    if re.search('[^y]s$', tok) and self['lemma'][-1]!='s':
      return [Constraint('Emp|None', 'Could be an emphatic form')]
    return []

####################### START PREDICTORS ##########################
  def noConstraint(self):
    return []

  def predictCaseDET(self):
    # TODO: check for singular NOUN eventually
    if self['token'].lower()=='ny':
      return [Constraint('Gen|None', 'Could be article before genitive feminine singular')]
    return []

  def predictDefiniteDET(self):
    if self['lemma']=='yn':
      return [Constraint('Def', 'Definite articles require Definite=Def')]
    return []

  # just Cmp,Sup for now
  def predictDegreeADJ(self):
    # weak check; permitted any time token differs from lemma
    # can't even check initial s' because of copula forms (s'laik, etc.)
    if self['token'].lower() != self['lemma']:
      return [Constraint('Cmp|Sup|None', 'Could be a comparative or superlative adjective')]
    return []

  # only Len
  def predictFormADJ(self):
    return [Constraint('Len|None', 'placeholder...')]
    return []

  # Ecl, Emp, HPref, Len
  def predictFormNOUN(self):
    return [Constraint('Ecl|Emp|HPref|Len|None', 'placeholder...')]
    ans = self.predictNounEclipsis()
    ans.extend(self.predictNounHPref())
    ans.extend(self.predictNounLenition())
    ans.extend(self.predictEmphatic())
    return ans

  # only Len; TODO: PM pp. 7-11
  def predictFormNUM(self):
    return [Constraint('Len|None', 'placeholder...')]
    return []

  def predictFormPROPN(self):
    return self.predictFormNOUN()

  # Ecl, Emp, Len
  def predictFormVERB(self):
    return [Constraint('Ecl|Emp|Len|None', 'placeholder...')]
    ans = self.predictVerbEclipsis()
    ans.extend(self.predictVerbLenition())
    ans.extend(self.predictEmphatic())
    return ans

  # genitive singular article
  def predictGenderDET(self):
    if re.match("n[y']?$", self['token'].lower()):
      if self.has('PronType','Art'):
      # TODO: check for singular NOUN eventually
        return [Constraint('Fem|None', 'Could be article before genitive feminine singular')]
      if self.has('Poss','Yes'):
        return [Constraint('Fem|Masc', 'Possessive form “ny” must have Gender feature')]
    if self['lemma']=='e':
      return [Constraint('Fem|Masc', 'Ambiguous 3rd person singular possessive must have Gender feature')]
    return []

  def predictGenderPRON(self):
    if self['lemma'] == 'ee':
      return [Constraint('Fem', 'Feminine pronoun should have Gender=Fem')]
    if self['lemma'] == 'eh':
      return [Constraint('Masc', 'Masculine pronoun should have Gender=Masc')]
    return []

  def predictMoodVERB(self):
    # distinguishing the moods is a lexical thing; handle with dict lookup
    return [Constraint('Cnd|Imp|Ind', 'All verbs must have the Mood feature')]

  def predictNumberADJ(self):
    tok = self['token'].lower()
    if tok != self['lemma'] and tok[-2:]=='ey':
      return [Constraint('Plur|None', 'Looks like it could be plural')]
    return []

  # articles and possessives
  def predictNumberDET(self):
    if self['lemma'] == 'yn':
      if self['token'].lower()=='ny':
        # TODO: check following noun
        return [Constraint('Sing|Plur|None', 'Could be plural article or genitive feminine singular')]
      else:
        return [Constraint('Sing', 'Appears to be a singular article, requiring Number=Sing')]
    elif self.has('Poss','Yes'):
      if self['lemma'] in ['my','dty','e', 'ny']:
        return [Constraint('Sing', 'Appears to be a singular possessive, requiring Number=Sing')]
      elif self['lemma'] == 'nyn':
        return [Constraint('Plur', 'Appears to be a plural possessive, requiring Number=Plur')]
    return []

  def predictNumberPRON(self):
    if self['lemma'] in ['ee','eh','mee','oo','ou']:
      return [Constraint('Sing', 'Singular pronoun should have Number=Sing')]
    if self['lemma'] in ['ad','mayd','shin','shiu']:
      return [Constraint('Plur', 'Plural pronoun should have Number=Plur')]
    return []

  # TODO: could check endings, -ym => Sing, -mayd or -jee => Plur
  def predictNumberVERB(self):
    return [Constraint('Sing|Plur|None', 'Some verbs have a Number feature')]

  def predictPartTypeADP(self):
    head = self.getHead()
    if self['lemma']=='y' and self['deprel']=='mark' and \
      head['upos']=='NOUN' and head['index']==self['index']+1:
        return [Constraint('Inf', 'This looks like an infinite particle requiring PartType=Inf')]
    return []

  def predictPartTypePART(self):
    head = self.getHead()
    lemma = self['lemma']
    if lemma=='cha':
      if head['upos']=='VERB' and head['index']==self['index']+1:
        return [Constraint('Vb', 'This looks like a verbal particle requiring PartType=Vb')]
    if lemma=='dy':
      if head['upos']=='VERB' and head['index']==self['index']+1:
        return [Constraint('Cmpl', 'This looks like a verbal particle requiring PartType=Cmpl')]
      elif head['upos']=='ADJ' and head['index']==self['index']+1:
        return [Constraint('Ad','Should have PartType=Ad in adverbial phrase')]
    if lemma=='nagh':
      if head['upos']=='VERB' and head['index']==self['index']+1:
        return [Constraint('Cmpl|Vb','Should be PartType=Cmpl or PartType=Vb')]
    if lemma=='ny':
      if head['upos']=='VERB' and head.has('Mood','Imp'):
        return [Constraint('Vb','Negative imperative particle should have PartType=Vb')]
      if head['upos']=='ADJ' and head.has('Degree','Cmp'):
        return [Constraint('Comp','Comparative particle should have PartType=Comp')]
    if lemma=='y':
      if self['deprel']=='case:voc':
        return [Constraint('Voc','Vocative particle should have PartType=Voc')]
    return []

  def predictPersonDET(self):
    possessives = {'dty': 2, 'e': 3, 'my': 1, 'ny': 3}
    if self['lemma'] in possessives:
      return [Constraint(str(possessives[self['lemma']]), 'Possessives must have the correct Person feature')]
    elif self['lemma']=='nyn':
      return [Constraint('1|2|3', 'Ambiguous plural possessive must have the Person feature')]
    return []

  def predictPersonPRON(self):
    pronouns = {'ad': 3, 'ee': 3, 'eh': 3, 'mayd': 1, 'mee': 1, 'oo': 2, 'ou': 2, 'shin': 1, 'shiu': 2}
    if self['lemma'] in pronouns:
      return [Constraint(str(pronouns[self['lemma']]), 'Personal pronouns must have the correct Person feature')]
    return []

  # code hard code certain endings, as in predictNumberVERB
  def predictPersonVERB(self):
    return [Constraint('1|2|3|None', 'Some verbs have the Person feature')]

  def predictPolarityAUX(self):
    if self['token'].lower() in ['cha','nagh']:
      self.addFeature('Polarity','Neg')
      return [Constraint('Neg', 'Negative copula forms should have Polarity=Neg')]
    return []

  def predictPolarityPART(self):
    if self['token'].lower() in ['cha','chan','nagh','nar','nara']:
      self.addFeature('Polarity','Neg')
      return [Constraint('Neg', 'Negative particles should have Polarity=Neg')]
    return []

  def predictPossDET(self):
    if self['lemma'] in ['dty','e','my','nyn']:
      return [Constraint('Yes', 'Possessives need Poss=Yes feature')]
    if self['deprel']=='nmod:poss':
      return [Constraint('Yes', 'Anything with nmod:poss should have Poss=Yes')]
    if self['lemma']=='ny' and not self.has('PronType','Art'):
      return [Constraint('Yes', 'When “ny” is a determiner but not the definite article, it should have Poss=Yes')]
    return []

  def predictPronTypeDET(self):
    if self['lemma']=='yn':
      return [Constraint('Art', 'Definite articles require PronType=Art')]
    return []

  def predictPronTypePRON(self):
    tok = self['token'].lower()
    if tok in ['adhene', 'adsyn', 'eshyn', 'ish', 'meehene', 'mish', 'shinyn', 'shiuish', 'uss']:
      return [Constraint('Emp', 'Emphatic pronouns require PronType=Emp')]
    if self['lemma'] in ['shen', 'shoh']:
      return [Constraint('Dem', 'Demonstrative pronouns require PronType=Dem')]
    return []

  def predictReflexPRON(self):
    if self['lemma']=='hene':
      return [Constraint('Yes', 'Reflexive pronoun “hene” requires Reflex=Yes')]
    return []
  
  # tensed verbs are precisely those with Mood=Ind (for now)
  def predictTenseVERB(self):
    if self.has('Mood','Ind'):
      return [Constraint('Past|Pres|Fut', 'Verbs in indicative mood must have a Tense feature')]
    return []
