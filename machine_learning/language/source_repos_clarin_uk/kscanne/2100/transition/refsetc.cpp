#include "RichPoint.h"
#include <iostream>
using namespace std;

// void printScaled(RichPoint* p) {
// void printScaled(const RichPoint& p) {
// void printScaled(RichPoint& p) {
void printScaled(RichPoint p) {
  p.scale(1.0/p.distance(RichPoint(0,0)));
  cout << p << endl;
}

int main() {

  RichPoint p(0,0);
  RichPoint q(1,1);
  RichPoint r(2,2);
  cout << "p = " << p << endl;
  cout << "q = " << q << endl;
  cout << "r = " << r << endl;

  RichPoint* pptr = &p;
  RichPoint* qptr = &q;
  RichPoint* rptr = &r;
  cout << "pptr = " << pptr << endl;
  cout << "qptr = " << qptr << endl;
  cout << "rptr = " << rptr << endl;

  RichPoint& pref = p;
  RichPoint& qref = q;
  RichPoint& rref = r;
  cout << "pref = " << pref << endl;
  cout << "qref = " << qref << endl;
  cout << "rref = " << rref << endl;

  cout << "and now bitwise copy q to p" << endl;
  p = q;
  cout << "p = " << p << endl;
  cout << "q = " << q << endl;
  cout << "pptr = " << &p << endl;
  cout << "qptr = " << &q << endl;

  cout << "and now copy via reference, not like Python!" << endl;
  qref = rref;
  cout << "q = " << q << endl;
  cout << "r = " << r << endl;
  cout << "qref = " << qref << endl;
  cout << "rref = " << rref << endl;
  cout << "qptr = " << &q << endl;
  cout << "rptr = " << &r << endl;

  cout << "p, scaled to unit length: ";
  printScaled(p);
  cout << "original p= " << p << endl;
}
