{-# LANGUAGE CPP, ForeignFunctionInterface, JavaScriptFFI #-}

module Crubadan.Front.Net ( netget, cgiDomain ) where

import GHCJS.Foreign (FromJSString (..))
import GHCJS.Types (JSString)

import Data.Maybe (fromJust)
import Data.Default (def)
import JavaScript.JQuery (ajax, arData)

import qualified Data.Text as T (pack, unpack, Text)

import qualified Crubadan.Shared.Types as CS

url = T.pack "http://localhost/cgi/"   --"http://octalsrc.net/cgi/"

query q = [(T.pack "query", T.pack (show q))]

netget :: String -> CS.Request -> IO (Maybe CS.Response)
netget url r = 
  do ar <- ajax (T.pack url) (query r) def
     return . fmap (fromJust . read . T.unpack) . arData $ ar

cgiDomain :: IO String
cgiDomain = fmap fromJSString ffiGetHostname

foreign import javascript safe "$r = window.location.hostname;"
   ffiGetHostname :: IO JSString
