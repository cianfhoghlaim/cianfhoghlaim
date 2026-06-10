#include <iostream>
using namespace std;

int main() {
  int* myarray=0;
  int len=-1;

  while (len!=0) {
    cout << "how many numbers to enter (0 to quit): ";
    cin >> len;

    myarray = new int[len];
    //cout << "pointer to len = " << &len << "\n";
    for (int i = 0; i < len; i++) {
      //cout << "pointer = " << myarray+i << "\n";
      cout << "Enter value #" << i << ": ";
      cin >> myarray[i];
    }

    int sum = 0;
    for (int i = 0; i < len; i++) {
      sum += myarray[i];
    }
    cout << "sum = " << sum << endl;
    delete myarray;
  }
 
  return 0;
}
