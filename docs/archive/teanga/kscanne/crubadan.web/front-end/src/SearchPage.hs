import Control.Applicative
import Reactive.Banana
import Reactive.Banana.Frameworks

import Crubadan.Front.JS
import Crubadan.Front.Types
import Crubadan.Front.Net
import Crubadan.Shared.Types


{- ** FRONT-END CONFIGURATION ** 
   
   cgiURL : the target url for back-end cgi requests
   
   wsURL : the directory for landing-page urls

   mkFields : the list of fields (in order) which are
              to be displayed for the user in the
              search table
   
   resultsPerPage : the number of results that show at
                    one time on-screen (this might be
                    something that the user should be
                    able to change, but it doesn't seem
                    worth it to make that work at the
                    moment..
   -}

cgiURL url = url ++ "/cgi/" -- extension for cgi queries
wsURL url = url ++ "/ws/" -- extension for links to landing-pages

{- Fields are a three-tuple of
     
     face : the label the column has in the search table
     
     key : the key from the EOLAS files that the column 
           corresponds to

     display : the function used to display field values
               (plain unless the value needs to be a
                click-able link in the table or something)
   -}
mkFields :: String -> [Field]
mkFields domain = 
  
  [ ( "Name (English)", "name_english", (withLink (wsURL u) ".html") )
  , ( "BCP-47 Code",    "lang",         plain                        ) 
  , ( "ISO 639-3 Code", "ISO_639-3",    plain                        ) 
  , ( "Country",        "country",      plain                        )
  ]

  where u = reqURL domain

resultsPerPage = 20 :: Int

{- ** END OF FRONT-END CONFIGURATION ** -}


reqURL domain = "http://" ++ domain

main = do domain <- cgiDomain
          putStrLn domain
          let fields = mkFields domain
          
          cullLoadingDiv
          initSearchTable fields
          
          (s,p,n,r) <- getAddHandlers 
          attachHandlers fields (fire s, fire p, fire n)
          network <- compile (mkNetwork domain 
                                        (fire r)
                                        ( addHandler s
                                        , addHandler p
                                        , addHandler n
                                        , addHandler r ))


          -- start listening for key-ups and responses to update
          actuate network
          
          -- then spawn an empty query to fill the table to start
          initQuery <- readSearchTable fields
          handleRq domain (fire r) (0, resultsPerPage, initQuery) 

getAddHandlers = do searchTable <- newAddHandler
                    prevButton <- newAddHandler
                    nextButton <- newAddHandler
                    responses <- newAddHandler
                    return ( searchTable
                           , prevButton
                           , nextButton
                           , responses )

addHandler = fst
fire       = snd

mkNetwork domain sneaky (s,p,n,r) = 
  do eQueries <- fromAddHandler s
     ePrevious <- fromAddHandler p
     eNext <- fromAddHandler n
     eResponses <- fromAddHandler r 
     
     let ePages = countPages <$> eResponses
         
         bPages = stepper 1 ePages
         countPages (Just r) = ((responseTotal r) 
                                `div` resultsPerPage) + 1
         countPages _ = 1
         bRangeLim = (\a f -> 
                        mayDo f (\x -> 
                                   (x >= 1) && (x <= a))) 
                     <$> bPages

         eQU = fmap (\_ -> setOne) eQueries 
         ePU = fmap (\_ -> minusOne) ePrevious 
         eNU = fmap (\_ -> plusOne) eNext
         
         eUpdaters = eQU `union` ePU `union` eNU 
         bCurrentPage = accumB 1 (bRangeLim <@> eUpdaters)

         bReqIndex = fmap (\p -> resultsPerPage * (p - 1)) bCurrentPage
         bReqNum = pure resultsPerPage
         bReqQuery = stepper (emptyQ (mkFields domain)) eQueries
         bRequest = (\a b c -> (a,b,c)) 
                    <$> bReqIndex 
                    <*> bReqNum 
                    <*> bReqQuery

         sendRq = handleRq domain sneaky
     
     cRq <- changes bRequest
     -- \/ react on changes to the search request that would be sent
     reactimate' (fmap sendRq <$> (cRq))
     -- \/ react on new responses recieved
     reactimate (fmap (showResults (mkFields domain)) eResponses)

emptyQ :: [Field] -> Query
emptyQ = foldr (\f qs -> (fieldKey f, ""):qs) []

setOne :: Int -> Int
setOne _ = 1
minusOne :: Int -> Int
minusOne a = a - 1
plusOne :: Int -> Int
plusOne a = a + 1

mayDo :: (a -> a) -> (a -> Bool) -> (a -> a)
mayDo fun test x = if test (fun x)
                      then fun x
                      else x

handleRq :: String -> Handler (Maybe Response) -> Request -> IO ()
handleRq domain fire rq = 
  print rq >> netget (cgiURL (reqURL domain)) rq >>= fire

showResults :: [Field] -> Maybe Response -> IO ()
showResults fields r = print r >> writeResponse fields r
