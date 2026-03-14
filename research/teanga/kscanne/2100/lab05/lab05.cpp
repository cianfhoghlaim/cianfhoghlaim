#include "book.h"
#include "BSTNode.h"

// Count the number of nodes in a binary tree
template <typename E>
int count(BinNode<E>* root) {
  if (root == NULL) return 0;  // Nothing to count
  return 1 + count(root->left())
           + count(root->right());
}

template <typename E>
int height(BinNode<E>* root) {
  return 0;
}

template <typename E>
int leaf_count(BinNode<E>* root) {
  return 0;
}

template <typename E>
int sum_nodes(BinNode<E>* root) {
  return 0;
}

template <typename E>
bool search(BinNode<E>* root, const E& val) {
  return false;
}

template <typename E>
void print_tree(BinNode<E>* root) {
}

template <typename E>
void print_tree_by_level(BinNode<E>* root) {
}

int main()
{
  BSTNode<int,int>* root = new BSTNode<int,int>(1,1);
  BSTNode<int,int>* left = new BSTNode<int,int>(2,2);
  BSTNode<int,int>* right = new BSTNode<int,int>(3,3);
  left->setLeft(new BSTNode<int,int>(4,4));
  left->setRight(new BSTNode<int,int>(5,5));
  root->setLeft(left);
  root->setRight(right);
  print_tree(root);
  cout << " Node count = " << count(root) << endl;
  cout << " Height = " << height(root) << endl;
  cout << " Leaf count = " << leaf_count(root) << endl;
  cout << " Sum of node values = " << sum_nodes(root) << endl;
  for (int i=0; i <= 6; i++) {
    if (search(root, i)) {
      cout << "Found " << i << " in the tree..." << endl;
    }
    else {
      cout << "Did not find " << i << " in the tree..." << endl;
    }
  }
}
