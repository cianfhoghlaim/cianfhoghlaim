#!/usr/bin/perl

# for training only;
# this requires three text files
# connacht.txt, mumhain.txt and ulaidh.txt
# in this directory (not provided in repository),
# one sentence per line

use strict;
use warnings;
use utf8;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %words;
sub word_count
{
	(my $file) = @_;
	return $words{$file} if (exists($words{$file}));
	open(CORPUS, "<:utf8", "$file.txt") or die "Could not open corpus file $file.txt: $!";
	my $count = 0;
	while (<CORPUS>) {
		while (m/(\p{L}|[ʼ’'-])+/g) {
			$count++;
		}
	}
	close CORPUS;
	$words{$file} = $count;
}

# computes logprob of the feature in the given training corpus (M, U, or C)
# assumes sentence segmented so that trigrams are on one line
sub logprob
{
	(my $file, my $feature_re, my $universe_re) = @_;
	open(CORPUS, "<:utf8", "$file.txt") or die "Could not open corpus file $file.txt: $!";
	my $count = 0;
	my $total = 0;
	while (<CORPUS>) {
		while (m/$feature_re/g) {
			$count++;
		}
		#while (m/$universe_re/g) { $total++; }
	}
	close CORPUS;
	return log($count + 0.2) - log(word_count($file));
}

# usually just pipe features.txt through this
# but can also incrementally train with single words by saying:
# echo "neómat" | perl train.pl >> model.txt
while (<STDIN>) {
	chomp;
	next if (m/^#/);
	if (m/\t/) {
		(my $feature, my $universe) = m/^(.+)\t(.+)$/;
		my $featureout = $feature;
		$feature =~ s/^/(^| )/;
		$featureout =~ s/^/^/; # in model file, want to match start of trigram
		$universe =~ s/^/(^| )/;
		my $feature_re = qr/$feature/i;
		my $universe_re = qr/$universe/i;
		printf("%s\t%.3f\t%.3f\t%.3f\n", $featureout, logprob('connacht', $feature_re, $universe_re), logprob('mumhain', $feature_re, $universe_re), logprob('ulaidh', $feature_re, $universe_re));
	}
	else {
		my $feature = $_;
		my $featureout = $feature;
		$feature =~ s/^/(^| )/;
		$feature =~ s/$/(\$|[^A-Za-zÁÉÍÓÚáéíóú'-])/;
		$featureout =~ s/^/^/; # in model file, want to match start of trigram
		$featureout =~ s/$/[ ]/;
		my $feature_re = qr/$feature/i;
		printf("%s\t%.3f\t%.3f\t%.3f\n", $featureout, logprob('connacht', $feature_re, ''), logprob('mumhain', $feature_re, ''), logprob('ulaidh', $feature_re, ''));
	}
}

exit 0;
