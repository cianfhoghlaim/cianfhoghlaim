#include "RichPoint.h"
#include <cmath>

RichPoint::RichPoint(double initialX=0.0, double initialY=0.0) : _x(initialX), _y(initialY) { }

double RichPoint::getX() const {
  return _x;
}

double RichPoint::getY() const {
  return _y;
}

void RichPoint::setX(double val) {
  _x = val;
}

void RichPoint::setY(double val) {
  _y = val;
}

void RichPoint::scale(double factor) {
  _x *= factor;
  _y *= factor;
}

double RichPoint::distance(RichPoint other) const {
  double dx = _x - other._x;
  double dy = _y - other._y;
  return sqrt(dx*dx + dy*dy);
}

void RichPoint::normalize() {
  double mag = distance(RichPoint());
  if (mag > 0) {
    scale(1.0/mag);
  }
}

RichPoint RichPoint::operator+(RichPoint other) const {
  return RichPoint(_x + other._x, _y + other._y);
}

RichPoint RichPoint::operator*(double factor) const {
  return RichPoint(_x * factor, _y * factor);
}

double RichPoint::operator*(RichPoint other) const {
  return _x * other._x + _y * other._y;
}

RichPoint operator*(double factor, RichPoint p) {
  return p * factor;
}

ostream& operator<<(ostream& out, RichPoint p) {
  out << "<" << p.getX() << "," << p.getY() << ">";
  return out;
}
