#include <iostream>
using namespace std;

class RichPoint {

  private:
    double _x;
    double _y;

  public:
    RichPoint(double initialX, double initialY);
    double getX() const;
    double getY() const;
    void setX(double val);
    void setY(double val);

    void scale(double factor);
    double distance(RichPoint other) const;
    void normalize();
    RichPoint operator+(RichPoint other) const;
    RichPoint operator*(double factor) const;  // scalar multiple
    double operator*(RichPoint other) const; // dot product

};

RichPoint operator*(double factor, RichPoint p);
ostream& operator<<(ostream& out, RichPoint p);
