#!/usr/bin/perl
# makes best guess at correct stem; flags OOV words and ambiguous words

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %focloir;
open(FOC, "<:utf8", "tagdict.tsv") or die "Could not open tagdict.tsv: $!";
while (<FOC>) {
	chomp;
	(my $tok, my $stem, my $pos) = split(/\t/);
	my @cands = split(/\|/, $stem);
	for my $s (@cands) {
		$focloir{"$tok|$pos"}->{$s} = 1;
	}
}
close FOC;

# strategy is to score all candidates with this function and
# keep the one with the best (highest) score
sub stem_score {
	(my $token, my $stem) = @_;
	my $ans = 0;
	$ans += 10000 if (($token eq 'cheayn' and $stem eq 'keayn') or
						($token eq 'gleaysh' and $stem eq 'cleaysh') or
						($token eq 'greiney' and $stem eq 'grian') or
						($token eq 'hee' and $stem eq 'faik') or
						($token eq 'hie' and $stem eq 'thie') or
						($token eq 'vac' and $stem eq 'mac') or
						($token eq 'vee' and $stem eq 'mee'));
	$ans += 1000 if ($token eq $stem);
	(my $tok_initial) = $token =~ m/^(.)/;
	(my $stem_initial) = $stem =~ m/^(.)/;
	$ans += 100 if ($tok_initial eq $stem_initial);
	my $lendiff = abs(length($token) - length($stem));
	$ans -= 10*$lendiff;
	my $realdiff = length($token) - length($stem);
	$ans -= $realdiff;
	$ans -= 1 if ($tok_initial =~ m/[Bb]/ and $stem_initial =~ m/[Pp]/);
	$ans -= 1 if ($tok_initial =~ m/[Vv]/ and $stem_initial !~ m/[Bb]/); #b>m,f
	$ans -= 1 if ($tok_initial =~ m/[Yy]/ and $stem_initial !~ m/[Jj]/); #j>g
	return $ans;
}

# best guess stem with no context; just know POS and list of candidates
sub guess_stem {
	(my $w, my $pos) = @_;
	my $key = "$w|$pos";
	my $ans;
	return $w if ($pos =~ m/^(PUNCT|SYM|X)$/ or $w =~ m/^[0-9,.]+$/);
	if (exists($focloir{$key})) {
		my @sorted = sort { stem_score($w,$b) <=> stem_score($w,$a) } keys %{$focloir{$key}};
		$ans = $sorted[0];
		$ans .= '(?)' if (scalar(@sorted) > 1);
	}
	else {
		my $lckey = lc($w)."|$pos";
		if (exists($focloir{$lckey})) {
			my @sorted = sort { stem_score($w,$b) <=> stem_score($w,$a) } keys %{$focloir{$lckey}};
			$ans = $sorted[0];
			$ans .= '(?)' if (scalar(@sorted) > 1);
		}
		else {
			$ans = $w.'(!)';
		}
	}
	return $ans;
}

sub fix_sentence {
	(my $aref) = @_;
	my $len = scalar(@$aref);
	for (my $i=0; $i < $len; $i++) {
		my $hr = $aref->[$i];
		if ($hr->{'n'} =~ m/-/) {
			$hr->{'s'} = '_';
		}
		else {
			$hr->{'s'} = guess_stem($hr->{'w'}, $hr->{'p'});
		}
	}
}

sub output_sentence {
	(my $aref) = @_;
	for my $href (@$aref) {
		print "$href->{'n'}\t$href->{'w'}\t$href->{'s'}\t$href->{'p'}\t$href->{'a'}\t$href->{'g'}\n";
	}
	print "\n";
}

my @sentence;

# pipe in edit.tsv AFTER POS tags have been corrected/checked
# and adds a column with my best guess stem
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
		(my $num, my $tok, my $pos, my $allpos, my $ga) = split(/\t/);
		# key 's' will store the answer
		push @sentence, {'n' => $num, 'w' => $tok, 'p' => $pos, 'a' => $allpos, 'g' => $ga, 's' => ''};
	}
}

exit 0;
