"""
Low-level utility functions.
"""
import random
import re
import httplib
import json
import datetime
import time
import calendar
from logging import log, DEBUG, INFO, WARN, ERROR
from functools import update_wrapper
import itertools
try:
    from Crypto.Hash import SHA as sha
except:
    import sha

def decorator(d):
    """Make function d a decorator: d wraps a function fn."""
    def _d(fn):
        return update_wrapper(d(fn), fn)
    update_wrapper(_d, d)
    return _d

@decorator
def timed(f):
    def wrapper(*args, **kwargs):
        start_t = time.time()
        retval = f(*args, **kwargs)
        dd('%s time: %5.3f' % (f.__name__, time.time() - start_t))
        return retval
    return wrapper

class Obj(object):
    """
    A generic object with members set at create time, as in o=Obj(x=1,y=2)
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

### The following secret string should be kept secret. Whoever has it can spoof
### session tokens and impersonate anybody.
##secret = 'd0fI7jsfjudIJkDeHFzO6m4maDzBS0uVwkaG5lQtKbvdZto8yD'

class PurpleError(Exception):
    # HTTP error codes are used for Purple return codes too.
    OK = httplib.OK # 200
    BAD_PARAM = httplib.BAD_REQUEST # 400
    NOT_ALLOWED = httplib.FORBIDDEN # 403
    NOT_FOUND = httplib.NOT_FOUND # 404
    TIMEOUT = httplib.REQUEST_TIMEOUT # 408
    CONFLICT = httplib.CONFLICT # 409
    ERROR = httplib.INTERNAL_SERVER_ERROR # 500
    NOT_IMPLEMENTED = httplib.NOT_IMPLEMENTED # 501
    SERVICE_UNAVAILABLE = httplib.SERVICE_UNAVAILABLE # 503
    def __init__(self, code, msg):
        log(ERROR, '*** %d: %s' % (code, msg))
        super(Exception, self).__init__(code, msg)

## Temporary code for debugging
dbg_messages = []

def dbg(msg):
    global dbg_messages
    dbg_messages.append(msg)

def dbg_clear():
    global dbg_messages
    dbg_messages = []

def dbg_get():
    global dbg_messages
    return dbg_messages

def dd(msg):
    log(INFO, '>> ' + msg)
#########

def u8(x):
    """
    Return a UTF8 string from any object, for safe logging, etc.
    """
    if type(x) is str:
        return x
    return unicode(x).encode('utf8','replace')

def sha1(s):
    """Return the hex SHA1 of the given string"""
    return sha.new(s).hexdigest()

##def sign_str(s):
##    """Return the given string signed by our secret""" #TODO: replace calls to this with class Signature.
##    return Signature(secret).sign(s)

def first_n(n, iterable):
    "Iterator over the first n elements of iterable"
    return (x for _,x in itertools.izip(xrange(n), iterable))

class Signature:
    """
    Sign short pieces of text using a secret key and strip and verify the signature.
    """
    def __init__(self, secret, sep=':'):
        """
        secret (str) - The secret that will be used for signing and verification.
        sep (str) - Some string to put between the text and the signature. This
            can be an empty string.
        """
        self.secret = secret
        self.sep = sep

    def sign(self, text):
        """Return the given text with a signature appended."""
        return text + self.sep + self.gen_sig(text)

    def strip(self, signed_text):
        """Remove the signature and return the original unsigned text."""
        tail_len = len(self.sep) + 40
        return signed_text[:-tail_len]

    def gen_sig(self, text):
        """Generate and return the signature for the given text."""
        return sha1(text + self.secret)

    def verify(self, signed_text):
        """Return True iff the given text contains a valid signature."""
        tail_len = len(self.sep) + 40
        if len(signed_text) < tail_len or signed_text[-tail_len:-40] != self.sep:
            return False
        text, sig = signed_text[:-tail_len], signed_text[-40:]
        return self.gen_sig(text) == sig

# The chars that make up IDs in the database (user IDs, group IDs, etc).
# Do not change this - a change can break the program.
# Note: this string must be sorted by ASCII value.
_ID_ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

# Chars to be used in auto-generated passwords that users need to read and remember.
# This does not contain confusing letters/digits (1-I-l, 0-O) and preferably impossible
# to create offensive words from (omitting vowels is pretty good for this).
_PWD_CHARS = '23456789bcdghjkmnpqrstvwxyz'

def make_random_id(l, alphabet=_ID_ALPHABET):
    """
    Return a random string of len l made of the given chars
    (default: uppercase letters, lowercase letters and digits).
    """
    return ''.join([random.choice(alphabet) for _ in xrange(l)])

def make_group_access_code():
    # Private group access codes are unque-per-group and for single use, so they can be short.
    return make_random_id(5, _PWD_CHARS)

def make_user_id():
    return 'u' + make_random_id(14) # Do not change! See uid2fraction below().

def is_user_id(s):
    """Return True iff the given string has the format of a user id."""
    #TODO: remove the hard-coded old uids once they are deleted from the DB.
    return (re.match(r'u[%s]{14}\Z' % _ID_ALPHABET, s)
        or s in (
        # Old user_ids on purple-dev:
        '6YFqLzxPbDi8UH','Buo8ZZ6Pb7DnMj','Jc9p8E6G3GizKw','QNpQbJFf9ORucD',
        # Old user_ids on 3ringstrialservice:
        '6FdXg6sER6hHHE','7DxH9j00qqiUk4','AdhTJIXVWn9qnL','EIAEPLTaOT9miD','HoNrkwwPO7kT5R',
        'J1LXsSF7ult824','J7dZWScIJytTAL','QfR7LOWjS1J7jI','RthdFH4ZtFp2Wd','S540Qn9zzshf3v',
        'WsbH309nlyI6hZ','crZziaO74SO0XR','gLYs5HElcdONaz','le6IG5itKQZR2o','ophnLHU3tDSUd9',
        'szrlQmzrliCpnI','wZQFolLROCInCv','xl9CVXCiUmM1Q9')
       )

def datetime2timestamp(dt):
    return calendar.timegm(dt.utctimetuple()) # WTF?!

def uid2fraction(uid):
    """
    Given a user id, return where in the user-id space it is as a fraction
    in the range 0.0-1.0 ('u0000000000000000' -> 0.0, 'uzzzzzzzzzzzzzz' -> ~1.0).
    Assumes user-ids in the DB are all the same length and made of 'u' followed
    by random chars out of [a-zA-Z0-9].
    """
    #NOTE: this code does not work correctly with old user IDs.
    radix = len(_ID_ALPHABET)
    frac = 0.0
    exp = 1.0/radix
    for c in uid[1:]:
        frac += _ID_ALPHABET.find(c) * exp
        exp /= radix
    return frac

def json_dump(var, sort_keys=None):
    """Return a compact JSON representation of var as a string."""
    if sort_keys is None:
        return json.dumps(var, separators=(',',':')) # Use default sort_keys, whatever it is.
    return json.dumps(var, separators=(',',':'), sort_keys=sort_keys)

def json_load(s, dflt=None):
    """Convert back from a JSON-formatted string to a Python variable"""
    return json.loads(s) if s else dflt

def phone_tail(num):
    """Return the last 7 digits from the given (short) string."""
    return filter(lambda c: c.isdigit(), num)[-7:]

def name_to_3_tuple(name):
    """
    Return a canonic form of the given name - (first, middle, last) in lowercase,
    treating hyphens and dots as spaces.
    """
    L = name.lower().replace('-',' ').replace('.',' ').split()
    if not L:       return ('', '', '')
    if len(L) == 1: return (L[0], '', '')
    if len(L) == 2: return (L[0], '', L[1])
    return (L[0], L[1], ' '.join(L[2:]))

def same_name(name1, name2):
    """
    Return True if the two names seem to belong to the same person.
    Match examples: "John K. Doe" vs "J. Doe", "Moe Bill" vs "Bill Moe".
    Mismatch example: "James" vs "J. Bond", "Mary Jane" vs "John Jane".
    Comparison allows some (but not all) order variations and some initial-vs-
    full name parts.
    """
    def variations(name):
        """Iterate over all reasonable order variations of first-middle-last names"""
        yield (name[0], name[1], name[2])
        if name[1]:
            yield (name[2], name[0], name[1])
            yield (name[1], name[2], name[0])
        else:
            yield (name[2], name[1], name[0])
    def component_match(s1, s2):
        """
        Given two strings, return 0 if they are equal, 1 if one is the initial
        of the other, 3 if one is empty and the other not, 9 if different.
        """
        if s1 == s2: return 0
        if not s1 or not s2: return 3
        if len(s1) == 1 and s2.startswith(s1): return 1
        if len(s2) == 1 and s1.startswith(s2): return 1
        return 9
    def name_match(name1, name2):
        return 5 > sum(map(lambda (a,b): component_match(a,b), zip(name1,name2)))
    if type(name1) in (str,unicode):
        name1 = name_to_3_tuple(name1)
    if type(name2) in (str,unicode):
        name2 = name_to_3_tuple(name2)
    for n1 in variations(name1):
        if name_match(name2, n1):
            return True
    return False
# Previous code:
#    #TODO: Maybe allow rotations (John K Doe appearing as Doe John K)
#    #TODO: maybe allow either first or last to be an initial (J Doe would match John Doe)
#    if type(name1) in (str,unicode):
#        name1 = name_to_3_tuple(name1)
#    if type(name2) in (str,unicode):
#        name2 = name_to_3_tuple(name2)
#    first1,mid1,last1 = name1
#    first2,mid2,last2 = name2
#    dd('comparing %s -- %s' % (repr(name1), repr(name2)))
#    if not mid1 and not mid2 and ((first1,last1) == (first2,last2) or (first1,last1) == (last2,first2)):
#        dd('-> same!')
#        # Exact match with possible reversal of order when no middle name.
#        return True
#    # First and last names must match exactly
#    if (first1,last1) != (first2,last2):
#        return False
#    # Middle name can match more loosely - by one being absent or by it being
#    # the initial letter of the other.
#    if mid1 == mid2:
#        return True
#    if len(mid1) <= 1 and mid2.startswith(mid1):
#        return True
#    if len(mid2) <= 1 and mid1.startswith(mid2):
#        return True
#    return False

def american_date_to_date(s):
    """
    Given a mm/dd/yyyy string return a date() object. Return None if s is empty
    or invalid.
    """
    if False:
        #TODO
        try:
            m,d,y = [int(x) for x in s.split('/')]
            return datetime.date(y, m, d)
        except:
            pass
    return None #TODO

def get_source_abbrev(source): #TODO: move this to handles.py
    """
    Return the short form of the given source ('fb', 'ab', etc) or an empty string
    if not a known source.
    """
    #TODO: complete the list.
    abbrevs = {'facebook':'fb', 'twitter':'tt', 'addressbook':'ab', 'linkedin':'li',
               'foursquare':'4s'}
    return abbrevs.get(source, '')

#TODO: move the following function to a less low-level source file.
def merge_contact_dicts(c, c1):
    """
    Merge details from contact c1 into contact c.
    Properties that are lists get appended with duplicates dropped.
    Non-empty properties take precedence over empty ones and longer strings over
    shorter ones.
    The 'name' property gets a special treatment: longer AB entries are preferred
    and other names are collected in an added 'other_names' property.
    Note that the 'handles' list may contain duplicate handles if they appear
    with different labels.
    """
    def add_other_name(c, name):
        """Add name to c['other_names'] if not already there and not empty"""
        if name and name.lower() not in map(lambda n: n.lower(), c.setdefault('other_names',[])):
            c['other_names'].append(name)

    for k in c1:
        t1, t = type(c1[k]), type(c.get(k))
        if t1 is list and t is list:
            # Append the two lists, dropping duplicates.
            L = c[k][:]
            L1 = [v for v in c1[k] if v not in L]
            c[k] = L + L1
        elif t1 in (str,unicode) and t in (str,unicode):
            # Prefer longer strings over shorter ones, pick arbitrarily if both
            # have the same length; collect distinct names in 'other_names'.
            if len(c1[k]) > len(c[k]):
                if k == 'name':
                    add_other_name(c, c[k])
                c[k] = c1[k]
            elif k == 'name' and c[k].lower() != c1[k].lower():
                add_other_name(c, c1[k])
        elif t1 in (int,float) and t in (int,float):
            # Prefer larger numeric values over smaller ones.
            if c1[k] > c[k]:
                c[k] = c1[k]
        elif c1[k]:
            # Other types - prefer non-empty, pick arbitrarily if both non-empty.
            c[k] = c1[k]

def iter_chunks(items, chunk_size):
    """
    Iterator over slices of the items list that are all roughly the same size
    and between 0.75*chunk_size and 1.5*chunk_size items long.
    """
    n_items = len(items)
    n_chunks = max(1, int(round(n_items * 1.0 / chunk_size)))
    chunk_size = n_items / n_chunks
    rem = n_items % n_chunks
    idx = 0
    while idx < n_items:
        this_chunk_size = chunk_size + int(rem > 0)
        yield items[idx:idx+this_chunk_size]
        idx += this_chunk_size
        rem -= 1
