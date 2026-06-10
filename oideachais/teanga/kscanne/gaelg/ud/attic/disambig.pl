#!/usr/bin/perl
# Ugly rule-based POS disambiguation for bootstrapping the
# initial version of the corpus 

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

sub one_pass {
	(my $aref) = @_;
	my $len = scalar(@$aref);
	for (my $i=0; $i < $len; $i++) {
		my $hr = $aref->[$i];
		next if ($hr->{'t'} ne '');
		$hr->{'t'} = $hr->{'p'} if ($hr->{'n'} =~ m/-/); # multiword token
		$hr->{'t'} = $hr->{'p'} unless ($hr->{'p'} =~ m/\|/); # UNAMBIG easy
		$hr->{'t'} = 'CCONJ' if ($hr->{'w'} =~ m/^[Aa]gh$/);
		$hr->{'t'} = 'NOUN' if ($hr->{'w'} =~ m/^[Aa]rgid$/);
		$hr->{'t'} = 'ADJ' if ($hr->{'w'} =~ m/^[Aa]rd$/);
		$hr->{'t'} = 'CCONJ' if ($hr->{'w'} =~ m/^[Aa]s$/);
		$hr->{'t'} = 'ADP' if ($hr->{'w'} =~ m/^[Aa]yn$/);
		$hr->{'t'} = 'NOUN' if ($hr->{'w'} =~ m/^[Bb]ee$/ and $hr->{'g'} =~ m/^[Bb]h?ia$/);
		$hr->{'t'} = 'VERB' if ($hr->{'w'} =~ m/^[Bb]ee$/ and $hr->{'t'} eq '');
		$hr->{'t'} = 'ADV' if ($hr->{'w'} =~ m/^[Cc]ha$/ and $hr->{'g'} =~ m/^[Cc]homh?( |$)/);
		$hr->{'t'} = 'PART' if ($hr->{'w'} =~ m/^[Cc]ha$/ and $hr->{'t'} eq '');
		$hr->{'t'} = 'VERB' if ($hr->{'w'} =~ m/^[Cc]h?ur$/ and $hr->{'g'} =~ m/^([Cc]h?uir|[Tt]abhair|[Tt]hug)$/);
		$hr->{'t'} = 'NOUN' if ($hr->{'w'} =~ m/^[Cc]h?ur$/ and $hr->{'t'} eq '');
		$hr->{'t'} = 'ADP' if ($hr->{'w'} =~ m/^[Cc]ordail$/ and $aref->[$i+1]->{'w'} =~ m/^rish$/i);
		$hr->{'t'} = 'NOUN' if ($hr->{'w'} =~ m/^[Dd]einey$/);
		$hr->{'t'} = 'ADP' if ($hr->{'w'} =~ m/^[Dd]ooin$/);
		$hr->{'t'} = 'ADJ' if ($hr->{'w'} =~ m/^[Dd]rogh$/);
		$hr->{'t'} = 'PART' if ($hr->{'w'} =~ m/^[Dd]y$/ and $hr->{'g'} =~ m/^(go|gur)/i);
		$hr->{'t'} = 'PART' if ($hr->{'w'} =~ m/^[Dd]y$/ and $aref->[$i+1]->{'p'} eq 'VERB');
		$hr->{'t'} = 'PART' if ($hr->{'w'} =~ m/^[Dd]y$/ and $aref->[$i+1]->{'w'} =~ m/^liooar$/i);
		$hr->{'t'} = 'DET' if ($hr->{'w'} =~ m/^[Dd]y$/ and $aref->[$i+1]->{'w'} =~ m/^chooilley$/i);  # cf "a h-uile" in gd; DET/DET fixed
		$hr->{'t'} = 'ADP' if ($hr->{'w'} =~ m/^[Dd]y$/ and $hr->{'t'} eq '');
		$hr->{'t'} = 'PRON' if ($hr->{'w'} =~ m/^[Ee][eh]$/);
		$hr->{'t'} = 'ADP' if ($hr->{'w'} =~ m/^[Ee]r$/);
		$hr->{'t'} = 'ADJ' if ($hr->{'w'} =~ m/^[Ee]rbee$/);
		$hr->{'t'} = 'ADP' if ($hr->{'w'} =~ m/^[Ee]u$/);
		$hr->{'t'} = 'ADV' if ($hr->{'w'} =~ m/^[Ff]eer$/);
		$hr->{'t'} = 'VERB' if ($hr->{'w'} =~ m/^[Gg]how$/);
		$hr->{'t'} = 'VERB' if ($hr->{'w'} =~ m/^[Hh]ug$/);
		$hr->{'t'} = 'ADP' if ($hr->{'w'} =~ m/^[Jj]eu$/);
		$hr->{'t'} = 'ADV' if ($hr->{'w'} =~ m/^[Jj]iu$/);
		$hr->{'t'} = 'NOUN' if ($hr->{'w'} =~ m/^[Ll]aa$/);
		$hr->{'t'} = 'ADV' if ($hr->{'w'} =~ m/^[Mm]agh$/);
		$hr->{'t'} = 'ADV' if ($hr->{'w'} =~ m/^[Mm]airagh$/);
		$hr->{'t'} = 'PRON' if ($hr->{'w'} =~ m/^[Mm]ee$/);
		$hr->{'t'} = 'ADJ' if ($hr->{'w'} =~ m/^[MmVv]ie$/);
		$hr->{'t'} = 'SCONJ' if ($hr->{'w'} =~ m/^[Mm]y$/ and $hr->{'g'} =~ m/^[Mm]ás?( |$)/);
		$hr->{'t'} = 'DET' if ($hr->{'w'} =~ m/^[Mm]y$/ and $hr->{'t'} eq '');
		$hr->{'t'} = 'SCONJ' if ($hr->{'w'} =~ m/^[Mm]yr$/ and $aref->[$i+1]->{'p'} =~ m/VERB/);
		$hr->{'t'} = 'ADP' if ($hr->{'w'} =~ m/^[Mm]yr$/ and $hr->{'t'} eq '');
		$hr->{'t'} = 'PART' if ($hr->{'w'} =~ m/^[Nn]agh$/);
		$hr->{'t'} = 'VERB' if ($hr->{'w'} =~ m/^[Nn]ee$/);
		$hr->{'t'} = 'PART' if ($hr->{'w'} =~ m/^[Nn]y$/ and $hr->{'g'} =~ m/^[Nn]íos( |$)/);
		# although some of these could be imperatives 'Ná habair' (PART)
		$hr->{'t'} = 'CCONJ' if ($hr->{'w'} =~ m/^[Nn]y$/ and $hr->{'g'} =~ m/^[Nn][áó]( |$)/);
		$hr->{'t'} = 'DET' if ($hr->{'w'} =~ m/^[Nn]y$/ and $hr->{'t'} eq '');
		$hr->{'t'} = 'ADP' if ($hr->{'w'} =~ m/^[Oo]rt$/);
		$hr->{'t'} = 'PRON' if ($hr->{'w'} =~ m/^[Oo]u$/);
		$hr->{'t'} = 'NOUN' if ($hr->{'w'} =~ m/^[Rr]aad$/);
		$hr->{'t'} = 'ADP' if ($hr->{'w'} =~ m/^[Rr]ee$/ and $hr->{'g'} =~ m/^[Ll]éi$/);
		$hr->{'t'} = 'NOUN' if ($hr->{'w'} =~ m/^[Rr]ee$/ and $hr->{'t'} eq '');
		$hr->{'t'} = 'VERB' if ($hr->{'w'} =~ m/^Roie$/ and $hr->{'g'} =~ m/^Rith/);
		$hr->{'t'} = 'ADV' if ($hr->{'w'} =~ m/^[Rr]oie$/ and $hr->{'g'} =~ m/^[Rr]oimhe/);
		$hr->{'t'} = 'NOUN' if ($hr->{'w'} =~ m/^[Rr]oie$/ and $hr->{'t'} eq '');
		$hr->{'t'} = 'ADJ' if ($hr->{'w'} =~ m/^[Ss]hare$/);
		$hr->{'t'} = 'ADV' if ($hr->{'w'} =~ m/^[Ss]heese$/);
		$hr->{'t'} = 'DET' if ($hr->{'w'} =~ m/^[Ss]h(en|oh)$/ and $i>1 and $aref->[$i-2]->{'w'} =~ m/^(yn?|ny|'n)$/i);
		$hr->{'t'} = 'PRON' if ($hr->{'w'} =~ m/^[Ss]h(en|oh)$/ and $hr->{'t'} eq '');
		$hr->{'t'} = 'PRON' if ($hr->{'w'} =~ m/^[Ss]hin$/);
		$hr->{'t'} = 'ADV' if ($hr->{'w'} =~ m/^[Ss]tiagh$/);
		$hr->{'t'} = 'NOUN' if ($hr->{'w'} =~ m/^[Tt]hie$/);
		$hr->{'t'} = 'SCONJ' if ($hr->{'w'} =~ m/^[Tt]ra$/);
		$hr->{'t'} = 'VERB' if ($hr->{'w'} =~ m/^[Vv]a$/);
		$hr->{'t'} = 'VERB' if ($hr->{'w'} =~ m/^[Vv]er$/);
		$hr->{'t'} = 'ADP' if ($hr->{'w'} =~ m/^[Vv]eih$/);
		$hr->{'t'} = 'ADP' if ($hr->{'w'} =~ m/^y$/ and $hr->{'g'} eq 'a');
		$hr->{'t'} = 'DET' if ($hr->{'w'} =~ m/^[Yy]$/ and $hr->{'t'} eq '');

		$hr->{'t'} = 'NOUN' if ($hr->{'w'} =~ m/^[Hh]ie$/ and $i>0 and $aref->[$i-1]->{'t'} =~ m/^(DET|INTJ)$/);
		$hr->{'t'} = 'VERB' if ($hr->{'w'} =~ m/^[Hh]ie$/ and $hr->{'t'} eq '');


		# based on context, not specific token
		$hr->{'t'} = 'NOUN' if ($hr->{'p'} =~ m/NOUN/ and $i>0 and $aref->[$i-1]->{'w'} =~ m/^([Yy]n?|[Nn]y)$/);
		$hr->{'t'} = 'PROPN' if ($hr->{'p'} =~ m/PROPN/ and $i>0 and $aref->[$i-1]->{'w'} =~ m/^([Yy]n?|[Nn]y)$/);
	}
}

sub tag_unigram {
	(my $href) = @_;
	return if ($href->{'t'} ne '');
	my @in_order = qw(NOUN ADP DET VERB PRON ADJ PROPN CCONJ PART ADV SCONJ);
	for my $t (@in_order) {
		if ($href->{'p'} =~ m/$t/) {
			$href->{'t'} = $t;
			last;
		}
	}
}

sub last_resort {
	(my $aref) = @_;
	my $len = scalar(@$aref);
	for (my $i=0; $i < $len; $i++) {
		my $hr = $aref->[$i];
		$hr->{'t'} = 'NUM' if ($hr->{'t'} eq '' and $hr->{'p'} =~ m/NUM/);
		tag_unigram($hr);
		$hr->{'t'} = $hr->{'p'} if ($hr->{'t'} eq '');  # no-op I hope
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
		print "$href->{'n'}\t$href->{'w'}\t$href->{'t'}\t$href->{'p'}\t$href->{'g'}\n";
	}
	print "\n";
}

my @sentence;

# pipe in draft.tsv
# and adds a column with my best guess disambiguated POS tag
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
		(my $num, my $tok, my $pos, my $ga) = split(/\t/);
		# key 't' will store the answer
		push @sentence, {'n' => $num, 'w' => $tok, 'p' => $pos, 'g' => $ga, 't' => ''};
	}
}

exit 0;
