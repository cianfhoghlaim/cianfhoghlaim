#include <iostream>
using namespace std;

int main() {
  int myarray[4];
  int len;

  // danger!! if user enters len > 4, we have a "buffer overflow"
  // and weird things will happen
  cout << "how many numbers to enter: ";
  cin >> len;

  //cout << "pointer to len = " << &len << "\n";
  for (int i = 0; i < len; i++) {
    //cout << "pointer = " << myarray+i << "\n";
    cout << "Enter value #" << i << ": ";
    cin >> myarray[i];
  }

  for (int i = 0; i < len; i++) {
    cout << "element at index " << i << " = " << myarray[i] << "\n";
  }
 
  return 0;
}
