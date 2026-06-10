#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %all;
my $currtext=undef;
my $curr2print='';
my $curr2comp='';
while (<STDIN>) {
	chomp;
	$curr2print .= "$_\n";
	if (m/^# text = (.+)$/) {
		$currtext = $1;
	}
	elsif (m/^#/) {
		1;
	}
	elsif (m/^$/) {
		if (exists($all{$currtext})) {
			if ($all{$currtext} ne $curr2comp) {
				print STDERR "have already seen sentence: $currtext\n";
				print STDERR "!!!! previous annotation differs !!!!\n";
				print STDERR "Previous:\n$all{$currtext}";
				print STDERR "This:\n$curr2comp";
			}
		}
		else {
			print $curr2print;
			$all{$currtext} = $curr2comp;
		}
		$currtext = undef;
		$curr2comp = '';
		$curr2print = '';
	}
	elsif (m/^[0-9]/) {
		$curr2comp .= "$_\n";
	}
}

exit 0;
