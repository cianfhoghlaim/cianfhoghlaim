#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use locale;
use JSON;
use Storable;
use List::Util qw(shuffle);
use Date::Parse;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

# arg and return val are in YYYY-MM-DD format
sub increment_date {
	(my $s) = @_;
	my @t = (gmtime(str2time($s,'GMT') + 24*60*60))[5,4,3];
	$t[0] += 1900;
	$t[1] += 1;
	return sprintf("%04d-%02d-%02d", @t);
}

# not used currently
sub toponcanna {
    (my $w) = @_;
    for ($w) {
        s/bh/ḃ/g;
        s/ch/ċ/g;
        s/dh/ḋ/g;
        s/fh/ḟ/g;
        s/gh/ġ/g;
        s/mh/ṁ/g;
        s/ph/ṗ/g;
        s/sh/ṡ/g;
        s/th/ṫ/g;
    }
    return $w;
}

my %words;
my %puzzles;

if ($#ARGV != 0) {
	die "Usage: $0 langcode";
}
my $teanga = $ARGV[0];

open(WORDLIST, "<:utf8", "words-$teanga.txt") or die "Could not open words-$teanga.txt: $!";
while (<WORDLIST>) {
	chomp;
	my $word = $_;
	next if (length($word)<4);
	next if ($word =~ m/(\p{Lu}|\p{S}|\p{N}|\p{P})/); # no caps, punct in words
	#$word = toponcanna($word); 
	my %uniq;
	for my $letter (split(//,$word)) {
		$uniq{$letter} = 1;
	}
	my $letters = join('',sort keys %uniq);
	$puzzles{$letters}->{$word} = 1 if (length($letters)==7);
	$words{$word} = $letters if (length($letters)<=7);
}
close WORDLIST;

#my $minscore=0;
#my $mincount=0;
# for Irish (headwords only), (50,8) gives 4808 puzzles
# for Irish (headwords only), (75,15) gives 4421 puzzles
# for English (full wordlist), (75,15) gives 9889 puzzles
# for Gàidhlig (headwords only), (75,15) gives 3451 puzzles
my $minscore=75;
my $mincount=15;
my @puzzlelist = shuffle(keys %puzzles);
my %ans;
my $datestr = '2022-01-14';
for my $p (@puzzlelist) {
	my @pangrams = sort keys %{$puzzles{$p}};
	my %cands;
	for my $w (keys %words) {
		my $patt = $words{$w};
		$patt =~ s/(.)/$1.".*"/ge;
		$cands{$w} = 1 if ($p =~ m/$patt/);
	}
	my @candidate_puzzles; # any of the 7 meeting the score/wordcount criteria
	for (my $i=0; $i<7; $i++) {
		my $c = substr($p,$i,1);
		my @allwords;
		my $score = 0;
		for my $w (sort keys %cands) {
			next unless ($w =~ m/$c/);
			push @allwords, $w;
			if (length($w)==4) {
				$score++;
			}
			else {
				$score += length($w);
				$score += 7 if (exists($puzzles{$p}->{$w}));
			}
		}
		if (scalar(@allwords)>=$mincount and $score>=$minscore) {
			my @letters = split(//,$p);
			my $temp = $letters[3];
			$letters[3] = $letters[$i]; # required by the JavaScript
			$letters[$i] = $temp;
			# pangrams, center_letter not actually used in JS
			push @candidate_puzzles, {
					'pangrams' => \@pangrams,
					'letters' => join('',@letters),
					'maxscore' => $score,
					'center_letter' => $c,
					'possible_words' => \@allwords,
			};
		}
	}
	if (scalar(@candidate_puzzles)>0) {
		$ans{$datestr} = $candidate_puzzles[ rand @candidate_puzzles ];
		$datestr = increment_date($datestr);
	}
}

open(JSONOUT, ">:utf8", "puzzles-$teanga.json") or die "Could not open JSON: $!";
print JSONOUT to_json(\%ans, { pretty => 1 });
close JSONOUT;
store \%ans, "puzzles-$teanga.hash";

exit 0;
