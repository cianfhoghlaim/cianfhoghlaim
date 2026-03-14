import re
from goidelic import GoidelicToken
from rules import Constraint

class GDToken(GoidelicToken):
  
  def __init__(self, lineNumber=None, line=None):
    super().__init__(lineNumber, line)

  # also "Foreign"
  def checkableFeatures(self):
    return [
            'Case',
            'Degree',
            'Form',
            'Gender',
            'Mood',
            'Number',
            #'PartType',
            #'Person',
            'Polarity',
            'Poss',
            'PronType',
            'Reflex',
            'Tense',
            'VerbForm'
           ]

  def autosetFeatures(self):
    if self.isLenited():
      self.addFeature('XForm','Len')
    if self.isEclipsed():
      self.addFeature('XForm','Ecl')
    if self.hasPrefixH():
      self.addFeature('XForm','HPref')

  def predictFeatureValue(self, feat):
    return getattr(GDToken, 'predict'+feat+self['upos'], GDToken.noConstraint)(self)

  ####################### START BOOLEAN METHODS ##########################

  def isLenited(self):
    return (self['token'][0].lower() != self['lemma'][0].lower()) or (self['lemma'][1].lower()!='h' and re.match('^[cgp]h',self['token'].lower()))

  def isEclipsed(self):
    return False

  # additional exceptions in Gàidhlig, mostly fixed adjectival phrases:
  # sam bith, mu dheireadh, thall
  def isAttributiveAdjective(self):
    return super().isAttributiveAdjective() and \
      self['lemma'] not in ['a-muigh', 'a-staigh', 'fa-leth', 'mu', 'muigh', 'sam', 'tall']

  ######################## END BOOLEAN METHODS ###########################

  def noConstraint(self):
    return []

  def predictCaseADJ(self):
    return super().predictCaseADJ()

  # TODO: see Irish; base this on if head noun is Case=Gen?
  def predictCaseDET(self):
    if self['lemma']=='an':
      return [Constraint('Gen|None', 'Some articles are annotated Case=Gen')]
    return []

  # TODO... complicated like Irish
  def predictCaseNOUN(self):
    return [Constraint('Nom|Gen|Dat|Voc|None', 'placeholder...')]

  def predictCasePROPN(self):
    return self.predictCaseNOUN()

  # TODO: tighten up by doing this when preceded by PartType=Comp
  # and in that case requiring *both* Cmp and Sup since that seems 
  # to be the convention here...
  def predictDegreeADJ(self):
    return [Constraint('Cmp|Sup|None', 'Adjectives are sometimes Degree=Cmp,Sup')]

  def predictFormPRON(self):
    if self['token'].lower() in ['àsan', 'esan', 'iadsan', 'ise', 'mis\'', 'mise', 'sibhse', 'sinne', 'thus\'', 'thusa', 'tusa']:
      return [Constraint('Emp', 'Emphatic pronouns require Form=Emp')]
    return []

  # checks agreement with NOUN if amod
  def predictGenderADJ(self):
    return super().predictGenderADJ()

  def predictGenderDET(self):
    if self['lemma']=='an' and not self.has('Poss','Yes'):
      return [Constraint('Fem|Masc|None', 'Some articles have Gender feature')]
    if self['lemma']=='a' and self.has('Poss','Yes') and self.has('Person','3'):
      return [Constraint('Fem|Masc', '3rd person possessive requires Gender feature')]
    return []

  def predictGenderNOUN(self):
    return [Constraint('Fem|Masc|None', 'placeholder...')]

  def predictGenderPRON(self):
    if self['lemma']=='a' and self.has('Poss','Yes'):
      return [Constraint('Fem|Masc', '3rd person possessive requires Gender feature')]
    pronouns = {'e': 'Masc', 'è': 'Masc', 'i': 'Fem', 'ì': 'Fem'}
    if self['lemma'] in pronouns:
      return [Constraint(pronouns[self['lemma']], 'Personal pronouns require correct Gender feature')]
    return []

  def predictGenderPROPN(self):
    return self.predictGenderNOUN()

  def predictMoodAUX(self):
    if self['token'].lower() == 'an':
      return [Constraint('Int', 'Copula “an” requires feature Mood=Int')]
    if self['token'].lower() == 'nach':
      return [Constraint('Int|None', 'Copula “nach” sometimes has Mood=Int')]
    return []

  def predictMoodVERB(self):
    if self['Tense']==None and not self.has('Foreign','Yes'):
      return [Constraint('Cnd|Imp', 'Non-foreign verbs without Tense require Mood feature')]
    return []

  # doesn't generalize to Goidelic because of Irish examples like
  # "dhá fhear mhóra"
  def predictNumberADJ(self):
    if self.isAttributiveAdjective():
      head = self.getUltimateHead()
      if head['Number']!=None:
        theNumber = head['Number'][0]
        return [Constraint(theNumber, 'Adjective number should match noun it modifies')]
    return []

  def predictNumberDET(self):
    if self['lemma']=='an' and not self.has('Poss','Yes'):
      return [Constraint('Sing|Plur|Dual', 'Articles must have Number feature')]
    if self.has('Poss','Yes'):
      possessives = {'an': 'Plur', 'ar': 'Plur', 'ur': 'Plur', 'do': 'Sing', 'mo': 'Sing', 'a': 'Sing'}
      if self['lemma'] in possessives:
        return [Constraint(possessives[self['lemma']], 'Possessives require correct Number feature')]
    return []

  def predictNumberNOUN(self):
    if self['Foreign']==None and self['VerbForm']==None:
      return [Constraint('Sing|Plur|None', 'Most nouns except verbal nouns have a Number feature')]
    return []

  def predictNumberPRON(self):
    # same as above under DET
    if self.has('Poss','Yes'):
      possessives = {'an': 'Plur', 'ar': 'Plur', 'ur': 'Plur', 'do': 'Sing', 'mo': 'Sing', 'a': 'Sing'}
      if self['lemma'] in possessives:
        return [Constraint(possessives[self['lemma']], 'Possessives require correct Number feature')]
    else:
      pronouns = {'àsan': 'Plur', 'e': 'Sing', 'è': 'Sing', 'i': 'Sing', 'ì': 'Sing', 'iad': 'Plur', 'mi': 'Sing', 'mis\'': 'Sing', 'sib\'': 'Plur', 'sibh': 'Plur', 'sinn': 'Plur', 'thu': 'Sing'}
      if self['lemma'] in pronouns:
        return [Constraint(pronouns[self['lemma']], 'Pronouns require correct Number feature')]
    return []

  def predictPartTypePART(self):
    return []

  def predictPersonDET(self):
    return []

  def predictPersonPRON(self):
    return []

  # Irish marks Person=3 also
  def predictPersonVERB(self):
    return [Constraint('0|1|2|None', 'Verbs sometimes have the Person feature')]

  def predictPolarityAUX(self):
    tok = self['token'].lower()
    if tok in ['an', 'gun', 'gur']:
      return [Constraint('Aff', 'This copula should have Polarity=Aff')]
    if tok in ['cha', 'chan', 'nach']:
      return [Constraint('Neg', 'This copula should have Polarity=Neg')]
    return []

  def predictPolarityPART(self):
    tok = self['token'].lower()
    if tok in ['cha', 'chan', 'na', 'nach']:
      return [Constraint('Neg', 'This particle should have Polarity=Neg')]
    if tok == 'na':
      return [Constraint('Neg|None', 'This particle sometimes has Polarity=Neg')]
    return []

  def predictPossDET(self):
    if self['lemma'] in ['ar','do','mo','ur']:
      return [Constraint('Yes', 'This possessive requires Poss=Yes')]
    if self['lemma']=='a':
      "a h-uile"
      if any(t['lemma']=='uile' and t['deprel']=='fixed' for t in self.getDependents()):
        return []
      else:
        return [Constraint('Yes', 'This possessive requires Poss=Yes')]
    if self['lemma']=='an':
      # no better way to distinguish these from definite article an/am...
      if self['deprel'] in ['nmod:poss', 'obj']:
        return [Constraint('Yes', 'This possessive requires Poss=Yes')]
    return []

  def predictPossPRON(self):
    return self.predictPossDET()

  # usually, but not always, before superlative ADJ
  def predictPronTypeAUX(self):
    return [Constraint('Rel|None', 'Copulae sometimes have PronType=Rel')]

  def predictPronTypePART(self):
    if self.has('PartType','Vb'):
      if self['lemma']=='na' and self.has('Polarity','Neg'):
        return []
      else:
        return [Constraint('Int|Rel', 'Verbal particles should have PronType')]
    return []

  # only PronType=Int, about 4% of all PRON (dè, cò, etc.)
  def predictPronTypePRON(self):
    return [Constraint('Int|None', 'Some pronouns have PronType=Int')]

  # Irish is just lemma 'féin'
  def predictReflexPRON(self):
    if re.search('^(f[eéè]in|c[eéè]ile|a-chèile)$', self['lemma']):
      return [Constraint('Yes', 'Both “fèin” and “chèile” require Reflex=Yes')]
    if self['lemma']=='a' and any(re.search('^c[eéè]ile$',t['lemma']) and t['index']==self['index']+1 for t in self.getDependents()):
      return [Constraint('Yes', 'The “a” in “a chèile” requires Reflex=Yes')]
    return []

  # unlike ga, no Mood=Cnd
  def predictTenseAUX(self):
    return [Constraint('Past|Pres', 'Copulas be marked as present or past tense')]

  def predictTensePART(self):
    if self['lemma']=='do':
      return [Constraint('Past', 'Verbal particle do requires Tense=Past')]
    return []

  def predictTenseVERB(self):
    return super().predictTenseVERB()

  def predictVerbFormNOUN(self):
    return super().predictVerbFormNOUN()
