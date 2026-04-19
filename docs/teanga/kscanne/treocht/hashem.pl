#!/usr/bin/perl

use strict;
use warnings;
use utf8;
use Storable;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

# CHANGE THIS IN ~/gaeilge/canuinti/buildtable.sh TOO!
my $N = 50000;
my %total;  # keys are months, values are total number of words in that month
my %words;  # keys are top $N words, vals are *total* counts
my %counts; # keys look like "agus|2015-01", values are count for that month
my %table;  # keys are top $N words, vals are comma-separated rel. freqs,
			# one per month since 2015-01

sub month_count {
	(my $w, my $m) = @_;
	my $key = "$w|$m";
	return $counts{$key} if (exists($counts{$key}));
	return 0;
}

# units are # per million words
sub month_rel_freq {
	(my $w, my $m) = @_;
	return 1000000.0*month_count($w,$m)/(1.0*$total{$m});
}

# first, fill up %total hash
print "Reading monthly word totals from counts.txt...\n";
open(COUNTS, "<:utf8", "counts.txt") or die "Could not open counts.txt: $!";
my $lastmonth;
while (<COUNTS>) {
	chomp;
	(my $m, my $c) = m/^([0-9]{4}-[0-9][0-9]) ([0-9]+)$/;
	# NB <<< This is where we determine the months to include in DB
	next unless ($m =~ m/^20(1[5-9]|[2-9][0-9])-[0-9][0-9]$/); # 2015-
	$total{$m} = $c;
	$lastmonth = $m;
}
close COUNTS;
delete $total{$lastmonth};

# now, put all candidate words into %words hash
print "Reading total word frequencies (all-time) from freq.txt, top $N words...\n";
open(FREQ, "<:utf8", "freq.txt") or die "Could not open freq.txt: $!";
while (<FREQ>) {
	chomp;
	(my $c, my $w) = split(/ /);
	$words{$w} = $c;
	last if ($. >= $N);
}
close FREQ;

# next, fill the %counts hash with month-by-month word counts (top $N only)
print "Reading month-by-month frequency files from freq/ directory...\n";
my @months = sort keys %total;
for my $m (@months) {
	open(MONTH, "<:utf8", "freq/$m") or die "Could not open freq/$m: $!";
	while (<MONTH>) {
		chomp;
		(my $c, my $w) = split(/ /);
		$counts{"$w|$m"} = $c if (exists($words{$w}));
	}
	close MONTH;
}

# finally, fill the final %table hash which we'll write out
print "Computing the final hash table for writing to disk...\n";
for my $w (keys %words) {
	# should only be 2015-01 ... present
	my $val='';
	for my $m (@months) {
		my $relfreq = month_rel_freq($w,$m);
		$relfreq = sprintf("%.2f", $relfreq) unless ($relfreq==0);
		$val .= "$relfreq,";
	}
	$val =~ s/.$//;
	$table{$w} = $val;
}
$table{'MONTHS'} = join(',',sort keys %total);

print "Writing to table.hash...\n";
store \%table, "table.hash";
exit 0;
