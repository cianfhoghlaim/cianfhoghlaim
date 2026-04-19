#include "LabeledPoint.h"

LabeledPoint::LabeledPoint(double initialX, double initialY) : RichPoint(initialX, initialY), label() {
}

LabeledPoint::LabeledPoint(double initialX, double initialY, const char* name) : RichPoint(initialX, initialY), label(name) {
}

LabeledPoint::LabeledPoint(double initialX, double initialY, mystring name) : RichPoint(initialX, initialY), label(name) {
}

mystring LabeledPoint::getLabel() const {
  return label;
}

ostream& operator<<(ostream& out, LabeledPoint p) {
  out << (RichPoint) p << " (" << p.getLabel() << ")";
  return out;
}
