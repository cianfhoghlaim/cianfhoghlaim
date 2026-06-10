
test:
	cat liosta.tsv | cut -f 2 > correct.txt
	cat liosta.tsv | cut -f 3 | python3 grc2ga.py | diff -u correct.txt -
