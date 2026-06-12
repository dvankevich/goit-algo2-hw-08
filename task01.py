import random
import time

class Node:
    def __init__(self, key, value):
        self.data = (key, value)
        self.next: Node | None = None
        self.prev: Node | None = None

class DoublyLinkedList:
    def __init__(self):
        self.head: Node | None = None
        self.tail: Node | None = None

    def push(self, key, value):
        new_node = Node(key, value)
        new_node.next = self.head
        if self.head:
            self.head.prev = new_node
        else:
            self.tail = new_node
        self.head = new_node
        return new_node

    def remove(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None

    def move_to_front(self, node):
        if node != self.head:
            self.remove(node)
            node.next = self.head
            if self.head:
                self.head.prev = node
            self.head = node

    def remove_last(self):
        if self.tail:
            last = self.tail
            self.remove(last)
            return last
        return None

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.list = DoublyLinkedList()

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self.list.move_to_front(node)
            return node.data[1]
        return -1

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.data = (key, value)
            self.list.move_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                last = self.list.remove_last()
                if last:
                    del self.cache[last.data[0]]
            new_node = self.list.push(key, value)
            self.cache[key] = new_node

cache = LRUCache(capacity=1000)

def range_sum_no_cache(array, left, right):
    return sum(array[left:right + 1])

def update_no_cache(array, index, value):
    array[index] = value

def range_sum_with_cache(array, left, right):
    key = (left, right)
    cached_result = cache.get(key)
    
    if cached_result != -1:
        return cached_result
    
    # Cache-miss: рахуємо суму та кладемо в кеш
    result = sum(array[left:right + 1])
    cache.put(key, result)
    return result

def update_with_cache(array, index, value):
    array[index] = value
    
    # Збираємо ключі, що підлягають видаленню.
    keys_to_remove = [k for k in cache.cache.keys() if k[0] <= index <= k[1]]
    
    # Послідовно видаляємо з обох структур даних, щоб зберегти синхронізацію
    for k in keys_to_remove:
        node = cache.cache[k]
        cache.list.remove(node)  # Видаляємо вузол із двозв'язного списку
        del cache.cache[k]       # Видаляємо запис із хеш-таблиці


def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n//2), random.randint(n//2, n-1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:
            idx = random.randint(0, n-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:
            if random.random() < p_hot:
                left, right = random.choice(hot)
            else:
                left = random.randint(0, n-1)
                right = random.randint(left, n-1)
            queries.append(("Range", left, right))
    return queries


if __name__ == "__main__":
    N = 100_000
    Q = 50_000
    
    # Створення масиву
    initial_array = [random.randint(1, 100) for _ in range(N)]
    # Генеруємо пул запитів
    queries = make_queries(N, Q)
    
    print(f"Тестування активовано (N = {N}, Q = {Q})...\n")

    # 1. Тест без кешу
    array_no_cache = initial_array.copy()
    start_time = time.perf_counter()
    for query in queries:
        if query[0] == "Range":
            range_sum_no_cache(array_no_cache, query[1], query[2])
        elif query[0] == "Update":
            update_no_cache(array_no_cache, query[1], query[2])
    time_no_cache = time.perf_counter() - start_time

    # 2. Тест із LRU-кешем
    array_with_cache = initial_array.copy()
    cache = LRUCache(capacity=1000)  # Скидаємо/переініціалізуємо кеш перед тестом
    
    start_time = time.perf_counter()
    for query in queries:
        if query[0] == "Range":
            range_sum_with_cache(array_with_cache, query[1], query[2])
        elif query[0] == "Update":
            update_with_cache(array_with_cache, query[1], query[2])
    time_with_cache = time.perf_counter() - start_time

    # Виведення результатів
    speedup = time_no_cache / time_with_cache
    print(f"Без кешу :  {time_no_cache:.2f} c")
    print(f"LRU-кеш  :   {time_with_cache:.2f} c  (прискорення ×{speedup:.1f})")