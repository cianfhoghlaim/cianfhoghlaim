#include "mystring.h"
#include <string.h>

// allocate room for 32 chars but set to empty string
mystring::mystring() {
  allocated = 32;
  data = new char[allocated];
  data[0] = 0;
}

// allocate just enough room to copy str over
mystring::mystring(const char* str) {
  allocated = strlen(str)+1;
  data = new char[allocated];
  strcpy(data, str);
}

// copy constructor
mystring::mystring(const mystring& m) {
  allocated = m.allocated;
  data = new char[allocated];
  strcpy(data, m.data);
}

mystring::~mystring() {
  delete data;  // or delete[] data;
}

void mystring::resize(int newsize) {
  if (newsize > allocated) {
    char* temp = new char[allocated];
    strcpy(temp, data);
    delete data;
    data = new char[newsize];
    strcpy(data, temp);
    allocated = newsize;
    delete temp;
  }
}

int mystring::length() const {
  return strlen(data);
}

void mystring::operator+=(const mystring& other) {
  resize(length() + other.length() + 1);
  strcat(data, other.data);
}

ostream& operator<<(ostream& out, const mystring& ms) {
  out << ms.data;
  return out;
}
