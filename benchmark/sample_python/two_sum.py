def two_sum(nums, target):
    """Returns indices of the two numbers such that they add up to target."""
    seen = {}
    for idx, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], idx]
        seen[num] = idx
    return []

if __name__ == "__main__":
    nums = [2, 7, 11, 15]
    print(two_sum(nums, 9))  # Output: [0, 1]
