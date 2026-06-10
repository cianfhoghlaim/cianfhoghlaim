#!/usr/bin/perl

use strict;
use warnings;
use Lingua::GA::Gramadoir;

my $obj = new Lingua::GA::Gramadoir;

# no need to to_lower things, normalize etc. in these
# counts since they're just used for finding dupes, so 
# more uniqueness of tokens in better

sub process_me
{
	(my $text) = @_;
	my %seen;
	$seen{$_}++ foreach (@{$obj->tokenize($text)});
	$text='';
	$text .= "$_ $seen{$_}\n" foreach (sort keys %seen);
	return $text;
}

binmode STDOUT, ":encoding(iso-8859-1)";
binmode STDERR, ":encoding(iso-8859-1)";
binmode STDIN, ":bytes";

my $crub='/usr/local/share/crubadan/ga';
my $range="/snapshot/aimsigh/FREQ";

sub bytimestamp
{
	my $N = 0;
	opendir DIRH, "$crub/ciu" or die "could not open ciu dir: $!\n";
	foreach my $doctxt (readdir DIRH) {
		next if $doctxt !~ /\.txt$/;
		my $sprioc = "$range/$doctxt";
		my $foinse = "$crub/ciu/$doctxt";
		my $doit = 0;
		$N++;
		print "$N..." if ($N % 100 == 0);
		if (-e $sprioc) {
			my @stat1 = stat($foinse);
			my @stat2 = stat($sprioc);
			$doit = ($stat1[9] > $stat2[9]);
			print "Tokenizing $doctxt (out of date)...\n" if $doit;
		}
		else {
			$doit=1;
			print "Tokenizing $doctxt (first time)...\n";
		}
		if ($doit) {
			open (FOINSE, "<", $foinse) or die "Could not open source file $foinse: $!\n";
			local $/;
			$_ = <FOINSE>;
			close FOINSE;
			open (SPRIOC, ">", $sprioc) or die "Could not open target file $sprioc: $!\n";
			print SPRIOC process_me($_);
			close SPRIOC;
		}
	}
	closedir DIRH;
}

sub byqueue
{
	open(ANCIU, "<", "$crub/ANCIU") or die "could not open ANCIU: $!\n";
	while (<ANCIU>) {
		chomp;
		my $doctxt="$_.txt";
		my $sprioc = "$range/$doctxt";
		my $foinse = "$crub/ciu/$doctxt";
		print "Tokenizing $doctxt (first time)...\n";
		open (FOINSE, "<", $foinse) or die "Could not open source file $foinse: $!\n";
		local $/;
		$_ = <FOINSE>;
		close FOINSE;
		open (SPRIOC, ">", $sprioc) or die "Could not open target file $sprioc: $!\n";
		print SPRIOC process_me($_);
		close SPRIOC;
	}
	close ANCIU;
}

# bytimestamp();
byqueue();
exit 0;
