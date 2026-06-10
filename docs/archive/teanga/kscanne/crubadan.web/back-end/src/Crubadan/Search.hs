module Crubadan.Search ( genResponse ) where

import Text.Regex(Regex, mkRegex, matchRegex)
import Data.Maybe(isJust)
import qualified Data.Map as M
import Data.Char (toLower)
import qualified Crubadan.Types as C
import qualified Crubadan.Shared.Types as CS

genResponse :: CS.Request -> C.Database -> CS.Response
genResponse r d = let results = genResults (CS.requestData r) d
                      index = CS.requestIndex r
                      trim = cull (index) (CS.requestNum r)
                      dsize = length d
                      rsize = length results
                  in (index, rsize, dsize, trim results)

cull :: Int -> Int -> [a] -> [a]
cull 0 s ls = take s ls
cull i s (_:ls) = cull (i - 1) s ls
cull _ _ _ = []

genResults :: CS.Query -> C.Database -> [CS.Result]
genResults q = let trans (key,val) = ( key, (mayRegex val) )
               in crunch q . filter (matches (fmap trans q)) 


{- This adding-a-space is so that the first word of the field becomes
   a space-started word just like the rest, so that the match can be
   made uniformly over strings starting with a space. it doesn't appear
   in the visible results in any way
   
   kind of a hack, but it works? -}
fixQ s = let n = fmap toLower s
         in " " ++ n

mayRegex "" = Nothing
mayRegex s = Just (mkRegex (fixQ s))

matches :: [(String, Maybe Regex)] -> C.WS -> Bool
matches r ws = (and . fmap isJust . fmap (matchAttr ws)) r

matchAttr :: C.WS -> (String, Maybe Regex) -> Maybe [String]
matchAttr ws (s, Nothing) = Just ["pass"]
matchAttr ws (s,(Just r)) = -- space added here \/ linked with comment above
  M.lookup s (C.wsData ws) >>= matchRegex r . (" " ++) . fmap toLower . C.wsaMatch

crunch :: CS.Query -> [C.WS] -> [CS.Result]
crunch q = foldr (\w -> (:) (C.wsUID w, pullVals q w)) []

pullVals :: CS.Query -> C.WS -> [Maybe String]
pullVals q w = 
  let fetch k = (:) (M.lookup k (C.wsData w) 
                     >>= \a -> return (C.wsaFace a))
  in foldr fetch [] (fmap fst q)
