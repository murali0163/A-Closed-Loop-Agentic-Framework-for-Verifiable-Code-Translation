def two_sum(nums, target):
    """Returns indices of two numbers that add up to target."""
    seen = {}
    for idx, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], idx]
        seen[num] = idx
    return []

if __name__ == "__main__":
    nums = [2, 7, 11, 15]
    print(two_sum(nums, 9))
