#!/usr/bin/perl


use strict;
use warnings;
use Term::ANSIColor;
use Data::Dumper;
use utf8;

# first argument is the (tagged) word to disambiguate
my $sprioc = $ARGV[0];
# second argument is the list of stemmed sentences to disambiguate
#  can't read them from stdin since user must input answers!
my $datafile = $ARGV[1];
my %alreadydone;

sub userinput {
        my ($prompt) = @_;
        print "$prompt: ";
        $| = 1;          # flush
        $_ = getc;
        my $ans;
        while (m/[^\n]/) {
                $ans .= $_;
                $_ = getc;
        }
        return $ans;
}

die "You should specify the target word with its XML tag!\n" unless ($sprioc =~ m/^<[A-Z][^>]*>[^<>]+<\/[A-Z]>$/);

my $spriocfhocal = $sprioc;    # filename with training data for this word
$spriocfhocal =~ s/<[^>]+>//g;
(my $tg) = $sprioc =~ m/^<([A-Z])/;
$spriocfhocal =~ s/'//g;
$spriocfhocal =~ s/á/a_/g;
$spriocfhocal =~ s/é/e_/g;
$spriocfhocal =~ s/í/i_/g;
$spriocfhocal =~ s/ó/o_/g;
$spriocfhocal =~ s/ú/u_/g;
$spriocfhocal .= $tg;
$spriocfhocal = 'ba_NM' if ($sprioc eq '<N pl="n" gnt="n" gnd="m">bá</N>');

open (IONCHUR, "<:utf8", "../traenail/$spriocfhocal") or die "Could not open disambiguated corpus file \"traenail/$spriocfhocal\": $!\n";

while (<IONCHUR>) {
	chomp;
	(my $s, my $sentence) = m/^([-0-9]+) (.*)$/;
	$alreadydone{$sentence} = $s;
}
close IONCHUR;

open (CANDS, "<:utf8", $datafile) or die "Could not read sentences to train: $!\n";
while (<CANDS>) {
	chomp;
	my $cand = $_;
	my $taisp = $_;
	$taisp =~ s/$sprioc/colored($sprioc,'bold red')/eg;
	$taisp =~ s/<[^>]+>//g;
	print "\n$taisp\n";
	if (exists($alreadydone{$cand})) {
		print "This sentence already done (sense $alreadydone{$cand}):\n\n";
	}
	else {
		my $sense = 'A';
		$sense = userinput("Sense (-1=don't use for training)") while ($sense !~ m/(?:-1|[0-9])/);
		$alreadydone{$cand} = $sense;
	}
}
close CANDS;

open (ASCHUR, ">:utf8", "../traenail/$spriocfhocal") or die "Could not open output file: $!\n";
print ASCHUR "$alreadydone{$_} $_\n" foreach (sort keys %alreadydone);
close ASCHUR;

###########################################################################
#  This block selects the "feature" words to gather stats on and sticks
#  then into a hash called "final"

my %counts;
my %stoplist;
my %fullfreq;

open (FREQLIST, "/home/kps/gaeilge/ga2gd/beostem/FREQ") or die "Could not open stem frequency list: $!\n";
while (<FREQLIST>) {
	m/^ *([1-9][0-9]*) (<[^>]+>[^<]+<\/[A-Z]>)$/;
	$fullfreq{$2} = $1;
}
close FREQLIST;

open (STOPLIST, "<:utf8", "stoplist.txt") or die "Could not open stoplist: $!\n";
while (<STOPLIST>) {
	chomp;
	$stoplist{$_}++;
}
close STOPLIST;

foreach (keys %alreadydone) {
	while (/((<[ANV][^>]*>)[^<]+<\/[ANV]>)/g) {
		unless (exists($stoplist{$1}) or $sprioc eq $1 or $2 eq '<V cop="y">') {
			$counts{$1}++;
		}
	}
}

# first toss out lowest frequency tokens
my @cands = sort {$counts{$b} <=> $counts{$a}} keys %counts;
$#cands = 199 if ($#cands > 199);
# then keep only highest, measured according to *relative* frequency
@cands = sort {$counts{$b}/$fullfreq{$b} <=> $counts{$a}/$fullfreq{$a}} @cands;
$#cands = 74 if ($#cands > 74);
my %final;
$final{$_}++ foreach (@cands);

###########################################################################
#  This block computes the statistics and writes to a .dat file

my %P;  # plain probabilities P(s) of each sense
my %N;  # number of tokens seen for each sense
my %seen=();  # hash of hashes; $seen{'0'}{"<C>agus</C>"} is the number of
              # times "agus" appears in training data with sense 0
my %C;  # conditional probabilities P(v_j, s)   See p.640 Gur.-Martin
	# computed from counts in "seen"
my %unseen;  # probability to assign to unseen tokens
my $total = 0;   # number of disambiguated sentences
my $V = 47216;  # total "vocabulary size"; i.e. number of tagged words
                # in the corpus.  Get it as follows:
		# cat ../beostem/FREQ | wc -l
		# Only needed for "smoothing" zero counts.

# this loop just does *counts*; log probs are computed in following loop
foreach my $sentence (keys %alreadydone) {
	my $s = $alreadydone{$sentence};
	unless ($s eq "-1") {
		if (exists($P{$s})) {
			$P{$s}++;
		}
		else {
			$P{$s}=1;
			$N{$s}=0;
			$seen{$s}=();
		}
		$total++;
		# all of the "smarts" are contained in this loop - this is
		# the only place where it is decided which "features" of the
		# sentence are tracked and for which probs are computed.
		# Everything else is generic and just loops over keys of the C hash
		while ($sentence =~ m/(<[^>]+>[^<]+<\/[A-Z]>)/g) {
			$N{$s}++;
			if (exists($final{$1})) {
				if (exists($seen{$s}{$1})) {
					$seen{$s}{$1}++;
				}
				else {
					$seen{$s}{$1}=1;
				}
	#		print "I've seen $1 in sense $s sentence $seen{$s}{$1} times\n";
			}
		}
	}
}

# turn counts into log probs
foreach my $s (keys %P) {
	my $T = scalar(keys %{$seen{$s}});
	my $Z = $V - $T;   # tagged words not appearing with this sense
	$unseen{$s} = log($T) - log($Z) - log($N{$s} + $T);
	foreach (keys %{$seen{$s}}) {
		$C{"$_|$s"} = log($seen{$s}{$_}) - log($N{$s} + $T);
	}
}
$P{$_} = log($P{$_}) - log($total) foreach (keys %P);

# store P, C, N, unseen
open (DATAOUT, ">:utf8", "../traenail/$spriocfhocal.dat") or die "Could not open output .dat file: $!\n";
print DATAOUT Data::Dumper->Dump([\%P, \%C, \%unseen], [qw(P C unseen)]);
close DATAOUT;

exit 0;
