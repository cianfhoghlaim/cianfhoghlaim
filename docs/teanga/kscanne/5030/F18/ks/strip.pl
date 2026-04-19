#!/usr/bin/perl

use strict;
use warnings;
use Unicode::Normalize;

binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";

my $dbpath = '../data';
my $testpath = '../tests';
my %db;

sub load_stopwords {
  (my $language) = @_;
  open(STOPWORDS, "<:utf8", "$dbpath/$language.txt") or return;
  while (<STOPWORDS>) {
    chomp;
    $db{$language}->{NFC($_)}=1;
  }
  close STOPWORDS;
}

sub strip_stopwords {
  (my $language, my $string) = @_;
  load_stopwords($language) unless (exists($db{$language}));
  return undef unless (exists($db{$language}));
  $string =~ s/^ +//;
  return join(' ', grep {!exists($db{$language}->{NFC($_)}) and !exists($db{$language}->{lc(NFC($_))})} split(/ +/,$string));
}

open(TESTS, "<:utf8", "$testpath/cases.tsv") or die "Could not open cases.tsv: $!";
while (<TESTS>) {
  chomp;
  (my $testlang, my $testin, my $testout) = split(/\t/);
  my $result = strip_stopwords($testlang,$testin);
  next unless defined $result;
  print "Test on line $. failed; expected \"$testout\", got \"$result\"\n" unless $result eq $testout;
}
close TESTS;

exit 0;
