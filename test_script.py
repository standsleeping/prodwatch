import random
import time
from prodwatch.prodwatch import start_prodwatch

def calculate_sum(a, b):
    result = int(a) + int(b)
    print(f"{a} + {b} = {result}")
    return result


if __name__ == "__main__":
    start_prodwatch()

    for _ in range(100):
        a = random.randint(0, 100)
        b = random.randint(0, 100)
        print(f"Calling calculate_sum with {a} and {b}")
        calculate_sum(a, b)
        time.sleep(5)
