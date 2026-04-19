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
use Encode qw(decode);
use URI::Escape;

sub wdSparqlQuery {
  my $agent = shift;
  my $query = shift;
  my $format = shift;
  $query = uri_escape($query);
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
SELECT DISTINCT ?item ?articlename ?itemLabel ?itemDescription ?bday  WHERE {
  {
      ?item p:P31 ?statement0.
      ?statement0 (ps:P31) wd:Q5.
      ?item p:P569 ?statement_1.
      ?statement_1 psv:P569 ?statementValue_1.
      ?statementValue_1 wikibase:timePrecision ?precision_1.
      hint:Prior hint:rangeSafe "true"^^xsd:boolean.
      FILTER(?precision_1 = 11 )
      ?statementValue_1 wikibase:timeValue ?bday.
      hint:Prior hint:rangeSafe "true"^^xsd:boolean.
      FILTER(("+BLIAIN-00-00T00:00:00Z"^^xsd:dateTime <= ?bday))
      FILTER((?bday < "+PLUSONE-00-00T00:00:00Z"^^xsd:dateTime))
      ?item ^schema:about ?article .
      ?article schema:isPartOf <https://ga.wikipedia.org/>;
      schema:name ?articlename .
      SERVICE wikibase:label
      {
       bd:serviceParam wikibase:language "ga,mul" .
       ?item rdfs:label ?itemLabel .
       ?item schema:description ?itemDescription .
      }
  }
}
END_QUERY

my $yr = $ARGV[0];
$query =~ s/BLIAIN/$yr/;
my $nextyr = $yr+1;
$query =~ s/PLUSONE/$nextyr/;
my $cineal = $ARGV[1];  # 'breith' nó 'bas'
if ($cineal eq 'breith') {
	1;
}
elsif ($cineal eq 'bas') {
	$query =~ s/P569/P570/g;
}
else {
	die "Error!\n";
}

#print "QUERY:\n";
#print $query;

return wdSparqlQuery($agent, $query, $format);
}

# START OF MAIN
my $data = getMissingDescr();
#print Dumper($data);
#exit 0;
my %counts;    # keys are qids
my %alloutput; # keys are qids
my $href;
if (!defined(eval { $href = from_json(decode('utf8',$data)) }) or
            !defined($href) or ref($href) ne 'HASH') {
            print STDERR "ARG=$ARGV[0]; didn't understand the response from the server\n";
}
else {
	my $aref = $href->{'results'}->{'bindings'};
	my $num = scalar(@$aref);
	#print "$num results found...\n";
	for my $hr (@$aref) {
		my $QID = $hr->{'item'}->{'value'};
		$QID =~ s/^.+\/(Q[0-9]+)$/$1/;
		my $ga_label = 'NONE';
		$ga_label = $hr->{'itemLabel'}->{'value'} if (exists($hr->{'itemLabel'}));
		my $ga_description = 'NONE';
		$ga_description = $hr->{'itemDescription'}->{'value'} if (exists($hr->{'itemDescription'}));
		$ga_description =~ s/ *[(].*$//;
		my $ga_article_name = $hr->{'articlename'}->{'value'};
		my $bday = $hr->{'bday'}->{'value'};
		$bday =~ s/T.*//;
		if (exists($counts{$QID})) {
			$counts{$QID}++;
		}
		else {
			$counts{$QID} = 1;
		}
		$alloutput{$QID} = "$bday\t$QID\t$ga_article_name\t$ga_label\t$ga_description\n";
	}
}

for my $k (keys %alloutput) {
	print $alloutput{$k} if ($counts{$k}==1);
}
