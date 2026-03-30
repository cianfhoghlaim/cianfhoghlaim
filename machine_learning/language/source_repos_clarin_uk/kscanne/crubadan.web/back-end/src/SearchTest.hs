import Options.Applicative

import Crubadan.Search (genResponse)
import Crubadan.FileIO (readDatabase)
import qualified Crubadan.Types as C
import qualified Crubadan.Shared.Types as CS

data Ops = Ops { dbpath :: String
               , queryStr :: String }

getOps :: Parser Ops
getOps = Ops
  <$> strOption
          ( long "path"
         <> metavar "DBPATH"
         <> help "The path to the database directory")
  <*> strOption
          ( long "search"
         <> metavar "SEARCH"
         <> help "The string to test a search with")

main = do ops <- execParser (info (helper <*> getOps)
                                   ( fullDesc
                                  <> progDesc "Search for SEARCH"
                                  <> header "web-back-test - it's a test...")) 
          db <- readDatabase ["name_english", "lang"] (dbpath ops)
          print (genResponse (0,50,[("name_english", queryStr ops)]) db)
          putStrLn ""
          putStrLn "-- Full Database --"
          putStrLn ""
          print db
