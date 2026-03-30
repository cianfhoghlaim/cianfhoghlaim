#include "Trie.h"
#include <iostream>
#include <fstream>
using namespace std;

int main() {

  Trie t;
  ifstream i("freq.txt");
  char s[128];
  int count;
  while (!i.eof()) {
    i >> s >> count;
    t.insert(s,count);
  }

  cout << "Total size = " << t.totalSize() << "\n";

  while (1) {
    cout << "Search: ";
    cin >> s; 
    int ans = t.lookup(s);
    if (ans == -1) {
      cout << "Not found.\n";
    }
    else {
      cout << "Found, with count " << ans << "\n";
    }
  }

  return 0;

}
