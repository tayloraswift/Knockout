func pass_msg(_ name:String)
{
    print("\u{1B}[38;5;84mtest \(name)passed!\u{1B}[0m")
}

func fail_msg(_ name:String)
{
    print("\u{1B}[38;5;197mtest \(name)failed\u{1B}[0m")
}

public
func grade<T: Equatable>(_ output:T?, _ expected:T?, name:String)
{
    let padded_name = name.isEmpty ? name : name + " "

    if output == expected
    {
        pass_msg(padded_name)
    }
    else
    {
        fail_msg(padded_name)
        print("Expected output:")
        if let expected = expected
        { print(expected) }
        else
        { print("nil") }
        print("Produced output:")
        if let output = output
        { print(output) }
        else
        { print("nil") }
        print()
    }
}

public
func grade<T: Equatable>(_ output:[T], _ expected:[T], name:String)
{
    let padded_name = name.isEmpty ? name : name + " "

    if output == expected
    {
        pass_msg(padded_name)
    }
    else
    {
        fail_msg(padded_name)
        print("Expected output:")
        print(expected)
        print("Produced output:")
        print(output)
        print()
    }
}
