#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

# reads in suffixes.txt from stdin, one per line, and 
# output .aff file lines
my $ans = '';
my $count = 0;
while (<STDIN>) {
	chomp;
	m/^(.)(.*)$/;
	my $initial = $1;
	my $rest = $2;
	if ($initial =~ /^[aeiou]$/) {  # suffix starts with vowel
		if ($initial eq 'i') {
			$ans .= "SFX S a e$rest/X a\n"; $count++;
		}
		else {
			$ans .= "SFX S a $_/X a\n"; $count++;
		}
		$ans .= "SFX S e y$_/X e\n"; $count++;
		$ans .= "SFX S i y$_/X i\n"; $count++;
		$ans .= "SFX S o w$_/X o\n"; $count++;
		$ans .= "SFX S u w$_/X u\n"; $count++;
		if (/^i[^z]/) {  # t is ok, itse is from ik+ye
			$ans .= "SFX S 0 e$rest/X [eo][^aeiou]\n"; $count++;
			$ans .= "SFX S 0 $_/X [^eo][^aeiou]\n"; $count++;
		}
		else {
			$ans .= "SFX S 0 $_/X [^aeiou]\n"; $count++;
		}
	}
	else {  # suffix starts with consonant
		if (/^ye/) {
			$ans .= "SFX S 0 g$rest/X b\n"; $count++;
			$ans .= "SFX S d z$_/X d\n"; $count++;
			$ans .= "SFX S g z$_/X g\n"; $count++;
			$ans .= "SFX S k ts$_/X k\n"; $count++;
			$ans .= "SFX S 0 n$rest/X m\n"; $count++;
			$ans .= "SFX S 0 $rest/X [hjnsz]\n"; $count++;
			$ans .= "SFX S p k$rest/X p\n"; $count++;
			$ans .= "SFX S r $_/X r\n"; $count++;
			$ans .= "SFX S t s$rest/X t\n"; $count++;
			$ans .= "SFX S 0 $_/X [^bdghjkmnprstz]\n"; $count++;
		}
		else {
			$ans .= "SFX S 0 $_/X .\n"; $count++;
		}
	}
}
$ans =~ s/^/SFX S Y $count\n/;
print $ans;

exit 0;
