#!/usr/bin/python
from bisect import bisect_left

def findMedian(A):
    row_c = len(A)
    col_c = len(A[0])
    total_c = row_c * col_c
    med_idx = (total_c + 1) /2 #Ceiling

    for rid in range(0, len(A)):
        crow = A[rid] #Current row
        for item in crow:
#            print "Process item: %d" %item
            dup = 0
            lesser = 0
            for ilist in A:
                dup += ilist.count(item)
                lesser += bisect_left(ilist, item)

            print "item:%d dup:%d lesser:%d" %(item, dup, lesser)
            if lesser < med_idx and (lesser + dup) >= med_idx:
                return item

if __name__ == "__main__":

#A = [ [1, 3, 6], [2, 6, 9], [3, 6, 9] ]
    A = [ [5],[4],[3],[1],[2],[1],[3],[4],[3],[2],[5]]
    print "Median is %s" %str(findMedian(A))
