#!/bin/bash
# only non-recursive links (so one pass through this won't catch
# an [[Íomhá:...]] where the caption contains links)
# But I run the text through this twice to catch depth one cases!
# See makefile
sed 's/\[\[\([^|\[]*\)\]\]/\1/g' | sed 's/\[\[[^\[]*|\([^|\[]*\)\]\]/\1/g' | sed 's/\[http[^ \[]* /[/g' | sed 's/\[http[^ \[]*\]/ /g'
