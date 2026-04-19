#!/usr/bin/perl

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";


# reads in the output of Intergaelic, **ideally on plain text 
# with one sentence per line!!**
# Ta shin => Táimid
# ooilley => uile
# ginsh => ag insint
# skeealyn => scéalta
# , => ,
# reddyn => rudaí
# ta shin => atáimid
# 
# And then outputs a "POS-tagged" file (no disambiguation - see disambig.pl)
# but with extra info (full set of possible tags and Irish translation)
# which hopefully aids manually correction/completion

# keys are words, vals are hashes with tags as keys
my %tags;

open(DICT, "<:utf8", "tagdict.tsv") or die "Could not open tagdict.tsv: $!";
while (<DICT>) {
	chomp;
	# ignoring stems in the tagdict.tsv file at this stage
	(my $f, my $stemlists, my $tag) = split(/\t/);
	$tags{$f}->{$tag} = 1;
}
close DICT;

my %mwt;
open(MWT, "<:utf8", "mwtokens.tsv") or die "Could not open mwtokens.tsv: $!";
while (<MWT>) {
	chomp;
	next if (m/^#/);
	(my $tok, my $repl) = split(/\t/);
	my @repl_list = split(/ /,$repl);
	print STDERR "Warning: multiple replacements for mwt $tok\n" if (exists($mwt{$tok}));
	$mwt{$tok} = \@repl_list;
}
close MWT;

sub lookup {
	(my $w) = @_;
	return join('|',sort keys %{$tags{$w}}) if (exists($tags{$w}));
	return join('|',sort keys %{$tags{lc($w)}}) if (exists($tags{lc($w)}));
	return 'PUNCT' if (length($w)==1 and $w =~ /(\p{Punct}|\p{S})/);
	return 'NUM' if ($w =~ /[0-9]/ and $w !~ /[A-Za-z]/);
	return 'PROPN' if ($w =~ /\p{Lu}/);
	return 'OOV';
}

my $batch_name='ac';
my $sent_id=0;
my $wordno = 1;
my $orig;
while (<STDIN>) {
	chomp;
	if (m/^<div text="(.+)"\/> =>/) {
		$orig = $1;
		print "# sent_id = ${batch_name}_".sprintf("%03d", $sent_id)."\n";
		print "# text = $orig\n";
	}
	elsif (m/^\\n => \\n$/) {
		print "\n";
		$wordno = 1;
		$sent_id++;
	}
	else {
		(my $lhs, my $rhs) = m/^(.+) => (.+)$/;
		my $rhsprinted=0;
		my @lhstokens = split(/ /,$lhs);
		for my $lhst (@lhstokens) {  # loop over actual surface tokens
			my @alltokens;
			if (exists($mwt{$lhst})) {
				push @alltokens, @{$mwt{$lhst}};
			}
			elsif (exists($mwt{lc($lhst)})) {
				my $capped=0;
				for my $t (@{$mwt{lc($lhst)}}) {
					if ($capped) {
						push @alltokens, $t;
					}
					else {
						push @alltokens, ucfirst($t);
						$capped=1;
					}
				}
			}
			elsif ($lhst =~ m/^((?:[BbDdMmNnSsVvTt]|[Dd]t|[Tt]h)')(.+)$/) {
				push @alltokens, $1;
				push @alltokens, $2;
			}
			elsif ($lhst =~ m/^(.+)('n)$/) {
				push @alltokens, $1;
				push @alltokens, $2;
			}
			else {
				push @alltokens, $lhst;
			}
			if (scalar(@alltokens) > 1) {
				my $range_end = $wordno + scalar(@alltokens) - 1;
				print "$wordno-$range_end\t$lhst\t_\t\n";
			}
			for my $p (@alltokens) {
				my $tokentags = lookup($p);
				print "$wordno\t$p\t$tokentags\t";
				$wordno++;
				unless ($rhsprinted) {
					print $rhs;
					$rhsprinted = 1;
				}
				print "\n";
			}
		}
	}
}

exit 0;
