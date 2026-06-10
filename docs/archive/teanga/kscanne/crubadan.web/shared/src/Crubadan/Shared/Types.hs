module Crubadan.Shared.Types ( Query
                             , Result
                             , resultID
                             , resultData
                             , Request
                             , requestIndex
                             , requestNum
                             , requestData
                             , Response
                             , responseIndex
                             , responseNum
                             , responseTotal
                             , responseAll
                             , responseData ) where

type Query = [(String, String)]

type Result = (String, [Maybe String])

resultID = fst :: Result -> String
resultData = snd :: Result -> [Maybe String]

type Request = (Int, Int, Query)

requestIndex (i,_,_) = i
requestNum (_,n,_) = n
requestData (_,_,q) = q

type Response = (Int, Int, Int, [Result])

responseIndex (i,_,_,_) = i
responseNum (_,_,_,rs) = length rs
responseTotal (_,t,_,_) = t -- the total number of results
responseData (_,_,_,rs) = rs 
responseAll (_,_,a,_) = a -- the total number of database entries
