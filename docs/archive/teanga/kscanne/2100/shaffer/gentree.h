// This is from Figure 6.2 of the book, p.205
// Not actually distributed with the book source code...
// see genmain.cpp and the comments therein

// General tree node ADT
template <typename E> class GTNode {
public:
  E value();                    // Return node’s value
  bool isLeaf();                // True if node is a leaf
  GTNode* parent();             // Return parent
  GTNode* leftmostChild();      // Return first child
  GTNode* rightSibling();       // Return right sibling
  void setValue(E&);            // Set node’s value
  void insertFirst(GTNode<E>*); // Insert first child
  void insertNext(GTNode<E>*);  // Insert next sibling
  void removeFirst();           // Remove first child
  void removeNext();            // Remove right sibling
};

// General tree ADT
template <typename E> class GenTree {
public:
  void clear();            // Send all nodes to free store
  GTNode<E>* root();       // Return the root of the tree
  // Combine two subtrees
  void newroot(E&, GTNode<E>*, GTNode<E>*);
  void print();            // Print a tree
};
