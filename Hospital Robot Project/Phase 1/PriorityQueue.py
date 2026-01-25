import heapq

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def push(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def pop_lowest_f(self):
        return heapq.heappop(self.elements)[1]

    def empty(self):
        return len(self.elements) == 0

    def push_or_update(self, item, priority):
        heapq.heappush(self.elements, (priority, item))