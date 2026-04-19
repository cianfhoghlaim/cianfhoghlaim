#!/usr/bin/perl
use strict;
use warnings;
use utf8;
binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";
binmode STDERR, ":utf8";
use LWP::UserAgent;
use Data::Dumper;
use JSON;
use URI::Escape;
use HTML::Entities;
use Encode qw(decode);

sub wdSparqlQuery {
  my $agent = shift;
  my $query = shift;
  my $format = shift;
  my $baseURL = "https://query.wikidata.org/sparql";
  my $queryURL = "${baseURL}?query=${query}&format=${format}";
  my $ua = LWP::UserAgent -> new;
  $ua -> agent($agent);
  my $req = HTTP::Request -> new(GET => $queryURL);
  my $res = $ua -> request($req);
  my $str = $res -> content;
  return $str;
}

# set up query for Wikidata
sub getMissingDescr {
my $agent = "MyApp/0.1";
my $format = "json";
my $query = <<'END_QUERY';
SELECT DISTINCT ?item ?itemLabel ?logainmID WHERE {

  ?item wdt:P5097 ?logainmID.

  SERVICE wikibase:label { bd:serviceParam wikibase:language "ga". }
}
END_QUERY

return wdSparqlQuery($agent, $query, $format);
}

# START OF MAIN
my $data = getMissingDescr();
my $href;
if (!defined(eval { $href = from_json(decode('utf8',$data)) }) or
            !defined($href) or ref($href) ne 'HASH') {
    		#print "RESULTS with arg=$ARGV[0]: 0\n";
            print STDERR "didn't understand the response from the server\n";
}
else {
	my $aref = $href->{'results'}->{'bindings'};
	my $numres = scalar(@$aref);
	for my $hr (@$aref) {
		#print Dumper($hr)."\n";
		my $QID = $hr->{'item'}->{'value'};
		$QID =~ s/^.+\/(Q[0-9]+)$/$1/;
		my $wikidataGA = $hr->{'itemLabel'}->{'value'};
		my $logainmID = $hr->{'logainmID'}->{'value'};
		print "$QID\t$wikidataGA\t$logainmID\n";
	}
}
