module Crubadan.Front.Types ( Field
                            , fieldTitle
                            , fieldKey
                            , fieldDisplay
                            , DisplayFun
                            , plain
                            , withLink ) where

import Crubadan.Shared.Types

type Field = (String, String, DisplayFun)

fieldTitle :: Field -> String
fieldTitle (t,_,_) = t

fieldKey :: Field -> String
fieldKey (_,k,_) = k

fieldDisplay :: Field -> DisplayFun
fieldDisplay (_,_,f) = f

type DisplayFun = Result -> Maybe String -> String

plain :: DisplayFun
plain _ (Just s) = s
plain _ _ = "N/A"

withLink :: String -> String -> DisplayFun
withLink url extension r mayS = 
  "<a href=\"" ++ url ++ (resultID r) ++ extension ++ "\">" 
  ++ (plain r mayS) 
  ++ "</a>"
