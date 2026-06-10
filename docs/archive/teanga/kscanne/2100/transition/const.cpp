#include <iostream>
using namespace std;

int main() {
  const int oranges = 45;
  int apples = 3;
  //oranges++;
  apples++;
 
  const string alice("Alice");
  string bob("Bob");
  //alice.append(" Smith");
  bob.append(" Smith");

  cout << bob << " has " << apples << " apples." << endl;
}
