#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

# prefix flags - A,B,C on verbs with initial voiceless consonant, P,Q,R on rest
my $flag = $ARGV[0];

# reads in prefixes.txt from stdin, one per line, and 
# output .aff file lines
my $ans = '';
my $count = 0;
while (<STDIN>) {
	chomp;
	my $startbuttwo='';
	my $penult='';
	my $start='';
	my $final=$_;
	if (length($_) > 1) {
		m/^(.*)(.)(.)$/;
		$startbuttwo = $1;
		$penult = $2;
		$start = $startbuttwo.$penult;
		$final = $3;
	}
	if ($flag =~ /^[ABC]$/) {
#  Used to apply Dahl's law in this script, now voiced prefixes generated
#  by rw.pl (applied to "som") and piped in here...
#		my $dahl_p = m/[kt][aeiou]+$/;
#		my $voiced = $_;
#		if ($dahl_p) {
#			$voiced =~ s/k([aeiou]+)$/g$1/;
#			$voiced =~ s/t([aeiou]+)$/d$1/;
#		}
		$ans .= "PFX $flag 0 $_/SX .\n"; $count++;
	}
	else {
		if ($final eq 'a') {
			$ans .= "PFX $flag 0 $start/SX [aeou]\n"; $count++;
			$ans .= "PFX $flag i $start"."e/SX i\n"; $count++;
			$ans .= "PFX $flag 0 $_/SX [^aeiou]\n"; $count++;
		}
		elsif ($final eq 'e' or $final eq 'i') {
			if ($penult eq 'w' or $penult eq 'y') { # glide, but new y is deleted
				$ans .= "PFX $flag 0 $start/SX [aeiou]\n"; $count++;
			}
			else { # glide
				$ans .= "PFX $flag 0 $start"."y/SX [aeiou]\n"; $count++;
			}
			$ans .= "PFX $flag 0 $_/SX [^aeiou]\n"; $count++;
		}
		elsif ($final eq 'u') {
			if (/[fghkv]u$/) {
				$ans .= "PFX $flag 0 $start/SX [aeiou]\n"; $count++;
				$ans .= "PFX $flag 0 $_/SX [^aeiou]\n"; $count++;
			}
			else {
				if ($penult eq 'w' or $penult eq 'y') { # glide, but delete y or w
					$ans .= "PFX $flag 0 $startbuttwo"."w/SX [aeiou]\n"; $count++;
				}
				else { # glide
					$ans .= "PFX $flag 0 $start"."w/SX [aeiou]\n"; $count++;
				}
				$ans .= "PFX $flag 0 $_/SX [^aeiou]\n"; $count++;
			}
		}
		elsif ($final eq 'n') {
			$ans .= "PFX $flag 0 $_"."y/SX [aeiou]\n"; $count++;
			$ans .= "PFX $flag n $_/SX n\n"; $count++;
			$ans .= "PFX $flag 0 $_/SX [^aeioun]\n"; $count++;
		}
		else {  # prefix ends with consonant
			print STDERR "Warning: unexpected final letter in prefix $_.\n";
		}
	} # P,Q,R flags
} # while loop over prefixes
$ans =~ s/^/PFX $flag Y $count\n/;
print $ans;

exit 0;
