#!/usr/bin/python


if __name__ == "__main__":

    #ainp = [ -1, 3, -4, 5, 1, -6, 2, 1 ]
    ainp = []
    lsum_arr = []
    rsum_arr = []

    print len(ainp)
    print "Initial Input: %s" %str(ainp)
    for idx in range(0, len(ainp)):
        if idx == 0:
            lsum_arr.append(0)
        else:
            lsum_arr.append(lsum_arr[idx-1] + ainp[idx-1])

    print "Left sum: %s" %str(lsum_arr)

    if len(lsum_arr):
        total_sum = lsum_arr[len(lsum_arr)-1] + ainp[len(ainp)-1]
    for idx in range(0, len(ainp)):
        left_sum = lsum_arr[idx]
        right_sum = total_sum - left_sum - ainp[idx]
        if left_sum == right_sum:
            print "Found equivalent index %s val %s" %(idx, ainp[idx])



