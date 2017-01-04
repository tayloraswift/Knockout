@testable import Taylor
@testable import GradeTests

let test_cases:[([Int], Int, Bool, Int)] = [
([Int](), 0, false, 0),
([Int](), -92, false, 0),
([5], -2, false, 0),
([5], 7, false, 1),
([5], 5, false, 1),
([0, 1, 2, 3], 2, false, 3),
([0, 1, 2, 3], 2, true, 2),
([Int](repeating: 5, count: 13), 5, false, 13),
([Int](repeating: 5, count: 13), 5, true, 0),
]

func test_bisection<T: Comparable>(cases test_cases:[([T], T, Bool, Int)])
{
    for (i, (test_case, input, comparator, expected)) in test_cases.enumerated()
    {
        grade(test_case.bisect(input, with: comparator ? (<=) : (<)), expected, name: "bisection \(i)")
    }
}

func test_module()
{
    test_bisection(cases: test_cases)
}
