#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use JSON;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %addenda;
my $eng;
open(ADDENDA, "<:utf8", "addenda.txt") or die "Could not open addenda.txt: $!";
while (<ADDENDA>) {
	chomp;
	if (m/^<div text="(.+)"\/>$/) {
		$eng = $1;
	}
	elsif (m/^([A-Za-zÁÉÍÓÚáéíóú'].+[.?!])$/) {
		$addenda{$eng} = $1;
	}
	elsif (/^$/) {
		1;
	}
	else {
		print STDERR "Problem on line $.\n";
	}
}
close ADDENDA;

# pronm => X ensures that aym, assdoo, etc. won't be headwords
# even if not yet correctly decomposed in the conllu file
my $posmap = {'nm' => 'NOUN', 'nf' => 'NOUN', 'a' => 'ADJ', 'adv' => 'ADV', 'v' => 'VERB', 'n' => 'NOUN', 'pronm' => 'X', 'prep' => 'ADP', 'conj' => 'CONJ', 'interr' => 'PRON', 'card' => 'NUM', 'pn' => 'PRON', 'excl' => 'INTJ', 'poss' => 'DET', 'aindec' => 'ADJ', 'art' => 'DET', 'u' => 'PART', 'ord' => 'NUM'};
# aachoorsal_nm -> aachoorsal|NOUN
sub focloir2ud {
	(my $k) = @_;
	(my $w, my $p) = split(/_/,$k);
	$w =~ s/[0-9]+$//;
	my $udpos = 'UNK';
	$udpos = $posmap->{$p} if (exists($posmap->{$p}));
	$udpos = 'PROPN' if ($udpos eq 'NOUN' and $w =~ m/^[A-ZÇ]/);
	return "$w|$udpos";
}

my %altmap;
open(FOC, "<:utf8", "/home/kps/gaeilge/ga2gv/ga2gv/focloir.txt") or die "Could not open focloir.txt: $!";
while (<FOC>) {
	chomp;
	my @fields = split(/\t/,$_);
	my $udalt = focloir2ud($fields[0]);
	my $udnorm = $udalt;
	$udnorm = focloir2ud($fields[3]) if ($fields[3] ne '0');
	# don't redirect to another headword if this lemma already is one
	# e.g. boggey is "áthas" but also an alt vn boggaghey....
	# we don't want that redirect by default
	$altmap{$udalt} = $udnorm unless (exists($altmap{$udalt}));
}
close FOC;
# in a few cases, stuff in usage file is *always* the alt spelling
$altmap{'lhieggey|NOUN'} = 'lhieggal|NOUN';
$altmap{'lhoo|NOUN'} = 'loo|NOUN';
$altmap{'pobbyl|NOUN'} = 'pobble|NOUN';
$altmap{'shiauill|VERB'} = 'shiaull|VERB';
# cases where it's always the headword spelling, but thrown off
# because of a gender difference:
$altmap{'insh|NOUN'} = 'insh|NOUN';
$altmap{'key|NOUN'} = 'key|NOUN';
$altmap{'shalmane|NOUN'} = 'shalmane|NOUN';

my %result;
my %seen;
sub add_to_json {
	(my $lemma_href, my $gaelg, my $gaeilge, my $bearla) = @_;
	my $pair = "$gaelg|$gaeilge";
	unless (exists($seen{$pair})) {
		if (exists($addenda{$bearla}) and $gaeilge ne $addenda{$bearla}) {
			$gaeilge .= " (“$addenda{$bearla}”)";
		}
		for my $k (keys %{$lemma_href}) {
			next unless (exists($altmap{$k}));
			push @{$result{$altmap{$k}}}, $lemma_href->{$k}."|$gaeilge|$bearla";
		}
	}
	$seen{$pair}=1;
}

my %lemma2sent=();
my %mwpiece=();
my $gv='';
my $ga='';
my $en='';
my $cleangv='';
my $mwt_remaining = 0;
my $surface='';
my $spaceafter_p='';
while (<STDIN>) {
	chomp;
	if (m/^# newpar/) {
		if ($cleangv ne $gv) {
			print STDERR "QA Check: text field doesn't match detokenized sentence:\n$cleangv\n$gv\n";
		}
		add_to_json(\%lemma2sent,$gv,$ga,$en);
		%lemma2sent=();
		$cleangv = ''; 
		$gv=''; # read from 'text =' comment; no longer used
		$ga=''; # read from 'text_ga =' comment
		$en=''; # read from 'text_en =' comment
	}
	elsif (m/^# text = (.+)$/) {
		$gv .= ' ' if $gv;
		$gv .= $1;
	}
	elsif (m/^# text_ga = (.+)$/) {
		$ga .= ' ' if $ga;
		$ga .= $1;
	}
	elsif (m/^# text_en = (.+)$/) {
		$en .= ' ' if $en;
		$en .= $1;
	}
	elsif (m/^([0-9]+)-([0-9]+)\t/) {   # start of MWT
		$mwt_remaining = $2 - $1 + 1;
		my @pieces = split(/\t/);
		$surface = $pieces[1];
		$spaceafter_p = ($pieces[9] eq '_');
		%mwpiece=();
	}
	elsif (m/^[0-9]+\t/) {
		my @pieces = split(/\t/);
		my $key = "$pieces[2]|$pieces[3]";
		if ($mwt_remaining>0) {
			$mwt_remaining--;
			$mwpiece{$key} = 1;
		}
		else {
			$surface = $pieces[1];
			$spaceafter_p = ($pieces[9] eq '_');
		}
		$lemma2sent{$key} = $cleangv unless (exists($lemma2sent{$key}));
		if ($mwt_remaining==0) {
			for my $k (keys %lemma2sent) {
				if ($k eq $key or exists($mwpiece{$k})) {
					$lemma2sent{$k} .= "*${surface}*";
				}
				else {
					$lemma2sent{$k} .= $surface;
				}
				$lemma2sent{$k} .= ' ' if $spaceafter_p;
			}
			$cleangv .= $surface;
			$cleangv .= ' ' if $spaceafter_p;
			%mwpiece=();
		}
	}
	else {   # skip all comments other than above, blanks, and multiword tokens
		1;
	}
}
add_to_json(\%lemma2sent,$gv,$ga,$en);

print to_json(\%result, { pretty => 1 });

exit 0;
