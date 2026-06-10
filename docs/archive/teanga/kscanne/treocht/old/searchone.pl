#!/usr/bin/perl

use strict;
use warnings;
use utf8;

# number of months to lump together when writing output
# 1 => monthly numbers, 3 => quarterly numbers, 12 => annual numbers, etc.
my $N = 1;
my $HERE='/home/kps/gaeilge/treocht';

# reads one tab-separated line from standard input that looks like this:
# ciniciúil\t[Cc]h?iniciú(il|la)\tsoiniciúil\t[Ss]h?oiniciú(il|la)"
#  Alternate column headers (human-readable description of the pattern)
#  and the actual regex to use in searching

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

sub count_in_file {
	(my $f, my $p) = @_;
	my $count = 0;
	open(MONTH, "<:utf8", "$HERE/glan/$f") or die "Could not open $f: $!";
	while (<MONTH>) {
		chomp;
		my $line = $_;
		while ($line =~ m/$p/g) {
			$count++;
		}
	}
	close MONTH;
	return $count;
}

my %total;
open(COUNTS, "<:utf8", "$HERE/counts.txt") or die "Could not open counts.txt: $!";
while (<COUNTS>) {
	chomp;
	(my $month, my $c) = m/^([0-9]{4}-[0-9][0-9]) ([0-9]+)$/;
	$total{$month} = $c;
}
close COUNTS;

while (<STDIN>) {
	chomp;
	my $line = $_;
	my @all = split(/\t/,$line);
	my @readable;
	my @patt;
	my $count=0;
	for my $a (@all) {
		if ($count % 2 == 0) {
			push @readable, $a;
		}
		else {
			push @patt, qr/(^|\P{L})$a($|\P{L})/;
		}
		$count++;
	}
	print 'Dáta';
	for (@readable) {
		print ",$_";
	}
	print "\n";
	my $cycle = $N;
	my $toprint;
	my %running_count;
	for my $p (@patt) {
		$running_count{$p} = 0;
	}
	my $running_total = 0;
	opendir(D, "${HERE}/glan") or die "Could not open glan directory: $!";
	my @months = sort readdir(D);
	for my $m (@months) {
		$m =~ s/^.*\/([0-9]{4}-[0-9][0-9])$/$1/;
		#next unless ($m =~ m/^20(0[4-9]|1[0-9])-[0-9][0-9]$/); # 2004-
		next unless ($m =~ m/^20(1[4-9]|[2-9][0-9])-[0-9][0-9]$/); # 2014-
		if ($cycle==0) {
			print $toprint;
			for my $p (@patt) {
				my $ans = 1000000.0*$running_count{$p} / $running_total;
				print ",$ans";
			}
			print "\n";
			for my $p (@patt) {
				$running_count{$p} = 0;
			}
			$running_total = 0;
		}
		$running_total += $total{$m};
		for my $p (@patt) {
			$running_count{$p} += count_in_file($m,$p);
		}
		$toprint = $m if ($cycle % $N == 0);
		$cycle = ($cycle+1) % $N;
	}
	closedir(D);
}

exit 0;
