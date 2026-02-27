"""Solution for selecting maximum number of equal-sum segments with spacing."""

import sys
from array import array

SUM_BIAS = 1 << 63
RADIX_MASK = (1 << 16) - 1
RADIX_SIZE = 1 << 16


def read_input() -> tuple:
    """Read and parse input.

    Returns:
        tuple: (array_length, max_chant_length, min_gap, values)
            - array_length: int, n
            - max_chant_length: int, M
            - min_gap: int, D
            - values: list of int, array values in 0-based storage
    """
    data = sys.stdin.buffer.read().split()
    array_length = int(data[0])
    max_chant_length = int(data[1])
    min_gap = int(data[2])
    values = [int(token) for token in data[3:3 + array_length]]
    return array_length, max_chant_length, min_gap, values


def count_total_chants(array_length: int, max_chant_length: int) -> int:
    """Count the number of valid chants of length at most max_chant_length.

    Args:
        array_length: Length of the array, n.
        max_chant_length: Maximum chant length, M.

    Returns:
        int: Total number of chants, N.
    """
    total_chants = 0
    for start_position in range(1, array_length + 1):
        remaining = array_length - start_position + 1
        total_chants += min(max_chant_length, remaining)
    return total_chants


def build_chants(values: list, max_chant_length: int) -> tuple:
    """Enumerate all valid chants and store them in compact arrays.

    Each chant stores:
        - sum_key: unsigned key for sorting by sum (sum + 2^63)
        - left_position: l (1-based)
        - right_position: r (1-based)

    Args:
        values: list of int, array values (0-based indexing).
        max_chant_length: int, maximum allowed chant length M.

    Returns:
        tuple: (sum_keys, left_positions, right_positions)
            - sum_keys: array('Q') of length N
            - left_positions: array('I') of length N
            - right_positions: array('I') of length N
    """
    array_length = len(values)
    total_chants = count_total_chants(array_length, max_chant_length)

    sum_keys = array("Q", [0]) * total_chants
    left_positions = array("I", [0]) * total_chants
    right_positions = array("I", [0]) * total_chants

    write_index = 0
    for left_position in range(1, array_length + 1):
        running_sum = 0
        max_right = min(array_length, left_position + max_chant_length - 1)

        for right_position in range(left_position, max_right + 1):
            running_sum += values[right_position - 1]
            sum_keys[write_index] = running_sum + SUM_BIAS
            left_positions[write_index] = left_position
            right_positions[write_index] = right_position
            write_index += 1

    return sum_keys, left_positions, right_positions


def stable_counting_sort_indices(
    input_indices: array,
    key_values: array,
    max_key_value: int
) -> array:
    """Stable counting sort of chant indices by a bounded integer key.

    Args:
        input_indices: array('I'), indices to sort.
        key_values: array, key for each chant index.
        max_key_value: int, maximum possible key value.

    Returns:
        array('I'): indices sorted stably by key_values.
    """
    indices_count = len(input_indices)
    counts = array("I", [0]) * (max_key_value + 1)

    for position in range(indices_count):
        chant_index = input_indices[position]
        counts[key_values[chant_index]] += 1

    running_total = 0
    for key in range(max_key_value + 1):
        running_total += counts[key]
        counts[key] = running_total

    output_indices = array("I", [0]) * indices_count
    for position in range(indices_count - 1, -1, -1):
        chant_index = input_indices[position]
        key = key_values[chant_index]
        counts[key] -= 1
        output_indices[counts[key]] = chant_index

    return output_indices


def stable_radix_sort_indices_by_sum(
    input_indices: array,
    sum_keys: array
) -> array:
    """Stable radix sort of chant indices by 64-bit unsigned sum_keys.

    Uses 16-bit digits, resulting in 4 passes.

    Args:
        input_indices: array('I'), indices to sort.
        sum_keys: array('Q'), sum key for each chant (sum + 2^63).

    Returns:
        array('I'): indices sorted stably by sum_keys.
    """
    indices = input_indices
    indices_count = len(indices)

    for shift in (0, 16, 32, 48):
        counts = array("I", [0]) * RADIX_SIZE

        for position in range(indices_count):
            chant_index = indices[position]
            digit = (sum_keys[chant_index] >> shift) & RADIX_MASK
            counts[digit] += 1

        running_total = 0
        for digit_value in range(RADIX_SIZE):
            running_total += counts[digit_value]
            counts[digit_value] = running_total

        output_indices = array("I", [0]) * indices_count
        for position in range(indices_count - 1, -1, -1):
            chant_index = indices[position]
            digit = (sum_keys[chant_index] >> shift) & RADIX_MASK
            counts[digit] -= 1
            output_indices[counts[digit]] = chant_index

        indices = output_indices

    return indices


def sort_chants(
    sum_keys: array,
    left_positions: array,
    right_positions: array,
    array_length: int
) -> array:
    """Sort chants by (sum, right_position, left_position).

    This is done via stable passes:
        1) left_position
        2) right_position
        3) sum_keys

    Args:
        sum_keys: array('Q') of sum keys.
        left_positions: array('I') of left endpoints.
        right_positions: array('I') of right endpoints.
        array_length: int, n.

    Returns:
        array('I'): chant indices in sorted order.
    """
    total_chants = len(sum_keys)
    indices = array("I", range(total_chants))

    indices = stable_counting_sort_indices(indices, left_positions, array_length)
    indices = stable_counting_sort_indices(indices, right_positions, array_length)
    indices = stable_radix_sort_indices_by_sum(indices, sum_keys)

    return indices


def find_best_sum_group(
    sorted_indices: array,
    sum_keys: array,
    left_positions: array,
    right_positions: array,
    min_gap: int
) -> tuple:
    """Find the sum block that yields maximum chant count, then smallest sum.

    Args:
        sorted_indices: array('I'), indices sorted by (sum, r, l).
        sum_keys: array('Q'), sum keys.
        left_positions: array('I'), l for each chant.
        right_positions: array('I'), r for each chant.
        min_gap: int, D.

    Returns:
        tuple: (best_sum_key, best_group_start, best_group_end)
            The group range is [best_group_start, best_group_end) in sorted order.
    """
    total_chants = len(sorted_indices)
    best_count = -1
    best_sum_key = 0
    best_group_start = 0
    best_group_end = 0

    position = 0
    negative_infinity = -10**30

    while position < total_chants:
        group_start = position
        current_sum_key = sum_keys[sorted_indices[position]]

        last_end = negative_infinity
        current_count = 0

        while position < total_chants:
            chant_index = sorted_indices[position]
            if sum_keys[chant_index] != current_sum_key:
                break

            left_position = left_positions[chant_index]
            right_position = right_positions[chant_index]
            if left_position > last_end + min_gap:
                current_count += 1
                last_end = right_position

            position += 1

        group_end = position

        if current_count > best_count:
            best_count = current_count
            best_sum_key = current_sum_key
            best_group_start = group_start
            best_group_end = group_end

    return best_sum_key, best_group_start, best_group_end


def reconstruct_answer(
    sorted_indices: array,
    left_positions: array,
    right_positions: array,
    group_start: int,
    group_end: int,
    min_gap: int
) -> list:
    """Reconstruct the greedy-selected chants for a chosen sum block.

    Args:
        sorted_indices: array('I'), indices sorted by (sum, r, l).
        left_positions: array('I'), l for each chant.
        right_positions: array('I'), r for each chant.
        group_start: int, start index of sum block in sorted order.
        group_end: int, end index (exclusive) of sum block in sorted order.
        min_gap: int, D.

    Returns:
        list: list of (l, r) pairs in required output order.
    """
    selected_chants = []
    negative_infinity = -10**30
    last_end = negative_infinity

    for position in range(group_start, group_end):
        chant_index = sorted_indices[position]
        left_position = left_positions[chant_index]
        right_position = right_positions[chant_index]

        if left_position > last_end + min_gap:
            selected_chants.append((left_position, right_position))
            last_end = right_position

    return selected_chants


def main() -> None:
    """Run the algorithm and print the unique optimal set of chants."""
    array_length, max_chant_length, min_gap, values = read_input()

    sum_keys, left_positions, right_positions = build_chants(
        values,
        max_chant_length
    )
    sorted_indices = sort_chants(
        sum_keys,
        left_positions,
        right_positions,
        array_length
    )

    best_sum_key, group_start, group_end = find_best_sum_group(
        sorted_indices,
        sum_keys,
        left_positions,
        right_positions,
        min_gap
    )

    selected_chants = reconstruct_answer(
        sorted_indices,
        left_positions,
        right_positions,
        group_start,
        group_end,
        min_gap
    )

    best_sum = int(best_sum_key - SUM_BIAS)
    output_lines = [f"{len(selected_chants)} {best_sum}\n"]
    for left_position, right_position in selected_chants:
        output_lines.append(f"{left_position} {right_position}\n")

    sys.stdout.write("\n".join(output_lines))


if __name__ == "__main__":
    main()