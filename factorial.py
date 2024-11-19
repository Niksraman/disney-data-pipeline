def my_factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * my_factorial(n - 1)

print(my_factorial(5))  # Correct function name
