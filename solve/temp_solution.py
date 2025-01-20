def factorial_sum(n):
    def factorial(x):
        result = 1
        for i in range(2, x + 1):
            result *= i
        return result

    total_sum = 0
    for i in range(1, n + 1):
        total_sum += factorial(i)
    
    return total_sum