#include <iostream>
using namespace std;
#include "RichPoint.h"
#include "mystring.h"

class LabeledPoint : public RichPoint {

  private:
     mystring label;

  public:
    LabeledPoint(double initialX, double initialY);
    LabeledPoint(double initialX, double initialY, const char* name);
    LabeledPoint(double initialX, double initialY, mystring name);
    mystring getLabel() const;

};

ostream& operator<<(ostream& out, LabeledPoint p);
