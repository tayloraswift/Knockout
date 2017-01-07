@testable import IO
@testable import GradeTests

let mock_rulers = [Ruler(), Ruler([0]), Ruler([0, 26, 26, 26, 27, 40]), Ruler([0, 20, 20, 30, 60, 200])]
let find_elem_tests = [ ([(6, 0), (26, 1)], [10, 50]),
                        ([(-50, 0), (-1, 1), (3, 1), (5, 1), (30, 2)], [-50, 0, 50]),
                        ([(-5, 0), (24, 1), (51, 6), (27, 4)], [0, 26, 26, 26, 40, 50, 50]),
                        ([(-20, 0), (-5, 1), (25, 4), (30, 4), (65, 5), (-2, 1), (180, 6)], [-20, 0, 20, 20, 30, 50, 60, 200])
                      ]

func test_ruler_aim(cases test_cases:[([(Int, Int)], [Int])], rulers:[Ruler])
{
    for (i, (ruler, (test_cases, expected))) in zip(rulers, test_cases).enumerated()
    {
        for (j, (input, expected)) in test_cases.enumerated()
        {
            ruler.press(u: input)
            grade(ruler.selected, expected, name: "ruler aim (ruler \(i), test \(j))")
        }
        ruler.motion_press(u: 51)
        ruler.release()
        grade(ruler.ruler, expected, name: "ruler edit (ruler \(i))")
    }
}

func test_module()
{
    test_ruler_aim(cases: find_elem_tests, rulers: mock_rulers)
}
