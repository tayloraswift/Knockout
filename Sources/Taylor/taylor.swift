import func Glibc.fopen
import func Glibc.fclose
import func Glibc.fseeko
import func Glibc.ftello
import func Glibc.fread
import func Glibc.rewind
import func Glibc.malloc
import func Glibc.free
import func Glibc.getenv
import typealias Glibc.FILE
import var Glibc.SEEK_END

public
let π:Double = Double.pi

public typealias Cpath    = String
public typealias Unixpath = String
public typealias CString = UnsafeMutablePointer<CChar>

infix operator ∪: AdditionPrecedence
public func ∪<T>(lhs:Set<T>, rhs:Set<T>) -> Set<T>
{
    return lhs.union(rhs)
}

infix operator ∩: MultiplicationPrecedence
public func ∩<T>(lhs:Set<T>, rhs:Set<T>) -> Set<T>
{
    return lhs.intersection(rhs)
}

infix operator ∈: ComparisonPrecedence
public func ∈<T>(lhs:T, rhs:Set<T>) -> Bool
{
    return rhs.contains(lhs)
}

public func unix_path(_ path:Cpath) -> Unixpath
{
    guard path.characters.count > 1
    else {
        return path
    }
    let path_i0 = path.startIndex
    let path_i2 = path.index(path_i0, offsetBy: 2)
    var expanded_path:Unixpath = path
    if path[path.startIndex..<path_i2] == "~/" {
        expanded_path = String(cString: getenv("HOME")) +
                        path[path.index(path_i0, offsetBy: 1)..<path.endIndex]
    }
    return expanded_path
}

public func open_text_file(_ path:Cpath) -> String?
{
    let path = unix_path(path)

    guard let f:UnsafeMutablePointer<FILE> = fopen(path, "rb")
    else {
        print("Error, could not open file '\(path)'")
        return nil
    }
    defer { fclose(f) }

    let fseek_status = fseeko(f, 0, SEEK_END)
    guard fseek_status == 0
    else {
        print("Error, fseeko() failed with error code \(fseek_status)")
        return nil
    }

    let n = ftello(f)
    guard 0..<CLong.max ~= n
    else {
        print("Error, ftello() returned file size outsize of allowed range")
        return nil
    }
    rewind(f)

    let cchar_buffer:CString = CString.allocate(capacity: n + 1) // leave room for sentinel
    defer { cchar_buffer.deallocate(capacity: n + 1) }

    let n_read = fread(cchar_buffer, MemoryLayout<CChar>.size, n, f)
    guard n_read == n
    else {
        print("Error, fread() read \(n_read) characters out of \(n)")
        return nil
    }
    cchar_buffer[n] = 0 // cap with sentinel
    return String(cString: cchar_buffer)
}

public class MovingAverage<N: FloatingPoint>
{
    let n:Int
    var k:Int = 0
    var i:Int = 0
    var Σ:N   = 0
    var data:[N]

    public
    var average:N {
        return Σ/N(k)
    }

    public
    init(samples:Int) {
        n = samples
        data = [N](repeating: 0, count: samples)
    }

    public
    func push(_ x:N) {
        Σ += x - data[i]
        data[i] = x
        i = (i + 1) % n
        k = min(k + 1, n)
    }

}
