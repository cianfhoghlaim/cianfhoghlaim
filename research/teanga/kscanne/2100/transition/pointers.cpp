#include <iostream>
using namespace std;

// the argument "a" is an array of ints
int sum(int* a, int len) {
  int ans = 0;
  for (int i = 0; i < len; i++) {
    ans += a[i]; 
  } 
  return ans;
}

int main() {
  int numbers[] = {1,5,6,4,67,3,4,2};
  int backup[8];
  int num = 5;
  int* address_of_num = &num;

  cout << "num: " << num << endl;
  cout << "num, via pointer: " << *address_of_num << endl;
  cout << "address of num: " << address_of_num << endl;

  for (int i = 0; i < 8; i++) {
    backup[i] = numbers[i]; 
  }
  cout << *backup << endl; // prints "1"
  cout << *(backup+4) << endl; // prints 67
  cout << "sum of backup: " << sum(backup, 8) << endl;


  cout << "original:" << endl;
  for (int i = 0; i < 8; i++) {
    cout << numbers[i] << endl;
  }
  cout << "backup:" << endl;
  for (int i = 0; i < 8; i++) {
    cout << backup[i] << endl;
  }
}
