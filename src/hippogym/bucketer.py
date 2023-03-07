# Given a UUID and total number of groups,
# returns the corresponding group based on the UUID
def bucketer(UUID: str, num_groups: int) -> int:
    # Get the number of requisite hex characters for the UUID
    hex_chars = UUID[-num_chars(num_groups) :]

    # sum last largest_prime digits
    primes_sum = 0
    for char in hex_chars:
        primes_sum += int(char, 16)

    return primes_sum % num_groups


def num_chars(n: int) -> int:
    # Determine all prime factors
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)

    # Get unique factors
    factors = list(set(factors))

    # Remove 2
    factors.pop(0)

    product = 1

    for factor in factors:
        product *= factor

    return product
