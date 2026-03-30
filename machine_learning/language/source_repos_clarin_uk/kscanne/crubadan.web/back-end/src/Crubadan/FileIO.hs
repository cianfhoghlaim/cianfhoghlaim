module Crubadan.FileIO ( readDatabase ) where

import System.Directory (getDirectoryContents)
import qualified Text.ParserCombinators.Parsec as P
import qualified Data.Map as M
import qualified Data.List as L

import qualified Crubadan.Types as C

recordFilename = "EOLAS"

readDatabase :: [String] -> String -> IO C.Database
readDatabase keys = fmap (sortEntries . processEntries keys) . entries

sortEntries :: C.Database -> C.Database
sortEntries = L.sortBy (\a b -> compare (C.engName a) (C.engName b))

entries :: String -> IO [String]
--entries path = getNames path >>= foldr entryAppend (return [])
entries path = do names <- getNames path
                  print names
                  foldr entryAppend (return []) names

getNames :: String -> IO [String]
getNames path = ( fmap (fmap (qualifyName path))
                . fmap (L.delete "." . L.delete "..") 
                . getDirectoryContents
                ) path

qualifyName :: String -> String -> String
qualifyName path name = path ++ "/" ++ name ++ "/" ++ recordFilename

entryAppend :: String -> IO [String] -> IO [String]
entryAppend name ss = 
  do content <- readFile name
     putStrLn content
     others <- ss
     return (content : others)

processEntries :: [String] -> [String] -> C.Database
processEntries keys = foldr p []
  where p f ss = case P.parse (wsFile keys) "(unknown)" f of
                   Left _ -> ss
                   Right w -> w : ss

wsFile :: [String] -> P.GenParser Char st C.WS
wsFile ks = 
  do name <- wsName
     P.char '\n'
     rs <- wsRecords ks
     return (C.WS name 
                  (M.fromList (("lang", C.Attribute name name) : rs)))

wsName = P.string "lang " >> P.many (P.noneOf "\n")

wsRecords ks = do record <- wsRecord
                  more <- moreRecords ks
                  return (if (elem (fst record) ks)
                             then record : more 
                             else more)

wsRecord = do key <- P.many (P.noneOf " ")
              P.char ' '
              val <- P.many (P.noneOf "\n")
              return ( key, C.Attribute val val )

moreRecords ks = P.char '\n' >> ((P.eof >> return []) P.<|> wsRecords ks)
