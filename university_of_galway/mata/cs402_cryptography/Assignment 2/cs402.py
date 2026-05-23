"""Some useful Python classes and functions for CS402 Cryptography.
You can load everything by placing this file somewhere in your Python module
path and running

    from cs402 import *

"""

__date__ = '2021-02-22'

########################################################################
# ALPHABETS
########################################################################
BINARY = "01"
ALPHABET26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHABET27 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
ALPHABET64 = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789."
ALPHABET68 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;: \n"
ALPHABET85 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:+-/*!?()[]{}_<>'\" \n"
ASCII  = ''.join(chr(i) for i in range(128))
EASCII = ''.join(chr(i) for i in range(256))

########################################################################
# UTILITY FUNCTIONS
########################################################################

def string_to_int_list(alphabet, text):
    try:
        return [alphabet.index(char) for char in text]
    except ValueError:
        raise ValueError('string contains characters not present in given alphabet')

def int_list_to_string(alphabet, int_list):
    try:
        return ''.join(alphabet[i] for i in int_list)
    except IndexError:
        raise ValueError('list of integers contains invalid indices for given alphabet')

def frequency_analysis(text, alphabet=None):
    if alphabet is not None:
        D = {char: 0 for char in alphabet}
    else:
        D = {}
        
    for char in text:
        D[char] = D.get(char,0) + 1
    return {char: float(count)/len(text) for char,count in D.items()}
    
def frequency_histogram(text, alphabet=None):
    import matplotlib.pyplot as plt
    D = frequency_analysis(text, alphabet)
    alphabet = sorted(D.keys())
    values = [D[char] for char in alphabet]
    plt.bar(['\\n' if char == '\n' else char for char in alphabet],values)
    plt.show()

def pairwise(collection):
    # Source: https://stackoverflow.com/a/30426000
    it = iter(collection)
    while True:
        try:
            yield next(it), next(it)
        except StopIteration:
            return

def without_trailing_zeros(L):
    L = list(L)
    while not L[-1]:
        L.pop()
    return L

def digraph_ranking(text, limit=10):
    if not len(text) % 2 == 0:
        raise ValueError('text of even length needed')
    D = {}
    for c,d in pairwise(text):
        key = c + d
        D[key] = D.get(key,0) + 1

    print('Most frequently used digraphs:')
    for i,key in enumerate(sorted(D.keys(),key=lambda k: D[k], reverse=True)):
        if i >= limit:
            return
        print('%2d. "%2s"\t%4d' % (i+1,key,D[key]))

def random_vector(length, m=2):
    import random
    # Produce a random vector of a given length over the integers mod m.
    return [random.randint(0,m-1) for _ in range(length)]

########################################################################
# NUMBER THEORY
########################################################################
def gcd(a, b):
    if a < 0:
        a = -a
    if b < 0:
        b = -b
    if not b:
        return a
    return gcd(b, a % b)

def egcd(a, b):
    if b < 0:
        x, y = egcd(a, -b)
        return x, -y
    if a < 0:
        x, y = egcd(-a, b)
        return -x, y
    if b == 0:
        return 1, 0
    x, y = egcd(b, a % b)
    return y, x - (a // b) * y

def modular_inverse(a, m):
    x, y = egcd(a,m)
    d = a*x + m*y
    if d != 1:
        raise ValueError('%d is not invertible modulo %d' % (a,m))
    return x % m

def modular_inverse_of_matrix(A, m):
    from sympy import Matrix
    A = Matrix(A)
    det = A.det()
    x = modular_inverse(int(det), m)
    B = x * A.adjugate()
    d,e = A.shape
    return [[int(B[i,j]) % m for j in range(e)] for i in range(d)]

def modular_matrix_product(A, B, modulus):
    if not A or not B:
        raise ValueError('invalid matrices')
    
    m = len(A)
    n = len(A[0])
    if n != len(B):
        raise ValueError('dimension mismatch')
    o = len(B[0])

    if any(len(a) != n for a in A) or any(len(b) != o for b in B):
        raise ValueError('inconsistent row lengths')
    
    return [[sum(A[i][k] * B[k][j] for k in range(n)) % modulus
             for j in range(o)]
            for i in range(m)]

def solve_modular_linear_system(A, b, m):
    from sympy import Matrix
    try:
        Ainv = modular_inverse_of_matrix(A, m)
    except ValueError:
        raise ValueError('non-invertible coefficient matrix')
    return [a % m for a in Matrix(Ainv) * Matrix([b]).transpose()]
    
########################################################################
# GENERAL TEXT-BASED CIPHERS
########################################################################

class Cipher:
    def __init__(self, alphabet):
        self.alphabet = alphabet
    
    # The encryption and decryption function are assumed to act on lists of
    # integers from 0 up to and incluing len(alphabet) - 1.
    
    def encrypt_int_list(self, key, int_list):
        raise NotImplementedError

    def decrypt_int_list(self, key, int_list):
        raise NotImplementedError
    
    def encrypt_string(self, key, text):
        return int_list_to_string(self.alphabet,
                                  self.encrypt_int_list(key, string_to_int_list(self.alphabet, text)))

    def decrypt_string(self, key, text):
        return int_list_to_string(self.alphabet,
                                  self.decrypt_int_list(key, string_to_int_list(self.alphabet, text)))

    def encrypt_file(self, key, in_filename, out_filename):
        with open(in_filename, 'r') as in_file:
            text = in_file.read()
        with open(out_filename, 'w') as out_file:
            out_file.write(self.encrypt_string(key, text))

    def decrypt_file(self, key, in_filename, out_filename):
        with open(in_filename, 'r') as in_file:
            text = in_file.read()
        with open(out_filename, 'w') as out_file:
            out_file.write(self.decrypt_string(key, text))

########################################################################
# SHIFT CIPHERS
########################################################################
            
class ShiftCipher(Cipher):
    def encrypt_int_list(self, key, int_list):
        return [(i + key) % len(self.alphabet) for i in int_list]

    def decrypt_int_list(self, key, int_list):
        return self.encrypt_int_list(-key, int_list)

########################################################################
# AFFINE CIPHERS
########################################################################

class AffineCipher(Cipher):
    def encrypt_int_list(self, key, int_list):
        a,b = key
        if gcd(a, len(self.alphabet)) != 1:
            raise ValueError('invalid key')
        return [(a*i + b) % len(self.alphabet) for i in int_list]

    def decrypt_int_list(self, key, int_list):
        a,b = key
        if gcd(a, len(self.alphabet)) != 1:
            raise ValueError('invalid key')
        x = modular_inverse(a, len(self.alphabet))
        return self.encrypt_int_list([x, (-b*x) % len(self.alphabet)], int_list)

########################################################################
# VIGENERE CIPHERS
########################################################################

class VigenereCipher(Cipher):
    def _process_int_list(self, key, int_list, scalar):
        key_list = string_to_int_list(self.alphabet, key)

        return [(c + scalar * key_list[i % len(key_list)]) % len(self.alphabet) for i,c in enumerate(int_list)]
    
    def encrypt_int_list(self, key, int_list):
        return self._process_int_list(key, int_list, +1)
    
    def decrypt_int_list(self, key, int_list):
        return self._process_int_list(key, int_list, -1)

########################################################################
# HIGHER-DIMENSIONAL AFFINE CIPHERS (INCL. HILL CIPHERS) 
########################################################################

class HigherAffineCipher(Cipher):
    def __init__(self, alphabet, dimension):
        self.alphabet = alphabet
        self.dimension = dimension

    def encrypt_int_list(self, key, int_list):
        from sympy import Matrix
        
        m = len(self.alphabet)
        
        A,b = Matrix(key[0]), Matrix(key[1])
        if len(int_list) % self.dimension:
            raise ValueError('message size is not a multiple of the dimension')

        if gcd(A.det(), m) != 1: 
            raise ValueError('invalid key')

        ciphertext = []
        for i in range(len(int_list) // self.dimension):
            x = Matrix(int_list[i*self.dimension:(i+1)*self.dimension])
            y = A * x + b
            ciphertext.extend(int(i) % m for i in y)
        return ciphertext

    def decrypt_int_list(self, key, int_list):
        from sympy import Matrix
        
        A,b = Matrix(key[0]), Matrix(key[1])
        B = Matrix(modular_inverse_of_matrix(A, len(self.alphabet)))
        return self.encrypt_int_list([B, list(-B*b)], int_list)

########################################################################
# LINEAR FEEDBACK SHIFT REGISTERS
########################################################################

class LFSR:
    def __check(self):
        if any(c not in range(1, self.length+1) for c in self.connection):
            raise ValueError('invalid connection polynomial')

        if any(s not in [0,1] for s in self.state):
            raise ValueError('invalid entry of state vector')
        
        if self.length != len(self.state):
            raise ValueError('invalid length of state vector')
        
    def __init__(self, length, connection, initial_state=None):
        self.length = length
        self.connection = set(connection)

        if initial_state is None:
            self.state = length * [0]
        else:
            self.state = list(initial_state)
            
        self.__check()
        

    def advance(self):
        self.__check()
        
        output = self.state[0]
        self.state = self.state[1:] + [sum(self.state[self.length-i] for i in self.connection) % 2]
        return output

    def __iter__(self):
        return self

    def __next__(self):
        return self.advance()
    
    def period(self, initial_state=None):
        if initial_state is not None:
            initial_state = list(initial_state)
            self.state = initial_state
        else:
            initial_state = self.state

        cnt = 1
        self.advance()
        while self.state != initial_state:
            cnt += 1
            self.advance()
        return cnt
    
class StreamCipher:
    def __init__(self, L):
        self.L = L

    def encrypt_bit_string(self, key, bits):
        self.L.state = key
        return [(b + self.L.advance()) % 2 for b in bits]
    
    decrypt_bit_string = encrypt_bit_string

########################################################################
# RSA
########################################################################

class RSA(Cipher):
    # NOTE:
    # The first symbol (in position zero) of our alphabet is treated specially
    # in that trailing instances of this symbol will be silently removed from
    # plaintexts and ciphertexts.
    def encrypt_int_list(self, public_key, int_list):
        int_list = without_trailing_zeros(int_list)
        base = len(self.alphabet)        
        m = sum(a * base**i for i,a in enumerate(int_list))

        n,e = public_key
        if m >= n or any(a >= len(self.alphabet) for a in int_list):
            raise ValueError('invalid list of integers')
        
        c = pow(m, e, n)
        out_list = []
        while c:
            c,r = divmod(c, base)
            out_list.append(r)
        return out_list
    
    decrypt_int_list = encrypt_int_list
