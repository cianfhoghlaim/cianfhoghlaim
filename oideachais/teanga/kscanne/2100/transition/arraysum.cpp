#include <iostream>
using namespace std;

int main() {
  int myarray[4];

  for (int i = 0; i < 4; i++) {
    cout << "Enter value #" << i << ": ";
    cin >> myarray[i];
  }

  int sum = 0;
  for (int i = 0; i < 4; i++) {
    sum += myarray[i];
  }
 
  cout << "Sum is " << sum << endl;

  return 0;
}
