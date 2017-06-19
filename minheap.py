import math

class MinHeap:

    def __init__(self, heapsize):
        self.heap = [(0, 0)]*(heapsize +1)

    def push(self, el):
        if el[1] > self.heap[1][1]:
            self.heap[1] = el
        # self.heap.append(el)
        self.heapifyList(self.heap)

    def pop(self):
        self.heapifyList(self.heap)
        return min(self.heap)

    def heapifyList(self, list):
        self.heap = list
        i = int(math.floor(len(self.heap))) / 2
        while i >= 1:
            self.heapify(i)
            i = i - 1

    def heapify(self, position):

        childPos = 2 * position

        while childPos <= len(self.heap)-1:
            if childPos < len(self.heap)-1 and self.heap[childPos][1] > self.heap[childPos + 1][1]:
                childPos += 1
            if self.heap[position][1] <= self.heap[childPos][1]:
                break
            else:
                temp = self.heap[position]
                self.heap[position] = self.heap[childPos]
                self.heap[childPos] = temp

                position = childPos
                childPos = 2 * position

    def getMinHeapToValue(self, marker):
        del self.heap[0]
        return self.heap[:marker]


if __name__ == '__main__':
    a = ['#',7,2,4,8,12,11,9,6]
    # a = [2,7,4,8,12,9,6,11]
    b = MinHeap()
    b.heapifyList(a)
    print '["#", 1, 2, 3, 4, 5, 6, 7, 8]'
    print b.getMinHeapToValue(10)
    b.push(26)
    b.push(3)
    print b.getMinHeapToValue(11)
