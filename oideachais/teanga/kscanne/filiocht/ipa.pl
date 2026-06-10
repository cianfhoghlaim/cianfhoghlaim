#!/usr/bin/perl
# takes plain text in Irish on standard input and outputs
# a phonetic transcription; designed to be piped into filiocht.pl
#
# TODO: last resort transcriptions: look up in English CMU dictionary,
# use Caighdeánaitheoir spelling rules, or just implement default 
# grapheme to phoneme rules

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

if ($#ARGV != 0) {
	die "Usage: $0 FP.txt\n";
}
my $ipafile = $ARGV[0];

my %ipa;
my @prefixes;
my @suffixes;
my $prefixrule;
my $suffixrule;
my $total=0;
my $found=0;

open(DICT, "<:utf8", $ipafile) or die "Could not open FP.txt: $!";
while (<DICT>) {
	chomp;
	(my $w, my $p) = m/^([^\t]+)\t([^\t]+)$/;
	$ipa{$w} = $p;
}
close DICT;

open(PREF, "<:utf8", 'reimir.csv') or die "Could not open reimir.csv: $!";
while (<PREF>) {
	chomp;
	next if (/^#/);
	my @r = split(/,/);
	push @prefixes, \@r;
}
close PREF;

open(SUFF, "<:utf8", 'iarmhir.csv') or die "Could not open iarmhir.csv: $!";
while (<SUFF>) {
	chomp;
	next if (/^#/);
	my @r = split(/,/);
	push @suffixes, \@r;
}
close SUFF;

sub strip_prefixes {
	(my $t) = @_;
	for my $rule (@prefixes) {
		my $tomatch = $rule->[1];
		if ($t =~ m/^$tomatch/) {
			my $repl = $rule->[0];
			$t =~ s/^$tomatch/$repl/;
			$prefixrule = $rule;
			return $t;
		}
	}
	return $t;
}

# unlike prefixes fn above, only return modified word if it's in the ipa hash
sub strip_suffixes {
	(my $t) = @_;
	for my $rule (@suffixes) {
		my $tomatch = $rule->[1];
		if ($t =~ m/$tomatch$/) {
			my $repl = $rule->[0];
			my $ans = $t;
			$ans =~ s/$tomatch$/$repl/;
			if (exists($ipa{$ans}) and $ipa{$ans} =~ m/$rule->[2]$/) {
				$suffixrule = $rule;
				return $ans;
			}
		}
	}
	return $t;
}

sub apply_ipa_rules {
	(my $ipa) = @_;
	if (defined($prefixrule)) {
		my $tomatch = $prefixrule->[2];
		my $repl = $prefixrule->[3];
		$repl = '' if ($repl eq '0');
		$ipa =~ s/^$tomatch/$repl/;
	}
	if (defined($suffixrule)) {
		my $tomatch = $suffixrule->[2];
		my $repl = $suffixrule->[3];
		$repl = '' if ($repl eq '0');
		$ipa =~ s/$tomatch$/$repl/;
	}
	return $ipa;
}

sub toipa {
	(my $t) = @_;
	my $orig = $t;
	my $ans = '';
	if (exists($ipa{$t})) {
		$ans = $ipa{$t};
		$found++;
	}
	else {
		$prefixrule = undef;
		$suffixrule = undef;
		$t = strip_prefixes($t);
		if (exists($ipa{$t})) {
			$ans = apply_ipa_rules($ipa{$t});
			$found++;
		}
		else {
			$t = strip_suffixes($t);
			if (exists($ipa{$t})) {
				$ans = apply_ipa_rules($ipa{$t});
				$found++;
			}
			else {
				$ans = "<$orig>";
				#$ans = "NO: $t (orig = $orig)";
			}
		}
	}
	return $ans;
}

# argument is a non-negative int ([0-9]+)
sub numtoipa {
	(my $t, my $with_object_p) = @_;
	my $ans = '';
	my $milte = int($t/1000);
	if ($milte > 0) {
		my $word = 'míle';
		$word = 'mhíle' if ($milte % 10 < 7);
		$ans .= numtoipa($milte,1)."\n" if ($milte > 1);
		$ans .= toipa($word);
	}
	$t = $t % 1000;
	my $ceadta = int($t/100);
	if ($ceadta > 0) {
		$ans .= "\n" if ($ans ne '');
		my $word = 'gcéad';
		$word = 'chéad' if ($ceadta % 10 < 7);
		$word = 'céad' if ($ceadta % 10 == 1);
		$ans .= numtoipa($ceadta,1)."\n" if ($ceadta > 1);
		$ans .= toipa($word);
	}
	$t = $t % 100;
	my $deicheanna = int($t/10);
	if ($deicheanna > 1) {
		$ans .= "\n" if ($ans ne '');
		my @w1 = ('','','fiche','tríocha','daichead','caoga','seasca','seachtó','ochtó','nócha');
		$ans .= toipa($w1[$deicheanna]);
	}
	$t = $t % 10;
	my @w2 = ('','haon','dó','trí','ceathair','cúig','sé','seacht','hocht','naoi','deich');
	my @w3 = ('','','dhá','trí','ceithre','cúig','sé','seacht','ocht','naoi','deich');
	if ($t == 0 and $deicheanna == 1) {
		$t = 10;
		$deicheanna = 0;
	}
	if ($t > 0) {
		$ans .= "\n" if ($ans ne '');
		if ($with_object_p) {
			$ans .= toipa($w3[$t]);
		}
		else {
			$ans .= toipa('a')."\n".toipa($w2[$t]);
		}
		if ($deicheanna==1) {
			my $word = 'déag';
			$word = 'dhéag' if ($t == 2);
			$ans .= "\n".toipa('déag')
		}
	}
	return $ans;
}

sub caighdeanu {
	(my $t) = @_;
	$t =~ s/ḃ/bh/g;
	$t =~ s/ċ/ch/g;
	$t =~ s/ḋ/dh/g;
	$t =~ s/ḟ/fh/g;
	$t =~ s/ġ/gh/g;
	$t =~ s/ṁ/mh/g;
	$t =~ s/ṗ/ph/g;
	$t =~ s/ṡ/sh/g;
	$t =~ s/ṫ/th/g;
	return $t;
}


while (<STDIN>) {
	chomp;
	s/https?:[^ ]+//g;
	#s/[A-Za-zÁÉÍÓÚáéíóú0-9.-]+\.(com|ie|uk|org)(\P{L})/$2/g;
	#s/ *@[A-Za-z0-9_]+//g;
	s/^RT @[A-Za-z0-9_]+: //;
	s/^(@[A-Za-z0-9_]+ )+//;
	s/([^0-9])([<:]3)+/$1/g;
	s/^ *//g;
	s/  */ /g;
	my $orig = $_;
	while (m/((\p{L}|[0-9’'-])+)/g) {
		my $t = $1;
		$t =~ s/[’'-]+$//;
		next if ($t eq '');
		$t =~ s/’/'/g;
		$t =~ s/^([nt])([AEIOUÁÉÍÓÚ])/$1-$2/;
		$t = lc($t);
		$t = caighdeanu($t);
		$total++;
		if ($t =~ m/^[0-9]+$/) {
			$found++;
			print numtoipa($t,0)."\n";
		}
		else {
			print toipa($t)."\n";
		}
	}
	print "<BRISEADH>$orig\n";
}

my $ans = $found / (1.0*$total);
print "Found: $ans\n";

exit 0;
