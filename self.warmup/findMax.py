'''
Given a list of non negative integers, arrange them such that they form the largest number.

For example:

Given [3, 30, 34, 5, 9], the largest formed number is 9534330.

Note: The result may be very large, so you need to return a string instead of an integer.
'''

class Solution:

    # @param A : tuple of integers
    # @return a strings
    def findMax(self, A, itern=0, common_prefix=0):

        if len(A) == 1:
            print "Ret: %s" %str(A)
            return ''.join(map(str,A)) #Base condition

        print "Input Arr: %s itern:%d" %(str(A), itern)
        more_iter = False
        ret = ''
        hashA = [[] for x in range(10)]
        for item in A:
            sitem = str(item)
            if itern < len(sitem):
                digit = int(sitem[itern])
                hashA[digit].append(item)
                more_iter = True
            else:
                digit = int(sitem[len(sitem)-1])
                hashA[digit].append(item)


        print "Hash: %s"  %str(hashA)
        print "\n\n"

        itern +=1
        #Now read the hashA in reverse order
        for idx in reversed(range(len(hashA))):
            if len(hashA[idx]) > 0:
                if not more_iter:
                    ret += ''.join(map(str,hashA[idx]))
                else:
                    # Find max from a list of integers starting with digit 'idx'
                    ret += self.findMax(hashA[idx],itern)
        print "Ret2: %s" %ret
        return ret

    def largestNumber(self, A):
        ret = self.findMax(A)
        answer = ret
        if int(ret) == 0:
            answer = str(int(ret))
        return answer

if __name__ == "__main__":
#    A = [3, 30, 34, 5, 9]
    A = [ 782, 240, 409, 678, 940, 502, 113, 686, 6, 825, 366, 686, 877, 357, 261, 772, 798, 29, 337, 646, 868, 974, 675, 271, 791, 124, 363, 298, 470, 991, 709, 533, 872, 780, 735, 19, 930, 895, 799, 395, 905 ]
    s = Solution()
    print s.largestNumber(A)
