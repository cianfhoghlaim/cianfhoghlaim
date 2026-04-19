#include "TrieNode.h"
#include <string.h>
#include <iostream>
using namespace std;
// A-Z are 0...25, 26=punctuation, space, etc., 27 = $ (end of word)
#define ALPHABET_SIZE 28

int getIndex(char c) {
  int ans=(int) (c-'A');
  if (ans>=32) ans-=32;
  if (ans < 0 || ans >= ALPHABET_SIZE-1)
    ans=ALPHABET_SIZE-2;
  return ans;
}

TrieNode::TrieNode() {
  fol = new TrieNode*[ALPHABET_SIZE];
  for (int i=0; i < ALPHABET_SIZE; i++)
    fol[i] = 0;
  val = 0;
}

TrieNode::TrieNode(int v) {
  fol = 0;  
  val = v;
}

TrieNode::~TrieNode() {
  if (fol != 0) {
    for (int i=0; i < ALPHABET_SIZE; i++)
      if (fol[i] != 0) {
        delete fol[i];
      }
    delete fol;
  }
}

int TrieNode::totalSize() const {
  int ans = sizeof(int) + sizeof(TrieNode**);
  if (fol != 0) {
    ans += ALPHABET_SIZE*sizeof(TrieNode*);
    for (int i=0; i < ALPHABET_SIZE; i++)
      if (fol[i] != 0) {
        ans += fol[i]->totalSize();
      }
  }
  return ans;
}

// return the length of the longest prefix of s that appears 
// in the trie starting at this node
int TrieNode::longestPrefix(const char* s) const {
  if (strlen(s)==0) {
    return 0;
  }
  else {
    int index=getIndex(s[0]);
    if (fol[index]==0) {
      return 0;
    }
    else {
      return 1+fol[index]->longestPrefix(s+1);
    }
  }
}

void TrieNode::insert(const char* s, int v) {
  if (strlen(s)==0) {
    if (fol[ALPHABET_SIZE-1]==0) {
      fol[ALPHABET_SIZE-1] = new TrieNode(v);
    }
    else {
      fol[ALPHABET_SIZE-1]->val = v;
    }
  }
  else {
    int index=getIndex(s[0]);
    if (fol[index]==0) {
      fol[index] = new TrieNode();
    }
    fol[index]->insert(s+1,v);
  }
}

int TrieNode::lookup(const char* s) const {
  if (strlen(s)==0) {
    if (fol[ALPHABET_SIZE-1]==0) {
      return -1;
    }
    else {
      return fol[ALPHABET_SIZE-1]->val;
    }
  }
  else {
    int index=getIndex(s[0]);
    if (fol[index]==0) {
      return -1;
    }
    else {
      return fol[index]->lookup(s+1);
    }
  }
}
