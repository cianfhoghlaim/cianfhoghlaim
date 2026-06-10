import Network.CGI( CGI, CGIResult, setHeader, readInput, output, getInputs)
import Network.FastCGI( runFastCGI )
import Control.Applicative

import qualified Crubadan.Search as S
import qualified Crubadan.Types as C
import qualified Crubadan.FileIO as F


{- It's worth noting that the "lang" key cannot be ignored, as
   it forms the UID of each language, and thus does not need to
   be listed here. -}
desiredKeys = ["name_english", "ISO_639-3", "country"]


cgiMain :: C.Database -> CGI CGIResult
cgiMain d = 
  do setHeader "Content-type" "text/plain"
     request <- readInput "query"
     output $ show $ S.genResponse <$> request <*> (pure d)

main :: IO ()
main = do d <- F.readDatabase 
                 desiredKeys
                 "/data/crubadan"
          runFastCGI $ cgiMain d 
