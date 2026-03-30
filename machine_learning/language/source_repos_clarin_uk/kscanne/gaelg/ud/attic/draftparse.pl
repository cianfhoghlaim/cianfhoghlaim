#!/usr/bin/perl
# Rules for filling in some easy deprels based on context;
# should be obsolete once we have bootstrapped a decent UD parser

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

sub one_pass {
	(my $aref) = @_;
	my $len = scalar(@$aref);
	my $conllu_index = 0;
	my $firstverb = -1;   # this will be a conllu_index, not "$i"
	my $lastnoun = -1;  # this will be a conllu_index, not "$i"
	for (my $i=0; $i < $len; $i++) {
		my $hr = $aref->[$i];
		$conllu_index++ if ($hr->{'n'} !~ m/-/);
		next if ($hr->{'t'} ne '' and $hr->{'h'} ne '');
		if ($hr->{'n'} =~ m/-/) {   # multiword tokens
			$hr->{'t'} = '_';
			$hr->{'h'} = '_';
		}
		elsif ($hr->{'p'} eq 'ADJ') {
			$hr->{'t'} = 'amod';
			if ($hr->{'s'} =~ m/^(drogh|shenn)$/) {
				$hr->{'h'} = $conllu_index+1;
			}
			else {
				if ($lastnoun==-1) {
					$hr->{'h'} = $conllu_index-1;
				}
				else {
					$hr->{'h'} = $lastnoun;
				}
			}
		}
		elsif ($hr->{'p'} eq 'ADP') {
			if ($aref->[$i+1]->{'p'} eq 'DET') {
				$hr->{'h'} = $conllu_index+2;
				$hr->{'t'} = 'case';
				$aref->[$i+1]->{'h'} = $conllu_index+2;
				$aref->[$i+1]->{'t'} = 'det';
			}
			elsif ($hr->{'s'} eq 'cordail' and $aref->[$i+1]->{'w'} =~ m/^[Rr]ish$/) {
				$hr->{'h'} = $conllu_index+2;
				$hr->{'t'} = 'case';
				$aref->[$i+1]->{'h'} = $conllu_index;
				$aref->[$i+1]->{'t'} = 'fixed';
			}
			elsif ($hr->{'s'} eq 'myr' and $aref->[$i+1]->{'s'} =~ m/^[Ss](hoh|hen)$/) {
				# following Irish...
				$hr->{'h'} = $conllu_index+2;
				$hr->{'t'} = 'advmod';
				$aref->[$i+1]->{'h'} = $conllu_index;
				$aref->[$i+1]->{'t'} = 'fixed';
				
			}
			elsif ($hr->{'s'} eq 'y') {
				$hr->{'h'} = $conllu_index+1;
				$hr->{'t'} = 'mark';   # following Irish: "X a chur", etc.
			}
			else {
				$hr->{'h'} = $conllu_index+1;
				$hr->{'t'} = 'case';
			}
		}
		elsif ($hr->{'p'} eq 'ADV') {
			if ($hr->{'s'} eq 'cha' and $i < $len-2 and $aref->[$i+1]->{'p'} eq 'ADJ' and $aref->[$i+2]->{'s'} eq 'as') {  # cha boght as X
				$hr->{'h'} = $conllu_index+1;
				$aref->[$i+2]->{'p'} = 'ADP';  # as is, weirdly, ADP here
			}
			$hr->{'t'} = 'advmod';
		}
		elsif ($hr->{'p'} eq 'CCONJ') {  # head of "as" is following conjunct
			$hr->{'t'} = 'cc';
			$hr->{'h'} = $conllu_index+1;
		}
		elsif ($hr->{'p'} eq 'DET') {
			if ($hr->{'s'} =~ m/^chooilley$/ and $i>0 and $aref->[$i-1]->{'s'} eq 'dy') {
				$hr->{'t'} = 'fixed';
				$hr->{'h'} = $conllu_index-1;
			}
			else {
				$hr->{'t'} = 'det';
				if ($hr->{'w'} =~ m/^[Ss](hoh|hen)$/) {
					$hr->{'h'} = $conllu_index-1;
				}
				else {	
					$hr->{'h'} = $conllu_index+1;
				}
			}
		}
		elsif ($hr->{'p'} eq 'NOUN') {
			$lastnoun = $conllu_index;
		}
		elsif ($hr->{'p'} eq 'PART') {
			if ($aref->[$i+1]->{'p'} eq 'VERB') {
				$hr->{'h'} = $conllu_index+1;
				$hr->{'t'} = 'mark';
			}
			elsif ($aref->[$i+1]->{'p'} eq 'ADJ') {
				$hr->{'h'} = $conllu_index+1;
				$hr->{'t'} = 'mark';
				$aref->[$i+1]->{'t'} = 'advmod';
				$aref->[$i+1]->{'h'} = 0;
			}
		}
		elsif ($hr->{'p'} eq 'PRON') {
			if ($hr->{'s'} eq 'hene') {
				$hr->{'h'} = $conllu_index-1;
				$hr->{'t'} = 'nmod';
			}
			elsif ($hr->{'s'} eq 'ou' and $aref->[$i+1]->{'w'} eq 'uss') {
				# T'ou uss; have uss point back to ou as fixed
				$aref->[$i+1]->{'h'} = $conllu_index;
				$aref->[$i+1]->{'t'} = 'fixed';
			}
		}
		elsif ($hr->{'p'} eq 'PUNCT') {
			$hr->{'t'} = 'punct';
			if ($hr->{'w'} =~ m/^[)”’]$/) {
				$hr->{'h'} = $conllu_index-1;
			}
			elsif ($hr->{'w'} =~ m/^[?.!]$/) {
				$hr->{'h'} = $firstverb;
			}
			else {
				$hr->{'h'} = $conllu_index+1;
			}
		}
		elsif ($hr->{'p'} eq 'SCONJ') {  # e.g.  "tra ghow eh..."
			$hr->{'h'} = $conllu_index+1;
			$hr->{'t'} = 'mark';
		}
		elsif ($hr->{'p'} eq 'VERB') {
			$firstverb = $conllu_index if ($firstverb == -1);
			if ($aref->[$i+1]->{'p'} eq 'PRON') {
				$aref->[$i+1]->{'h'} = $conllu_index;
				$aref->[$i+1]->{'t'} = 'nsubj';
			}
		}
	} # end of i loop over words in sentence
}

sub last_resort {
	(my $aref) = @_;
	my $len = scalar(@$aref);
	for (my $i=0; $i < $len; $i++) {
		my $hr = $aref->[$i];
		$hr->{'h'} = '0' if ($hr->{'h'} eq '');
		$hr->{'t'} = 'root' if ($hr->{'t'} eq '');
	}
}

sub fix_sentence {
	(my $aref) = @_;
	for (my $i=0; $i<5; $i++) {
		one_pass($aref);
	}
	last_resort($aref);
}

sub output_sentence {
	(my $aref) = @_;
	for my $href (@$aref) {
		print "$href->{'n'}\t$href->{'w'}\t$href->{'s'}\t$href->{'p'}\t_\t_\t$href->{'h'}\t$href->{'t'}\t_\t$href->{'g'}\n";
	}
	print "\n";
}

my @sentence;

while (<STDIN>) {
	chomp;
	if (m/^#/) {
		print "$_\n";
	}
	elsif (m/^$/) {
		fix_sentence(\@sentence);
		output_sentence(\@sentence);
		@sentence = ();
	}
	else {
		(my $num, my $tok, my $stem, my $pos, my $allpos, my $ga) = split(/\t/);
		push @sentence, {'n' => $num, 'w' => $tok, 's' => $stem, 'p' => $pos, 'a' => $allpos, 'g' => $ga, 't' => '', 'h' => ''};
	}
}

exit 0;
