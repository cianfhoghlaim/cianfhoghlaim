#include "Point.h"

Point::Point() {
  _x = 0;
  _y = 0;
}

double Point::getX() const {
  return _x;
}

double Point::getY() const {
  return _y;
}

void Point::setX(double val) {
  _x = val;
}

void Point::setY(double val) {
  _y = val;
}
