# coding: utf-8

class TrieIndex(object):
    def __init__(self):
        self.root = {}

    def add(self, key, value=None):
        if not key: return False

        p = self.root
        for i, u_char in enumerate(key):
            if u_char not in p:
                p[u_char] = {}
            p = p[u_char]

        p["__val"] = value
        return True

    def get(self, key):
        """
        Get the value by the key
        """
        p = self.root
        for i, u_char in enumerate(key):
            if u_char not in p:
                return None
            p = p[u_char]

        if p and "__val" in p:
            return p["__val"] # p can still hold the None value

        return None

    def contains(self, key):
        """
        Check whether the key is contained in the index
        """
        p = self.root
        for i, u_char in enumerate(key):
            if u_char not in p:
                return False

            p = p[u_char]

        return p and "__val" in p

    def matcher(self, string, begin=0):
        """
        matcher: find the common prefix of a given string and the trie

        @string the given string in unicode
        @begin the start index, ignore the unicode chars before it

        @return generator each time gives the index which it meets
        """
        string = string[begin:]
        p = self.root
        for i, u_char in enumerate(string):
            if u_char not in p:
                break

            p = p[u_char]
            if "__val" in p:
                yield begin + i + 1

if __name__ == "__main__":
    t = TrieIndex()
    t.add("abcd")
    t.add("abc")
    t.add(u"新中关")

    print "'abcd', 'abc' and u'新中关' added into trie index"

    print "=======\nexistence check:"
    print "abc in trie:", t.contains("abc")
    print "abcd in trie:", t.contains("abcd")
    print "ab in trie:", t.contains("ab")
    print "a in trie:", t.contains("a")
    print "新中关 in trie:", t.contains(u"新中关")

    print "=======\nmatching check:"
    for i in t.matcher("abcd"):
        print "find prefix 0-%d:" % i, ("abcd")[0:i]

    for i in t.matcher(u"我在新中关", 2):
        print "find prefix %d-%d" % (2, i), (u"我在新中关")[2:i]

    print "-------\nno match is found if we start matching from 0:"
    for i in t.matcher(u"我在新中关", 0):
        print "find prefix %d-%d" % (0, i), (u"我在新中关")[0:i]

    print "=======\nvalue check:"
    print "default values of abc and abcd are None:", t.get(u'abc'), t.get(u'abcd')

    t.add('abcdefg', 100)
    print "added key 'abcdefg' with value=100"
    print "get values of 'abcdefg' key:", t.get(u'abcdefg')


