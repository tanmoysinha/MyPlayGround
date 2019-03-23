#!/usr/bin/python

class Solution:
    # @param x : integer
    # @param n : integer
    # @param d : integer
    # @return an integer
    def pow(self, x, n, d):
        if n == 0:
            return 1
        if n % 2 != 0:
            return ((x % d) * pow(x, n-1, d)) % d

        rem = pow(x, n/2, d)
        return (rem * rem) %d

