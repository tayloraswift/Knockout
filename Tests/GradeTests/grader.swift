public
func grade<T: Equatable>(_ output:T, _ expected:T, name:String)
{
    let padded_name = name.isEmpty ? name : name + " "

    if output == expected
    {
        print("\u{1B}[38;5;84mtest \(padded_name)passed!\u{1B}[0m")
    }
    else
    {
        print("\u{1B}[38;5;197mtest \(padded_name)failed\u{1B}[0m")
        print("Expected output:")
        print(expected)
        print("Produced output:")
        print(output)
        print()
    }
}
