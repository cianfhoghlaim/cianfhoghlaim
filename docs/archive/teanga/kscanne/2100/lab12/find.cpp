#include "Trie.h"
#include <iostream>
#include <string.h>
using namespace std;

// this implementation only tells us if the substring is there or not
// We could store indices at the *interior nodes* of the trie if
// we wanted to return the index of the first place where the substring occurs
bool findSubstring(const char* big, const char* small) {
  Trie t;
  int biglen = strlen(big);
  for (int i=0; i < biglen; i++) {
    t.insert(big+i,i);
  }
  return t.longestPrefix(small) == strlen(small);
}

void findUI(const char* b, const char* s) {
  if (findSubstring(b,s)) {
    cout << "String contains \"" << s << "\"!\n";
  }
  else {
    cout << "String does not contain \"" << s << "\"!\n";
  }
}

int main() {

  char b[1024];

  cout << "Big string to search in: ";
  cin.getline(b,sizeof(b));

  // the typical setup is that you want to search for many short strings
  // in one long string, so you can just build the trie once and then
  // search very quickly thereafter; we're not doing that here
  findUI(b, "plate");
  findUI(b, "shrimp");

  return 0;
}
