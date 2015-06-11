import random, string, crypt, math
from hmac import compare_digest as compare_hash
from collections import Counter


def hash_password(password):
    salt = ''.join(random.sample(string.ascii_letters, 2))
    return crypt.crypt(crypt.crypt(password, salt), salt)


def compare_password(password, cryptedpasswd):
    return compare_hash(crypt.crypt(crypt.crypt(password, cryptedpasswd), cryptedpasswd), cryptedpasswd)

def entropy(s):
    g, lenght = Counter(s),float(len(s))
    return -sum(zlicz/lenght * math.log(zlicz/lenght,2) for zlicz in g .values())

def random_string():
    return ''.join(random.choice(string.ascii_letters) for i in range(20))
