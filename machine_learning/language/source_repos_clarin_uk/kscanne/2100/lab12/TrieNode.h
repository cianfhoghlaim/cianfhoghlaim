#ifndef _TRIENODE_
#define _TRIENODE_

class TrieNode {

private:

  int val;
  TrieNode** fol;

public:

  TrieNode();
  TrieNode(int v);
 ~TrieNode();
  void insert(const char* s, int v);
  int lookup(const char* s) const;
  int longestPrefix(const char* s) const;
  int totalSize() const;
};

#endif
