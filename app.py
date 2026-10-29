import mimetypes
from flask import Flask, render_template, request, jsonify
import os
mimetypes.add_type("text/css", ".css")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static",
)

app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# ============================================================
# 1. ALGORITHM CONFIGURATION
# ============================================================

ALGORITHMS = {
    "bubble": "Bubble Sort",
    "selection": "Selection Sort",
    "insertion": "Insertion Sort",
    "merge": "Merge Sort",
    "quick": "Quick Sort",
    "counting": "Counting Sort",
    "linear": "Linear Search",
    "binary": "Binary Search"
}


# ============================================================
# 2. VISUALIZATION FRAME
# ============================================================

def frame(values, highlights=None, kind="none", message=""):
    return {
        "array": list(values),
        "highlights": list(highlights or []),
        "kind": kind,
        "message": message
    }


# ============================================================
# 3. BUBBLE SORT
# ============================================================

def bubble_sort(values):
    a = values[:]
    steps = [frame(a, message="Starting Bubble Sort.")]

    for i in range(len(a)):
        swapped = False

        for j in range(len(a) - i - 1):
            steps.append(
                frame(a, [j, j + 1], "compare",
                      f"Compare {a[j]} and {a[j + 1]}.")
            )

            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True

                steps.append(
                    frame(a, [j, j + 1], "swap",
                          "Swap the two values.")
                )

        if not swapped:
            break

    steps.append(frame(a, message="Bubble Sort completed."))

    return steps, "Average/worst: O(n²); best: O(n)", "O(1)"


# ============================================================
# 4. SELECTION SORT
# ============================================================

def selection_sort(values):
    a = values[:]
    steps = [frame(a, message="Starting Selection Sort.")]

    for i in range(len(a) - 1):
        minimum = i

        for j in range(i + 1, len(a)):
            steps.append(
                frame(a, [minimum, j], "compare",
                      f"Compare {a[minimum]} and {a[j]}.")
            )

            if a[j] < a[minimum]:
                minimum = j

        if minimum != i:
            a[i], a[minimum] = a[minimum], a[i]

            steps.append(
                frame(a, [i, minimum], "swap",
                      f"Move minimum {a[i]} to index {i}.")
            )

    steps.append(frame(a, message="Selection Sort completed."))

    return steps, "O(n²)", "O(1)"


# ============================================================
# 5. INSERTION SORT
# ============================================================

def insertion_sort(values):
    a = values[:]
    steps = [frame(a, message="Starting Insertion Sort.")]

    for i in range(1, len(a)):
        key = a[i]
        j = i - 1

        while j >= 0 and a[j] > key:
            steps.append(
                frame(a, [j, j + 1], "compare",
                      f"Compare {a[j]} with key {key}.")
            )

            a[j + 1] = a[j]

            steps.append(
                frame(a, [j, j + 1], "swap",
                      f"Shift {a[j]} right.")
            )

            j -= 1

        a[j + 1] = key

        steps.append(
            frame(a, [j + 1], "found",
                  f"Place {key} at index {j + 1}.")
        )

    steps.append(frame(a, message="Insertion Sort completed."))

    return steps, "Average/worst: O(n²); best: O(n)", "O(1)"


# ============================================================
# 6. MERGE SORT
# ============================================================

def merge_sort(values):
    a = values[:]
    steps = [frame(a, message="Starting Merge Sort.")]

    def sort(low, high):
        if high - low <= 1:
            return

        middle = (low + high) // 2

        sort(low, middle)
        sort(middle, high)

        left = a[low:middle]
        right = a[middle:high]

        merged = []
        i = j = 0

        while i < len(left) and j < len(right):
            steps.append(
                frame(a, list(range(low, high)), "compare",
                      f"Merging {left} and {right}.")
            )

            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1

        merged.extend(left[i:])
        merged.extend(right[j:])

        a[low:high] = merged

        steps.append(
            frame(a, list(range(low, high)), "swap",
                  f"Merged positions {low} to {high - 1}.")
        )

    sort(0, len(a))

    steps.append(frame(a, message="Merge Sort completed."))

    return steps, "O(n log n)", "O(n)"


# ============================================================
# 7. QUICK SORT
# ============================================================

def quick_sort(values):
    a = values[:]
    steps = [frame(a, message="Starting Quick Sort.")]

    def sort(low, high):
        if low >= high:
            return

        pivot = a[high]
        i = low

        for j in range(low, high):
            steps.append(
                frame(a, [j, high], "compare",
                      f"Compare {a[j]} with pivot {pivot}.")
            )

            if a[j] <= pivot:
                a[i], a[j] = a[j], a[i]

                steps.append(
                    frame(a, [i, j], "swap",
                          "Move value to pivot's left side.")
                )

                i += 1

        a[i], a[high] = a[high], a[i]

        steps.append(
            frame(a, [i, high], "swap",
                  f"Place pivot at index {i}.")
        )

        sort(low, i - 1)
        sort(i + 1, high)

    sort(0, len(a) - 1)

    steps.append(frame(a, message="Quick Sort completed."))

    return steps, "Average: O(n log n); worst: O(n²)", "Average: O(log n) recursion"


# ============================================================
# 8. COUNTING SORT
# ============================================================

def counting_sort(values):
    a = values[:]
    steps = [frame(a, message="Starting Counting Sort.")]

    if not a:
        return steps, "O(n + k)", "O(n + k)"

    low = min(a)
    high = max(a)

    if high - low > 10000:
        raise ValueError(
            "Counting Sort supports a value range up to 10,000. "
            "Choose another algorithm."
        )

    counts = [0] * (high - low + 1)

    for value in a:
        counts[value - low] += 1
        steps.append(frame(a, message=f"Count value {value}."))

    output = []

    for offset, count in enumerate(counts):
        value = offset + low

        for _ in range(count):
            output.append(value)

            current = output + a[len(output):]

            steps.append(
                frame(current, message=f"Add {value} to sorted output.")
            )

    steps.append(frame(output, message="Counting Sort completed."))

    return steps, "O(n + k)", "O(n + k)"


# ============================================================
# 9. LINEAR SEARCH
# ============================================================

def linear_search(values, target):
    a = values[:]

    steps = [
        frame(a, message=f"Searching for {target} using Linear Search.")
    ]

    for i, value in enumerate(a):
        steps.append(
            frame(a, [i], "compare",
                  f"Check index {i}: {value}.")
        )

        if value == target:
            steps.append(
                frame(a, [i], "found",
                      f"Found {target} at index {i}.")
            )

            return steps, "Best: O(1); worst: O(n)", "O(1)"

    steps.append(frame(a, message=f"{target} was not found."))

    return steps, "Best: O(1); worst: O(n)", "O(1)"


# ============================================================
# 10. BINARY SEARCH
# ============================================================

def binary_search(values, target):
    a = sorted(values)

    steps = [
        frame(a, message=f"Binary Search uses a sorted copy. Looking for {target}.")
    ]

    left = 0
    right = len(a) - 1

    while left <= right:
        middle = (left + right) // 2

        steps.append(
            frame(a, [middle], "compare",
                  f"Check middle index {middle}: {a[middle]}.")
        )

        if a[middle] == target:
            steps.append(
                frame(a, [middle], "found",
                      f"Found {target} at index {middle} in sorted array.")
            )

            return steps, "Search: O(log n); incl. sorting: O(n log n)", "O(1) extra for search"

        if a[middle] < target:
            left = middle + 1

            steps.append(
                frame(a, message="Target is larger; search right half.")
            )
        else:
            right = middle - 1

            steps.append(
                frame(a, message="Target is smaller; search left half.")
            )

    steps.append(frame(a, message=f"{target} was not found."))

    return steps, "Search: O(log n); incl. sorting: O(n log n)", "O(1) extra for search"


# ============================================================
# 11. PYTHON, JAVA AND C++ IMPLEMENTATIONS
# ============================================================

PYTHON_SNIPPETS = {
    "bubble": '''def bubble_sort(arr):
    for i in range(len(arr)):
        swapped = False
        for j in range(len(arr) - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr''',

    "selection": '''def selection_sort(arr):
    for i in range(len(arr) - 1):
        minimum = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[minimum]:
                minimum = j
        arr[i], arr[minimum] = arr[minimum], arr[i]
    return arr''',

    "insertion": '''def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr''',

    "merge": '''def merge_sort(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    return result + left[i:] + right[j:]''',

    "quick": '''def quick_sort(arr):
    if len(arr) <= 1:
        return arr

    pivot = arr[-1]
    left = [x for x in arr[:-1] if x <= pivot]
    right = [x for x in arr[:-1] if x > pivot]

    return quick_sort(left) + [pivot] + quick_sort(right)''',

    "counting": '''def counting_sort(arr):
    if not arr:
        return []

    low, high = min(arr), max(arr)
    count = [0] * (high - low + 1)

    for value in arr:
        count[value - low] += 1

    result = []

    for i, frequency in enumerate(count):
        result.extend([i + low] * frequency)

    return result''',

    "linear": '''def linear_search(arr, target):
    for index, value in enumerate(arr):
        if value == target:
            return index
    return -1''',

    "binary": '''def binary_search(arr, target):
    arr = sorted(arr)
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1'''
}


JAVA_SNIPPETS = {
    "bubble": '''static void bubbleSort(int[] arr) {
    for (int i = 0; i < arr.length; i++) {
        boolean swapped = false;

        for (int j = 0; j < arr.length - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
                swapped = true;
            }
        }

        if (!swapped) break;
    }
}''',

    "selection": '''static void selectionSort(int[] arr) {
    for (int i = 0; i < arr.length - 1; i++) {
        int min = i;

        for (int j = i + 1; j < arr.length; j++) {
            if (arr[j] < arr[min]) min = j;
        }

        int temp = arr[i];
        arr[i] = arr[min];
        arr[min] = temp;
    }
}''',

    "insertion": '''static void insertionSort(int[] arr) {
    for (int i = 1; i < arr.length; i++) {
        int key = arr[i];
        int j = i - 1;

        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }

        arr[j + 1] = key;
    }
}''',

    "merge": '''static void mergeSort(int[] arr, int left, int right) {
    if (left >= right) return;

    int mid = left + (right - left) / 2;

    mergeSort(arr, left, mid);
    mergeSort(arr, mid + 1, right);

    int[] temp = new int[right - left + 1];
    int i = left, j = mid + 1, k = 0;

    while (i <= mid && j <= right) {
        temp[k++] = arr[i] <= arr[j] ? arr[i++] : arr[j++];
    }

    while (i <= mid) temp[k++] = arr[i++];
    while (j <= right) temp[k++] = arr[j++];

    System.arraycopy(temp, 0, arr, left, temp.length);
}''',

    "quick": '''static void quickSort(int[] arr, int low, int high) {
    if (low >= high) return;

    int pivot = arr[high];
    int i = low;

    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            int temp = arr[i];
            arr[i++] = arr[j];
            arr[j] = temp;
        }
    }

    int temp = arr[i];
    arr[i] = arr[high];
    arr[high] = temp;

    quickSort(arr, low, i - 1);
    quickSort(arr, i + 1, high);
}''',

    "counting": '''static int[] countingSort(int[] arr) {
    if (arr.length == 0) return arr;

    int min = arr[0], max = arr[0];

    for (int value : arr) {
        min = Math.min(min, value);
        max = Math.max(max, value);
    }

    int[] count = new int[max - min + 1];

    for (int value : arr) count[value - min]++;

    int index = 0;

    for (int i = 0; i < count.length; i++) {
        while (count[i]-- > 0) arr[index++] = i + min;
    }

    return arr;
}''',

    "linear": '''static int linearSearch(int[] arr, int target) {
    for (int i = 0; i < arr.length; i++) {
        if (arr[i] == target) return i;
    }

    return -1;
}''',

    "binary": '''static int binarySearch(int[] arr, int target) {
    int[] sorted = arr.clone();
    Arrays.sort(sorted);

    int left = 0, right = sorted.length - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;

        if (sorted[mid] == target) return mid;
        if (sorted[mid] < target) left = mid + 1;
        else right = mid - 1;
    }

    return -1;
}'''
}


CPP_SNIPPETS = {
    "bubble": '''void bubbleSort(vector<int>& arr) {
    int n = arr.size();

    for (int i = 0; i < n; i++) {
        bool swapped = false;

        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
                swapped = true;
            }
        }

        if (!swapped) break;
    }
}''',

    "selection": '''void selectionSort(vector<int>& arr) {
    int n = arr.size();

    for (int i = 0; i < n - 1; i++) {
        int minIndex = i;

        for (int j = i + 1; j < n; j++) {
            if (arr[j] < arr[minIndex]) minIndex = j;
        }

        swap(arr[i], arr[minIndex]);
    }
}''',

    "insertion": '''void insertionSort(vector<int>& arr) {
    for (int i = 1; i < arr.size(); i++) {
        int key = arr[i];
        int j = i - 1;

        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }

        arr[j + 1] = key;
    }
}''',

    "merge": '''void mergeSort(vector<int>& arr, int left, int right) {
    if (left >= right) return;

    int mid = left + (right - left) / 2;

    mergeSort(arr, left, mid);
    mergeSort(arr, mid + 1, right);

    vector<int> temp;
    int i = left, j = mid + 1;

    while (i <= mid && j <= right) {
        if (arr[i] <= arr[j]) temp.push_back(arr[i++]);
        else temp.push_back(arr[j++]);
    }

    while (i <= mid) temp.push_back(arr[i++]);
    while (j <= right) temp.push_back(arr[j++]);

    for (int k = 0; k < temp.size(); k++) {
        arr[left + k] = temp[k];
    }
}''',

    "quick": '''void quickSort(vector<int>& arr, int low, int high) {
    if (low >= high) return;

    int pivot = arr[high];
    int i = low;

    for (int j = low; j < high; j++) {
        if (arr[j] <= pivot) {
            swap(arr[i], arr[j]);
            i++;
        }
    }

    swap(arr[i], arr[high]);

    quickSort(arr, low, i - 1);
    quickSort(arr, i + 1, high);
}''',

    "counting": '''vector<int> countingSort(vector<int> arr) {
    if (arr.empty()) return arr;

    int low = *min_element(arr.begin(), arr.end());
    int high = *max_element(arr.begin(), arr.end());

    vector<int> count(high - low + 1, 0);

    for (int value : arr) count[value - low]++;

    int index = 0;

    for (int i = 0; i < count.size(); i++) {
        while (count[i]-- > 0) arr[index++] = i + low;
    }

    return arr;
}''',

    "linear": '''int linearSearch(const vector<int>& arr, int target) {
    for (int i = 0; i < arr.size(); i++) {
        if (arr[i] == target) return i;
    }

    return -1;
}''',

    "binary": '''int binarySearch(vector<int> arr, int target) {
    sort(arr.begin(), arr.end());

    int left = 0, right = arr.size() - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;

        if (arr[mid] == target) return mid;
        if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }

    return -1;
}'''
}


# ============================================================
# 12. COMBINE ALL THREE LANGUAGE IMPLEMENTATIONS
# ============================================================

def get_code_output(algorithm):
    python_code = PYTHON_SNIPPETS[algorithm]
    java_code = JAVA_SNIPPETS[algorithm]
    cpp_code = CPP_SNIPPETS[algorithm]

    return (
        "========== PYTHON ==========\n\n"
        + python_code
        + "\n\n========== JAVA ==========\n\n"
        + java_code
        + "\n\n========== C++ ==========\n\n"
        + cpp_code
    )


# ============================================================
# 13. SORTING ALGORITHM REGISTRY
# ============================================================

SORTERS = {
    "bubble": bubble_sort,
    "selection": selection_sort,
    "insertion": insertion_sort,
    "merge": merge_sort,
    "quick": quick_sort,
    "counting": counting_sort
}


# ============================================================
# 14. FLASK ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/run")
def run_algorithm():
    data = request.get_json(silent=True) or {}

    try:
        raw = data.get("array", [])

        if not isinstance(raw, list) or not 2 <= len(raw) <= 50:
            raise ValueError(
                "Enter between 2 and 50 integer values."
            )

        values = []

        for item in raw:
            if isinstance(item, bool):
                raise ValueError("Array values must be integers.")

            number = int(item)

            if number != float(item):
                raise ValueError("Array values must be whole numbers.")

            values.append(number)

        algorithm = data.get("algorithm", "bubble")

        if algorithm not in ALGORITHMS:
            raise ValueError("Choose a valid algorithm.")

        if algorithm in ("linear", "binary"):
            target_value = data.get("target")

            if target_value is None or str(target_value).strip() == "":
                raise ValueError(
                    "Enter a target value for searching."
                )

            target = int(target_value)

            if isinstance(target_value, bool):
                raise ValueError("Target must be a whole number.")

            if float(target_value) != target:
                raise ValueError("Target must be a whole number.")

            if algorithm == "linear":
                steps, tc, sc = linear_search(values, target)
            else:
                steps, tc, sc = binary_search(values, target)

        else:
            steps, tc, sc = SORTERS[algorithm](values)

        return jsonify({
            "steps": steps,
            "algorithm": ALGORITHMS[algorithm],
            "python_code": get_code_output(algorithm),
            "time_complexity": tc,
            "space_complexity": sc
        })

    except (ValueError, TypeError, OverflowError) as exc:
        return jsonify({"error": str(exc)}), 400


# ============================================================
# 15. START THE APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)