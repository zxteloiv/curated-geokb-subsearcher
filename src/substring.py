# coding: utf-8

def substring_iter(string, min_len=1):
    for l in xrange(min_len, len(string)):
        for pos in xrange(0, len(string)):
            endpos = pos + l
            if endpos > len(string):
                break

            yield string[pos:endpos]

if __name__ == "__main__":
    string = "hello"
    print "Given string:", string, 'length:', len(string)

    all_substrings = [s for s in substring_iter(string)]
    print "Number of substrings:", len(all_substrings)

    print "all substrings listed below:"
    print '\n'.join(all_substrings)

    print "=======\ncount of substrings for strings in different lengths"
    print "slen\tsubslen"
    for l in xrange(1, 20):
        string = 'a' * l
        print "%d\t%d" % (len(string), len([1 for s in substring_iter(string)]))



