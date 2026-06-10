#!/usr/bin/perl
#   Called only from the .sh script, not directly...

use strict;
use warnings;
use utf8;
use POSIX 'strftime';
my $inniu = strftime '%Y-%m-%d', localtime;

binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my %surface;
open(CONTAE, "<:utf8", "../wikidata/contaetha.tsv") or die "Could not open county db: $!";
while (<CONTAE>) {
	chomp;
	my @pieces = split(/\t/);
	$surface{$pieces[2]} = $pieces[1];
}
close CONTAE;

# aref looks like ['contae','Maigh Eo','barúntacht','Iorras',...]
sub disambiguator {
	(my $aref, my $lvl) = @_;
	my $len = scalar(@$aref);
	# note we loop by twos!
	for (my $i=0; $i < $len; $i += 2) {
		my $s = $aref->[$i];
		next if ($s eq 'contae');
		if ($lvl == 1) {
			return $aref->[$i+1];
		}
		else {
			$lvl--;
		}
	}
	return 'FAIL: '.join(' ',@$aref);
}

sub county {
	(my $aref) = @_;
	my $ans='';
	if (scalar(@$aref)>1 and $aref->[0] eq 'contae') {
		my $county = $aref->[1];
		$ans = $county;
	}
	return $ans;
}

sub pagetitle {
	(my $ainm, my $t, my $aref, my $level) = @_;
	my $ans = $ainm;
	my $c = county($aref);
	$ans .= ", $surface{$c}" if ($c ne '');
	return $ans if ($level==0);
	my $dis = disambiguator($aref, $level);
	if ($dis =~ m/^FAIL/ and $t eq 'toghroinn') {
		$dis = 'toghroinn';
	}
	$ans .= " ($dis)";
	return $ans;
}

sub description {
	(my $ainm, my $t, my $aref, my $level) = @_;
	if ($t =~ m/,.*,/) {
		$t =~ s/, ([^,]+)$/, agus $1/;
	}
	elsif ($t =~ m/,/) {
		$t =~ s/, / agus /;
	}
	my $ans = $t;
	my $c = county($aref);
	$ans .= " i g[[$surface{$c}]]" if (exists($surface{$c}));
	return $ans if ($level==0);
	#$ans .= '('.join(' ', @$aref).')';
	return $ans;
}

my @input;
# pipe in the output of ambig2wiki.sh...
while (<STDIN>) {
	chomp;
	push @input, $_;
}

my $tot = scalar(@input);

my @pagetitles;
my @descriptions;
my @logainmids;
my @levels;
for (my $i=0; $i < $tot; $i++) {
	push @levels, 0;
}
my $continue_p=1;
while ($continue_p) {
	for (my $i=0; $i < $tot; $i++) {
		my @pieces = split(/\t/, $input[$i]);
		$logainmids[$i] = shift(@pieces);
		my $ainm = shift(@pieces);
		my $cinealacha = shift(@pieces);
		$pagetitles[$i] = pagetitle($ainm,$cinealacha,\@pieces,$levels[$i]);
		$descriptions[$i] = description($ainm,$cinealacha,\@pieces,$levels[$i]);
	}
	$continue_p = 0;
	my %titled;
	for (my $i=0; $i < $tot; $i++) {
		if (exists($titled{$pagetitles[$i]})) {
			$titled{$pagetitles[$i]}++;
		}
		else {
			$titled{$pagetitles[$i]} = 1;
		}
	}
	for (my $i=0; $i < $tot; $i++) {
		if ($titled{$pagetitles[$i]}>1 and $levels[$i]<5) {
			$levels[$i]++;
			$continue_p = 1;
		}
	}
}


for (my $i=0; $i < $tot; $i++) {
	print "* [[$pagetitles[$i]]]: $descriptions[$i]<ref>{{Lua idirlín|url=https://www.logainm.ie/ga/$logainmids[$i]|teideal=Bunachar Logainmneacha na hÉireann|work=Logainm.ie|dátarochtana=$inniu}}</ref>\n";
}

exit 0;
