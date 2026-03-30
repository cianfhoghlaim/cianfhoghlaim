read lexc nish.txt
define Lexicon;
define DisallowIntermediateTags ~[$[ "+NAPl" | "+NIPl" | "+NASg" | "+NISg" | "+Poss" | "+Imp" ]];
define DisallowFakePrefixes ~[$[ "2P+" "Ex+" | "2P+" "Obv+" | "1P+" "Obv+" ]];
define DisallowMultipleObjects ~[$[ [ "+Indep" | "+Conj" ] ? ? ? ? ? ]];
define AnimatePlural [ "+Pl" -> "+NAPl" || "+NA" ?* _ .#. ];
define InanimatePlural [ "+Pl" -> "+NIPl" || "+NI" ?* _ .#. ];
define AnimateSingular [ "+Sg" -> "+NASg" || "+NA" ?* _ .#. ];
define InanimateSingular [ "+Sg" -> "+NISg" || "+NI" ?* _ .#. ];
define InsertPossSg [  "+Sg" -> "+Poss" "+Sg" || "Poss+" ?+ _ .#. ];
define InsertPossPl [  "+Pl" -> "+Poss" "+Pl" || "Poss+" ?+ _ .#. ];
define InsertPossObv [  "+Obv" -> "+Poss" "+Obv" || "Poss+" ?+ _ .#. ];
define InsertPossLoc [  "+Loc" -> "+Poss" "+Loc" || "Poss+" ?+ _ .#. ]; ! locatives can be possessed too; see V p.205
define 1sPossessum [ "+Poss" -> "+1P" "+Sg" "+Poss" || .#. "1P+" "Sg+" "Poss+" ?+ _ ? .#. ]; 
define 2sPossessum [ "+Poss" -> "+2P" "+Sg" "+Poss" || .#. "2P+" "Sg+" "Poss+" ?+ _ ? .#. ]; 
define 3sPossessum [ "+Poss" -> "+3P" "+Sg" "+Poss" || .#. "3P+" "Sg+" "Poss+" ?+ _ ? .#. ]; 
define 1pPossessum [ "+Poss" -> "+1P" "+Ex" "+Poss" || .#. "1P+" "Ex+" "Poss+" ?+ _ ? .#. ]; 
define 21Possessum [ "+Poss" -> "+1P" "+Pl" "+Poss" || .#. "1P+" "Pl+" "Poss+" ?+ _ ? .#. ]; 
define 2pPossessum [ "+Poss" -> "+2P" "+Pl" "+Poss" || .#. "2P+" "Pl+" "Poss+" ?+ _ ? .#. ]; 
define 3pPossessum [ "+Poss" -> "+3P" "+Pl" "+Poss" || .#. "3P+" "Pl+" "Poss+" ?+ _ ? .#. ]; 
define 1sActorIndep [ "+Indep" -> "+Indep" "+1P" "+Sg" || .#. "1P+" "Sg+" ?+ _ ]; 
define 2sActorIndep [ "+Indep" -> "+Indep" "+2P" "+Sg" || .#. "2P+" "Sg+" ?+ _ ]; 
define 3sActorIndep [ "+Indep" -> "+Indep" "+3P" "+Sg" || .#. "3P+" "Sg+" ?+ _ ]; 
define 3oActorIndep [ "+Indep" -> "+Indep" "+3P" "+Obv" || .#. "3P+" "Obv+" \"Pl+" ?+ _ ]; 
define 3opActorIndep [ "+Indep" -> "+Indep" "+3P" "+Obv" "+Pl" || .#. "3P+" "Obv+" "Pl+" ?+ _ ]; 
define 1pActorIndep [ "+Indep" -> "+Indep" "+1P" "+Ex" || .#. "1P+" "Ex+" ?+ _ ]; 
define 21ActorIndep [ "+Indep" -> "+Indep" "+1P" "+Pl" || .#. "1P+" "Pl+" ?+ _ ]; 
define 2pActorIndep [ "+Indep" -> "+Indep" "+2P" "+Pl" || .#. "2P+" "Pl+" ?+ _ ]; 
define 3pActorIndep [ "+Indep" -> "+Indep" "+3P" "+Pl" || .#. "3P+" "Pl+" ?+ _ ]; 
define ImpActorIndep [ "+Indep" -> "+Indep" "+Imp" || .#. "Imp+" ?+ _ ]; 
define NISgActorIndep [ "+Indep" -> "+Indep" "+NI" "+Sg" || .#. "NI+" "Sg+" ?+ _ ]; 
define NIPlActorIndep [ "+Indep" -> "+Indep" "+NI" "+Pl" || .#. "NI+" "Pl+" ?+ _ ]; 
define 1sActorConj [ "+Conj" -> "+Conj" "+1P" "+Sg" || .#. "1P+" "Sg+" ?+ _ ]; 
define 2sActorConj [ "+Conj" -> "+Conj" "+2P" "+Sg" || .#. "2P+" "Sg+" ?+ _ ]; 
define 3sActorConj [ "+Conj" -> "+Conj" "+3P" "+Sg" || .#. "3P+" "Sg+" ?+ _ ]; 
define 3oActorConj [ "+Conj" -> "+Conj" "+3P" "+Obv" || .#. "3P+" "Obv+" ?+ _ ];
define 1pActorConj [ "+Conj" -> "+Conj" "+1P" "+Ex" || .#. "1P+" "Ex+" ?+ _ ]; 
define 21ActorConj [ "+Conj" -> "+Conj" "+1P" "+Pl" || .#. "1P+" "Pl+" ?+ _ ]; 
define 2pActorConj [ "+Conj" -> "+Conj" "+2P" "+Pl" || .#. "2P+" "Pl+" ?+ _ ]; 
define 3pActorConj [ "+Conj" -> "+Conj" "+3P" "+Pl" || .#. "3P+" "Pl+" ?+ _ ]; 
define ImpActorConj [ "+Conj" -> "+Conj" "+Imp" || .#. "Imp+" ?+ _ ]; 
define NISgActorConj [ "+Conj" -> "+Conj" "+NI" "+Sg" || .#. "NI+" "Sg+" ?+ _ ]; 
define NIPlActorConj [ "+Conj" -> "+Conj" "+NI" "+Pl" || .#. "NI+" "Pl+" ?+ _ ]; 
define PropagatePossessum [ 1sPossessum .o. 2sPossessum .o. 3sPossessum .o. 1pPossessum .o. 21Possessum .o. 2pPossessum .o. 3pPossessum ];
define PropagateActorIndep [ 1sActorIndep .o. 2sActorIndep .o. 3sActorIndep .o. 3opActorIndep .o. 3oActorIndep .o. 1pActorIndep .o. 21ActorIndep .o. 2pActorIndep .o. 3pActorIndep .o. ImpActorIndep .o. NISgActorIndep .o. NIPlActorIndep ];
define PropagateActorConj [ 1sActorConj .o. 2sActorConj .o. 3sActorConj .o. 3oActorConj .o. 1pActorConj .o. 21ActorConj .o. 2pActorConj .o. 3pActorConj .o. ImpActorConj .o. NISgActorConj .o. NIPlActorConj ];
define PropagateActor [ PropagateActorIndep .o. PropagateActorConj ];
define NoConjSubjectPrefix [ [ "Imp+" | [ "1P+" | "2P+" | "3P+" | "NI+" ] [ "Sg+" | "Obv+" | "Pl+" | "Ex+" ] ] -> 0 || .#. _ ?+ "+Conj" ];
define ObviativeAnimateOnly ~[$[ "+NI" ?* "+Obv" ]];
! topicality hierarchy for prefixes in VTA
define Promote2PGoal [ [ "1P+" | "3P+" | "NI+" ] -> "2P+" || .#. _ ?+ [ "+Sg" | "+Pl" | "+Obv" | "+Ex" ] [ "+2P" | [ "+1P" "+Pl" ] ] ];
define Promote2PGoalImp [ "Imp+" -> "2P+" "Sg+" || .#. _ ?+ "+Imp" [ "+2P" | [ "+1P" "+Pl" ] ] ];
define Promote1PGoal [ [ "3P+" | "NI+" ] -> "1P+" || .#. _ ?+ [ "+Sg" | "+Obv" ] "+1P" [ "+Sg" | "+Ex" ] ];
define Promote1PGoalPl [ [ "3P+" | "NI+" ] "Pl+" -> "1P+" "Sg+" || .#. _ ?+ "+Pl" "+1P" [ "+Sg" | "+Ex" ] ];
define Promote1PGoalImp [ "Imp+" -> "1P+" "Sg+" || .#. _ ?+ "+Imp" "+1P" [ "+Sg" | "+Ex" ] ];
define Promote3PGoal [ "NI+" -> "3P+" || .#. _ ?+ [ "+Sg" | "+Pl" ] "+3P" [ "+Sg" | "+Pl" | "+Obv" ] ];
define TopicalityHierarchy [ Promote2PGoal .o. Promote2PGoalImp .o. Promote1PGoal .o. Promote1PGoalPl .o. Promote1PGoalImp .o. Promote3PGoal ];
define LongDistanceDependencies [ ObviativeAnimateOnly .o. InsertPossSg .o. InsertPossPl .o. InsertPossObv .o. InsertPossLoc .o. PropagatePossessum .o. PropagateActor .o. TopicalityHierarchy .o. NoConjSubjectPrefix .o. AnimatePlural .o. InanimatePlural .o. AnimateSingular .o. InanimateSingular ];
define PossLinkingD [ "@" -> d || _ [ a | e | i \i ] ];  ! V 4.9.2, but not ii or oo as in 4.9.2.1
define PossLinkingDO [ "@" -> d o || _ o \o ]; ! lengthen initial o (Biigtigong TSV)
define PossLinkingDW [ "@" w a -> d o o || _ \a ]; ! Biigtigong TSV, w + short a only
define PossLinkingDY [ "@" y -> d a y ];
define PossCoalesce [ i "@" -> 0 || _ [ i i | o o ] ];
define PossPrefixRules [ PossLinkingD .o. PossLinkingDO .o. PossLinkingDW .o. PossLinkingDY .o. PossCoalesce ];
define PluralRules [ n h "^" a -> n y a , a "^" a -> a , i i "^" a -> i i , e "^" a -> e , o o "^" a -> o o , W "^" a -> o o ];  ! same rules for Obviative
! V. p. 188 has -gan+dim. = gaans ( g a n "^" e -> g a a ),
! but Biigtigong prefers more regular g(a)nens
define ConOrDimRules [ w a "^" e -> o o , a a "^" e -> a a , i i "^" e -> i i , e "^" e -> e , o o "^" e -> o o , W "^" e -> o o , k "^" w "^" e -> k o o , g "^" w "^" e -> g o o , i w "^" e -> i i , i "^" w "^" e -> i i ];
define ShortAConOrDim [ a "^" e -> e || \a _ ];  ! miikna -> miiknens e.g.
define ClassVFinalI [ i "^" y "^" [ a | e | i ] -> i i ]; 
define ClassVOther [ "^" y "^" [ a | e | i ] -> i i || \i _ ]; 
define ClassVIDropY [ a y -> 0 || _ "^" A "^" i ];
define PejRules [ n s "^" i s -> n z h i s , n h "^" i s -> n y i s , a "^" i s -> a w i s , i i "^" i s -> i i w i s , e "^" i s -> e w i s , o o "^" i s -> o o w i s , W "^" i s -> o s , k "^" w "^" i s -> k o s , g "^" w "^" i s -> g o s , "^" A "^" i s -> a a s ];
define LocRules [ n h "^" i n -> n y i n , w a "^" i n -> o n , a a "^" i n -> a a n , i i "^" i n -> i i n , i w "^" i n g -> i i n g , i "^" w "^" i n g -> i i n g , e "^" i n -> e n , o o "^" i n -> o o n , W "^" i n -> o n , e "^" w "^" i n -> e n , k "^" w "^" i n -> k o n , g "^" w "^" i n -> g o n , "^" A "^" i n -> a a n ];
define ShortALocOrPoss [ a "^" i -> a a || \a _ ];  ! miikna -> miiknaang, miiknaam
define PossThmRules [ n h "^" i m -> n y i m , w a "^" i m -> o m , a a "^" i m -> a a m , i i "^" i m -> i i m , i w "^" i m -> i i m , i "^" w "^" i m -> i i m , e "^" i m -> e m , o o "^" i m -> o o m , W "^" i m -> o m , e "^" w "^" i m -> e m , k "^" w "^" i m -> k o m , g "^" w "^" i m -> g o m , "^" A "^" i m -> a a m ]; ! cf. V. p. 201
define LeniteQuasiDim [ z e n s "^" i s -> z h e n z h i s ];  ! as in kwezens -> kwezhenzhish, gwiiwzens -> gwiiwzhenzhish, V p.193; do this before PejRules
define SingularCleanup [ "^" [ w | W | y ] -> 0 || _ .#. ];
define classVICleanup [ "^" A -> 0 ];
define vai2Changes [ a m "~" [ i | o ] m -> a a m , a m "~" i n -> a a n , a m "~" b a n -> a m o b a n , a m "~" ŵ -> a m o ŵ || \a _ ];
define normalizeNasalToN [ [ m | n ] "~" n -> n || [ a | e | i | o ] _ [ g | z ] ];
define dropFinalDVII [ d "~" -> 0 || _ [ k | s | n z ] ];
define adjustFinalConsonant [ vai2Changes .o. normalizeNasalToN .o. dropFinalDVII ];
define keepFinalLongVowel [ "@" -> 0 || [ a a | i i | o o ] _ .#. ];
define dropFinalShortVowel [ [ a | i | o ] "@" -> 0 || _ .#. ];
define Cleanup [ "~" -> 0, "^" -> 0, "@" -> 0 ];
define Morph [ DisallowIntermediateTags .o. DisallowFakePrefixes .o. DisallowMultipleObjects .o. LongDistanceDependencies .o. Lexicon .o. adjustFinalConsonant .o. keepFinalLongVowel .o. dropFinalShortVowel .o. PossPrefixRules .o. PluralRules .o. ClassVFinalI .o. ClassVOther .o. ConOrDimRules .o. ShortAConOrDim .o. LeniteQuasiDim .o. ClassVIDropY .o. PejRules .o. LocRules .o. PossThmRules .o. ShortALocOrPoss .o. classVICleanup .o. SingularCleanup .o. Cleanup .o. @"syncopate.bin" ];
push Morph
save stack nish.bin
