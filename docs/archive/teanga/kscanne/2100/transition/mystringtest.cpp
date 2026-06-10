#include "mystring.h"

int main() {
  mystring a("Kevin");
  mystring b("Scannell");
  mystring acopy(a);
  cout << "length of " << a << " = " << a.length() << endl;
  cout << "length of " << b << " = " << b.length() << endl;
  acopy += b;
  cout << "concatenated = " << acopy << endl;
}


