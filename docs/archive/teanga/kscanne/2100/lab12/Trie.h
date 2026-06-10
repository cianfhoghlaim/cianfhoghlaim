#ifndef _TRIE_
#define _TRIE_

#include "TrieNode.h"

class Trie {

private:
  
  TrieNode* root;

public:

  Trie();
 ~Trie();
  void insert(const char* s, int v);
  int lookup(const char* s) const;
  int longestPrefix(const char* s) const;
  int totalSize() const;

};

#endif
