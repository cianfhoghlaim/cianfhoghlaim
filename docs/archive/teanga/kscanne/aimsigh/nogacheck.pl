#!/usr/bin/perl

use strict;
use warnings;
use Lingua::GA::Gramadoir;
use Encode qw(encode);

my $gr = new Lingua::GA::Gramadoir;

my $doccount=0;
while ($ARGV = shift @ARGV) {
	unless (open(ARGV, "<:bytes", $ARGV)) {
		warn "Could not open $ARGV: $!\n";
		next;
	}
	$doccount++;
	if ($doccount % 100 == 0) {
		print STDERR "$doccount...\n";
	}
	local $/;
	my $text = <ARGV>;
	my $missp = $gr->spell_check($text);
	my %missp_hash=();
	foreach my $bad (@$missp) {
		$missp_hash{$bad}++;
	}
	my $tokenref = $gr->tokenize($text);
	my $streak=0;
	my $best=0;
	for my $tok (@$tokenref) {
		if (exists($missp_hash{$tok})) {
			$streak=0;
		}
		else {
			$streak++;
			$best = $streak if ($streak > $best);
			last if ($streak > 5);
		}
	}
	print "$ARGV\n" if ($streak < 6);
#	print "$ARGV: $best\n" if ($streak < 6);
	close ARGV;
}
