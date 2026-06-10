module Crubadan.Types ( Database
                      , WS (..)
                      , Attribute (..) 
                      , engName ) where

import qualified Data.Map as M

type Database = [WS]

data WS = WS { wsUID :: String
             , wsData :: M.Map String Attribute
             } deriving (Read, Show, Eq)

data Attribute = Attribute { wsaFace :: String
                           , wsaMatch :: String
                           } deriving (Read, Show, Eq)

engName :: WS -> String
engName ws = case M.lookup "name_english" (wsData ws) of
               Just att -> wsaFace att
               _ -> "error: no English name?"
