def binary_search(arr, target):
    """Performs binary search on a sorted list and returns index or -1."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

if __name__ == "__main__":
    data = [1, 3, 5, 7, 9, 11]
    print(binary_search(data, 7))
    print(binary_search(data, 4))
