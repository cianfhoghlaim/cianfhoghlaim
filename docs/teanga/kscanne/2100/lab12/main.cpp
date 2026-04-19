#include "Trie.h"
#include <iostream>
using namespace std;

int main() {

  Trie t;
  t.insert("A", 481903);
  t.insert("AS", 161478);
  t.insert("ASK", 564);
  t.insert("AT", 105071);
  t.insert("ATE", 150);
  t.insert("BE", 67825);
  t.insert("BEE", 56);
  t.insert("BEEN", 39892);
  t.insert("BEET", 7);

  cout << "Total size = " << t.totalSize() << "\n";

  char s[128];

  while (1) {
    cout << "Search: ";
    cin >> s; 
    int ans = t.lookup(s);
    if (ans == -1) {
      cout << "Not found, longest prefix = " << t.longestPrefix(s) << "\n";
    }
    else {
      cout << "Found, with count " << ans << "\n";
    }
  }

  return 0;

}
