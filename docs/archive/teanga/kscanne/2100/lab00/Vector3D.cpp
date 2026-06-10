#include "Vector3D.h"
#include <cmath>

Vector3D::Vector3D() {
  for (int i=0; i < 3; i++) {
    c[i] = 0.0;
  }
}

Vector3D::Vector3D(const Vector3D& v) {
  for (int i=0; i < 3; i++) {
    c[i] = v.c[i];
  }
}

Vector3D::Vector3D(float x, float y, float z) {
  c[0] = x;
  c[1] = y;
  c[2] = z;
}

void Vector3D::setCoordinate(int i, float val) {
  c[i] = val;
}

float Vector3D::getCoordinate(int i) {
  return c[i];
}

float Vector3D::magnitude() {
  float ans = 0.0;
  for (int i=0; i < 3; i++) {
    ans += c[i]*c[i]; 
  }
  return sqrt(ans);
}

void Vector3D::normalize(){
  float m = magnitude();
  if (m != 0.0) {
    for (int i=0; i < 3; i++) {
      c[i] /= m;
    }
  }
}

Vector3D Vector3D::operator+(Vector3D& other) {
  return Vector3D(c[0]+other.c[0], c[1]+other.c[1], c[2]+other.c[2]);
}

float Vector3D::operator*(Vector3D& other) {
  float ans = 0.0;
  for (int i=0; i < 3; i++) {
    ans += c[i]*other.c[i]; 
  }
  return ans;
}

