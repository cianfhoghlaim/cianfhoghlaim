#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use JSON;
use locale;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my $data;
my $href;
open(DB, "<:utf8", "parsed.json") or die "Could not open parsed.json: $!";
{
local $/ = undef;
$data = <DB>;
close DB;
}
$href = from_json($data);
#die "Problem parsing JSON" if (!defined(eval { $href = from_json($data) }) or !defined($href) or ref($href) ne 'HASH');

sub keycmp {
	(my $a, my $b) = @_;
	(my $la, my $pa) = split(/\|/,$a);
	(my $lb, my $pb) = split(/\|/,$b);
	return $pa cmp $pb if ($la eq $lb);
	return $la cmp $lb;
}

# no AUX, PUNCT, X
my $ud2dict = {'ADJ' => 'a.', 'ADP' => 'prep.', 'ADV' => 'adv.', 'CCONJ' => 'conj.', 'DET' => 'det.', 'INTJ' => 'intj.', 'NOUN' => 'n.', 'NUM' => 'num.', 'PART' => 'part.', 'PRON' => 'pron.', 'PROPN' => 'prop.n.', 'SCONJ' => 'conj.', 'VERB' => 'v.'};
# input is e.g. thootçhey|NOUN
# and output is something human-readable for dict, like
# thootçhey, n.
sub ud2output {
	(my $k) = @_;
	return $ud2dict->{$k};
}

sub examplecmp {
	(my $a, my $b) = @_;
	(my $astarred, my $arest) = $a =~ m/^[^*]*\*([^*]*)\*(.*)$/;
	(my $bstarred, my $brest) = $b =~ m/^[^*]*\*([^*]*)\*(.*)$/;
	return ($arest cmp $brest) if ($astarred eq $bstarred);
	return ($astarred cmp $bstarred);
}

# words with > 1 POS where I haven't checked them all in 
# parsed.conllu for accuracy...
my $unresolved = {
'er' => 1, 'y' => 1, 'ny' => 1, 'dy' => 1, 'shen' => 1,
'as' => 1, 'shoh' => 1, 'magh' => 1, 'mie' => 1, 'stiagh' => 1, 'ooilley' => 1,
'cheilley' => 1, 'agh' => 1, 'na' => 1, 'cha' => 1, 'sheese' => 1,
'nagh' => 1, 'cre' => 1, 'chied' => 1, 'ersooyl' => 1, 'feed' => 1,
'myr' => 1, 'son' => 1,
};
# first batch:
# simple pronouns since these would contain pronomials as examples, confusingly
# (mee, eh, and ad already handled by frequency, but include all the same)
# second batch:
# prepositions not disambiugated from pronomials, lesh, jeh, etc.
# third batch:
# other stopwords not adding a lot of value (high freq)
my $alsoskip = {
'ad|PRON' => 1, 'adsyn|PRON' => 1, 'ee|PRON' => 1, 'ish|PRON' => 1, 'eh|PRON' => 1, 'eshyn|PRON' => 1, 'mayd|PRON' => 1, 'mee|PRON' => 1, 'mish|PRON' => 1, 'oo|PRON' => 1, 'uss|PRON' => 1, 'shin|PRON' => 1, 'shinyn|PRON' => 1, 'shiu|PRON' => 1, 'shiuish|PRON' => 1,
'jeh|ADP' => 1, 'lesh|ADP' => 1, 'rish|ADP' => 1, 'ass|ADP' => 1, 'fo|ADP' => 1, 'roish|ADP' => 1, 'voish|ADP' => 1, 'ry|ADP' => 1, 'veih|ADP' => 1,
'e|DET' => 1, 'my|DET' => 1, 'dty|DET' => 1, 've|NOUN' => 1, 'nyn|DET' => 1,
};

sub normalize_letter {
	(my $lemma) = @_;
	$lemma = uc($lemma);
	(my $first) = $lemma =~ m/^(.)/;
	$first = 'C' if ($first =~ m/^[Çç]$/);
	return $first;
}

my $currletter='';
for my $k (sort { keycmp($a,$b) } keys %$href) {
	(my $lemma, my $pos) = split(/\|/,$k);
	# First, kill most frequent words for space reasons....
	# bee|VERB, yn|DET, eh|PRON, er|ADP, mee|PRON, ec|ADP, ny|DET,
	# ayns|ADP, dy|ADP, cha|PART, da|ADP, ad|PRON
	my $freq = scalar(@{$href->{$k}});
	next if ($freq > 1000);
	next if ($pos =~ m/^(AUX|PUNCT|X)$/);
	next if (exists($unresolved->{$lemma}));
	next if (exists($alsoskip->{$k}));
	# print "$k\t$freq\n"; next;
	if (normalize_letter($lemma) ne $currletter) {
		$currletter = normalize_letter($lemma);
		print '\chapter*{'.$currletter."}\n";
		print '\addcontentsline{toc}{chapter}{'.$currletter."}\n";
	}
	print '\begin{longtable}{p{5cm}p{5cm}p{5cm}}'."\n";
	print '\caption*{\textbf{\large '.$lemma.', '.ud2output($pos).'}}\\\\'."\n";
	my $aref = $href->{$k};
	for my $entry (sort {examplecmp($a,$b)} @$aref) {
		$entry =~ s/\*([^*]*)\*/\\textbf{$1}/g;
		$entry =~ s/\|/ & /g;
		$entry =~ s/$/ \\\\/;
		print "$entry\n";
	}
	print '\end{longtable}'."\n\n";
}

exit 0;
