# Given a UUID and total number of groups,
# returns the corresponding group based on the UUID
def bucketer(UUID, n):
  # Get the number of requisite hex characters for the UUID
  hex_chars = UUID[-num_chars(n):]

  # sum last largest_prime digits
  sum = 0
  for char in hex_chars:
    sum += int(char, 16)

  return sum % n

def num_chars(n):
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
