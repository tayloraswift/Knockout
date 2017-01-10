@testable import Model
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

func test_node_attributes()
{
    final
    class MockNode:Node
    {
        private struct _Node_DNA
        {
            static let name = "mock"
            static let DNA = ElementDNA(
                Gene(name: "width", format: .int, defstr: "89"),
                Gene(name: "height", format: .int, defstr: "20"),
                Gene(name: "show", format: .bool, defstr: "false"),
                Gene(name: "class", format: .str, defstr: "body", imply: true),
                Gene(name: "zoom", format: .float, defstr: "1"),
                Gene(name: "indent", format: .binomial, defstr: "20"),
                Gene(name: "indent_lines", format: .int_set, defstr: "0"),
                Gene(name: "h_ruler", format: .ruler, defstr: "0 80"),
                Gene(name: "distr", format: .float_array, defstr: "0")
            )
        }
        override static var name:String { return _Node_DNA.name }
        override static var DNA:ElementDNA { return _Node_DNA.DNA }
    }

    let N0 = MockNode([:])
    let N1 = MockNode(["width": "80", "class": "p"])
    let N2 = MockNode(["width": "-6", "height": "- 40", "show": "1",
                        "class": "p", "zoom": "2.5", "indent": "1K + 3 + 6",
                        "indent_lines": "0, 3,4", "h_ruler": "0, 3.5, 40"])
    print(N0.description)
    print(N1.description)
    print(N2.description)
}

func test_module()
{
    test_ruler_aim(cases: find_elem_tests, rulers: mock_rulers)
    test_node_attributes()
}
