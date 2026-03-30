#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

# pipe fullstem-nomutate-gd.txt through this
# and output in "speling.org" format; see
# http://wiki.apertium.org/wiki/Speling_format

while (<STDIN>) {
	chomp;
	(my $pos, my $surface, my $lemmapos, my $lemma) = m/^(<[^>]+>)([^<]+)<\/[A-Z]> <([A-Z])[^>]*>([^<]+)<\/[A-Z]>$/;
	my $flags;
	my $my_pos;
	if ($pos =~ m/^<N/) {
		$my_pos = 'n';
		if ($pos =~ m/gnd="m"/) {
			$my_pos .= '.m';
		}
		elsif ($pos =~ m/gnd="f"/) {
			$my_pos .= '.f';
		}
		if ($pos =~ m/pl="y"/) {
			$flags = 'pl';
		}
		else {
			$flags = 'sg';
		}
		if ($pos =~ m/gnt="n"/) {
			$flags .= '.com';
		}
		elsif ($pos =~ m/gnt="y"/) {
			$flags .= '.gen';
		}
#  no datives else { $flags .= '.dat'; }
		if ($lemmapos eq 'V') {
			if ($my_pos =~ /f$/) {
				$flags = "ger.f.$flags";
			}
			elsif ($my_pos =~ /m$/) {
				$flags = "ger.m.$flags";
			}
			else {
				$flags = "ger.$flags";
			}
			$my_pos = 'vblex';
		}
		print "$lemma; $surface; $flags; $my_pos\n";
	}
	elsif ($pos =~ m/^<V/) {  # don't forget copula
		$my_pos = 'vblex';
		if ($pos =~ m/cop="y"/) {
			next;
		}
		else {
	         # ignoring p="[y|n]" now, use endings
			if ($pos =~ m/t="ord"/) {
				$flags = 'imp';
				if ($surface eq $lemma) {
					print "$lemma; $surface; $flags.p2.sg; $my_pos\n";
				}
				elsif ($surface =~ m/ibh$/) {
					print "$lemma; $surface; $flags.p2.pl; $my_pos\n";
				}
				else {
					print STDERR "Fadhb le foirm $surface (ord)\n";
				}
			}
	         # elsif ($pos =~ m/t="láith"/) { }   
			elsif ($pos =~ m/t="coinn"/) {
				$flags = 'cni';
				if ($surface =~ m/nn$/) {
					print "$lemma; $surface; $flags.p1.sg; $my_pos\n";
				}
				elsif ($surface =~ m/fe?á$/) {
				}
				elsif ($surface =~ m/dh$/) {
					print "$lemma; $surface; $flags.p2.sg; $my_pos\n";
					print "$lemma; $surface; $flags.p3.sg; $my_pos\n";
					print "$lemma; $surface; $flags.p2.pl; $my_pos\n";
					print "$lemma; $surface; $flags.p3.pl; $my_pos\n";
				}
				elsif ($surface =~ m/maid$/) {
					print "$lemma; $surface; $flags.p1.pl; $my_pos\n";
				}
				else {
					print STDERR "Fadhb le foirm $surface (coinn)\n";
				}
			}
	         # elsif ($pos =~ m/t="gnáth"/) { }   
			elsif ($pos =~ m/t="fáist"/) {
				$flags = 'fti';
				if ($surface =~ m/idh$/ or $surface eq 'nì') {
					print "$lemma; $surface; $flags.p1.sg; $my_pos\n";
					print "$lemma; $surface; $flags.p2.sg; $my_pos\n";
					print "$lemma; $surface; $flags.p3.sg; $my_pos\n";
					print "$lemma; $surface; $flags.p1.pl; $my_pos\n";
					print "$lemma; $surface; $flags.p2.pl; $my_pos\n";
					print "$lemma; $surface; $flags.p3.pl; $my_pos\n";
				}
				else {
					print STDERR "Fadhb le foirm $surface (fáist)\n";
				}
			}
			elsif ($pos =~ m/t="caite"/) {
				$flags = 'past';
				if ($surface eq $lemma or $surface eq 'ràinig' or $surface eq 'rinn' or $surface eq 'rug') {
					print "$lemma; $surface; $flags.p1.sg; $my_pos\n";
					print "$lemma; $surface; $flags.p2.sg; $my_pos\n";
					print "$lemma; $surface; $flags.p3.sg; $my_pos\n";
					print "$lemma; $surface; $flags.p1.pl; $my_pos\n";
					print "$lemma; $surface; $flags.p2.pl; $my_pos\n";
					print "$lemma; $surface; $flags.p3.pl; $my_pos\n";
				}
				else {
					print STDERR "Fadhb le foirm $surface (caite)\n";
				}
			}
	         # elsif ($pos =~ m/t="foshuit"/) { }   
		}
	}
	elsif ($pos =~ m/^<A/) {
		$my_pos = 'adj';
		if ($pos =~ m/gnt="y"/) {
			if ($pos =~ m/gnd="m"/) {
				$flags = 'm';
			}
			elsif ($pos =~ m/gnd="f"/) {
				$flags = 'f';
			}
			$flags .= '.sg.gen';
		}
		elsif ($pos =~ m/pl="y"/) {
			$flags = 'pl';
		}
		else {
			$flags = 'sg';
		}
		if ($lemmapos eq 'V') {
			$my_pos = 'vblex';
			$flags = "pp.$flags";
		}
		print "$lemma; $surface; $flags; $my_pos\n";
	}
#	elsif ($pos =~ m/^<R/) {
#		$my_pos = 'adv';
#	}
#	elsif ($pos =~ m/^<S/) {
#		$my_pos = 'pr';
#	}
#	elsif ($pos =~ m/^<P/) {
#		$my_pos = 'prn';
#	}
#	elsif ($pos =~ m/^<T/) {
#		$my_pos = 'det';
#	}
#	elsif ($pos =~ m/^<I/) {
#		$my_pos = 'ij';
#	}
	else {
		next;  # <O>, <C>, <D>, <U>, <Q>
	}
}
exit 0;
