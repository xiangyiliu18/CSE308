

def hailstone(n, count):
	if( n == 1):
		print(n)
		print(count)
		return count

	if n % 2 == 0:#if even
		print(n)
		hailstone(n/2, count + 1)
	else:#if odd
		print(n)
		hailstone(3*n + 1, count +1)

print("the count is " ,hailstone(10, 0))