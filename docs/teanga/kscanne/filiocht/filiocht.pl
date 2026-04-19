#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my $usaid = "Usage: $0 [-a|-f]\n-a = amhrán an ghréasáin\n-f = foclóir rímeanna\n";
die $usaid if ($#ARGV != 0);
my $brat = $ARGV[0];
die $usaid unless ($brat =~ /^-[af]$/);

# settings...
# if the max/min syllables are tweaked, can probably tweak the
# max/min character counts allowed in the driver script file.sh
my $minsyls=7;
my $maxsyls=14;
my $queuesize=1;  # max we'll keep with a given rhyme

if ($brat eq '-f') {
	$minsyls=0;
}

####################################################################
# keys are rhyme, value is arrayref of sentences ending in that rhyme
my %storas;

sub syllables {
	(my $ipa) = @_;
	$ipa =~ s/[aeiouə]/X/g;
	$ipa =~ s/X+/X/g;
	return ($ipa =~ tr/X//);
}

# ipa to ipa
sub lenite_guess {
	(my $ipa) = @_;
	$ipa =~ s/^b/v/;
	$ipa =~ s/^k/x/;
	$ipa =~ s/^[dg]/ɣ/;
	$ipa =~ s/^m/v/;
	$ipa =~ s/^p/f/;
	$ipa =~ s/^s/h/;
	$ipa =~ s/^t/h/;
	return $ipa;
}

# ipa to ipa
# to fix: gCuntas vs. Cuntas (g->n, k->g!)
sub eclipse_guess {
	(my $ipa) = @_;
	$ipa =~ s/^b/m/;
	$ipa =~ s/^[dg]/n/;
	$ipa =~ s/^k/g/;
	$ipa =~ s/^f/v/;
	$ipa =~ s/^p/b/;
	$ipa =~ s/^t/d/;
	return $ipa;
}

my %nbrs = (
'b' => 'bvmpf',
'd' => 'dɣnth',
'f' => 'fvpb',
'g' => 'gɣnkx',
'h' => 'hstd',
'k' => 'kxg',
'm' => 'mvb',
'n' => 'ndgɣ',
'p' => 'pfb',
's' => 'sht',
't' => 'thds',
'v' => 'vbfm',
'x' => 'xkg',
'ɣ' => 'ɣdgn',
);

# two arguments are single letters, in IPA
# return true iff they could be mutations of the same word
sub neighbors_p {
	(my $l1, my $l2) = @_;
	return (exists($nbrs{$l1}) and $nbrs{$l1} =~ m/$l2/);
}

sub same_last_word_p {
	(my $ipa1, my $ipa2) = @_;
	my $w1 = lastword($ipa1);
	my $w2 = lastword($ipa2);
	# nb "lastword" strips palatization marks '
	return 1 if ($w1 eq "h$w2" or $w2 eq "h$w1");  # ha:t' vs. a:t'
	return 1 if ($w1 eq "m$w2" or $w2 eq "m$w1");  # ma:t' vs. a:t'
	return 1 if ($w1 eq "d$w2" or $w2 eq "d$w1");  # ma:t' vs. a:t'
	return 1 if ($w1 eq "f$w2" or $w2 eq "f$w1");  # fada vs. fhada
	return 1 if ($w1 eq "b$w2" or $w2 eq "b$w1");  # fhéidir vs. b'fhéidir
	return 1 if ($w1 eq "t$w2" or $w2 eq "t$w1");  # t-anam vs anam
	(my $first1, my $rest1) = $w1 =~ m/^(.)(.*)$/;
	(my $first2, my $rest2) = $w2 =~ m/^(.)(.*)$/;
	return 0 if ($rest1 ne $rest2);  # including if lengths of w1/w2 differ!
	return 1 if (neighbors_p($first1,$first2));
	return ($first1 eq $first2);
# add other cases too; one a subset of the other (lár, céartlár)
# note that mutation check throws out pair (tsaoirse, daoirse) :/
}

# returns undef if last word has no IPA (<xxx>)
# or if it's just a short schwa (gə, etc.)  which shouldn't happen much
sub rhyme {
	(my $ipa) = @_;
	$ipa =~ s/ihə *$/əhə/; # so "beartaithe" and "cáilithe" don't rhyme
	$ipa =~ s/i:əxt(ə? *)$/əəxt$1/; # don't want "aclaíocht"+"polaitíocht"
	# long i: at the end is very common but isn't enough for a rhyme
	# short i is *uncommon*, mostly just aici, uirthi, roimpi, etc.
	# but similarly want to include more of the word
	(my $tail) = $ipa =~ m/([aeiou:]+[^ aeiou:>]*(i:?)?) *$/;
	#print "no rhyme for ipa = $ipa\n" if (!defined($tail));
	return $tail;
}

# note we break at stress marks too, so ansin/anseo
# at end of a sentence => last word is sin/seo as it should be
sub lastword {
	(my $ipa) = @_;
	(my $tail) = $ipa =~ m/([^ˈˌ ]*) *$/;
	if (defined($tail)) {
		$tail =~ s/[']//g;  # l'om -> lom
	}
	return $tail;
}

# reads output of ipa.pl phonetic transcription script
# which has one token per line, and a line with 
# <BRISEADH> at each sentence break (line breaks in original source)
my $curripa='';
while (<STDIN>) {
	chomp;
	if (m/^<BRISEADH>/) {
		my $sentence = $_;
		my $syls = syllables($curripa);
		if ($syls >= $minsyls and $syls <=$maxsyls) {
			$sentence =~ s/^<BRISEADH>//;
			$sentence =~ s/\t/ /g;
			my $rim = rhyme($curripa);
			if (defined($rim)) {
				#print "Sentence: $sentence\n";
				#print "IPA: $curripa\n";
				#print "Syllables: $syls\n";
				#print "Rhyme: $rim\n";
				if ($brat eq '-a' and exists($storas{$rim}) and scalar @{$storas{$rim}} > 0) {
					# anything in array should have same last word; no need to loop
					my $prev = $storas{$rim}->[0];
					(my $prevsent, my $previpa) = $prev =~ m/^(.+)\t(.+)$/;
					if (same_last_word_p($previpa,$curripa)) {
						push @{$storas{$rim}}, "$sentence\t$curripa" if (scalar @{$storas{$rim}} < $queuesize);
					}
					else {
						print "$prevsent\n";
						print "$sentence\n\n";
						shift @{$storas{$rim}};
					}
				}
				else {
					push @{$storas{$rim}}, "$sentence\t$curripa";
				}
			}
		}
		$curripa = '';
	}
	else {
		$curripa .= $_;
		$curripa .= ' ';
	}
}

if ($brat eq '-f') {
	for my $r (keys %storas) {
		my %seenlc;
		my @rhyming;
		for my $w (@{$storas{$r}}) {
			$w =~ s/\t.*//;
			unless (exists($seenlc{lc($w)})) {
				push @rhyming, $w;
				$seenlc{lc($w)} = 1;
			}
		}
		next if (scalar @rhyming < 2);
		print join(', ',@rhyming)."\n";
	}
}

exit 0;
