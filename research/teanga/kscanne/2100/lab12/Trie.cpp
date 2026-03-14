#include "Trie.h"

Trie::Trie() {
  root = new TrieNode();
}

Trie::~Trie() {
  delete root;
}

void Trie::insert(const char* s, int v) {
  root->insert(s,v);
}

int Trie::lookup(const char* s) const {
  return root->lookup(s);
}

int Trie::longestPrefix(const char* s) const {
  return root->longestPrefix(s);
}

int Trie::totalSize() const {
  return root->totalSize();
}
