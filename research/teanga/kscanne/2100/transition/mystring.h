#include <iostream>
using namespace std;

class mystring {

  private:
    char* data;
    int allocated;

    void resize(int newsize);

  public:
    mystring();
    mystring(const char* str);
    mystring(const mystring& m);
    ~mystring();
    int length() const;
    void operator+=(const mystring& other);

    friend ostream& operator<<(ostream& out, const mystring& ms);
};

