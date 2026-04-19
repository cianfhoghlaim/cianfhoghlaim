#include <iostream>
using namespace std;

int main() {
  int myarray[10];
  int i;

  for (i=0; i < 10; i++) {
    cin >> myarray[i];
    if (cin.eof()) {
      cerr << "Warning: less than 10 integers on input, quitting" << endl;
      break;
    }
    else if (cin.fail()) {
      cerr << "Not a valid integer, quitting" << endl;
      break;
    }
    else if (cin.bad()) {
      cerr << "Fatal failure reading input, quitting" << endl;
      break;
    }
  }

  if (i==10) {
    int sum = 0;
    for (int i=0; i < 10; i++) {
      sum += myarray[i];
    }
    cout << "sum = " << sum << endl;
  }
  return 0;
}
