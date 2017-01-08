import Taylor

/*
a helpful comment explaining our elegant but very unobvious and poorly named attribute model
*/

protocol AssignableFormatDict: class
{
    func assign(valstr:String?, gene:Gene, dispdict:inout [String: Node.DisplayInfo])
}

protocol ImmutableFormatDict:AssignableFormatDict
{
    associatedtype T

    static
    func is_immutable(_:String) -> String? // this is a stupid function
    static
    func interpret(_ str:String, gene:Gene) -> T?

    static
    var absolute_defval:T { get }
    var dict:[String: T] { get set }
}

extension ImmutableFormatDict
{
    func assign(valstr:String?, gene:Gene, dispdict:inout [String: Node.DisplayInfo])
    {
        let inputstr:String, exists:Bool
        if let valstr = valstr
        {
            inputstr = valstr
            exists = true
        }
        else
        {
            inputstr = gene.defstr
            exists = false
        }

        let value:T, valid:Bool
        if let v:T = Self.interpret(inputstr, gene: gene)
        {
            value = v
            valid = true
        }
        else
        {
            value = Self.interpret(gene.defstr, gene: gene) ?? Self.absolute_defval
            valid = false
            // we should never need Self.absolute_defval but i am paranoid
        }
        self.dict[gene.name] = value
        dispdict[gene.name] = Node.DisplayInfo(str: Self.is_immutable(inputstr),
                                               exists: exists, valid: valid)
    }

    static
    func is_immutable(_ inputstr:String) -> String?
    {
        return inputstr
    }
}

protocol MutatableFormatDict:ImmutableFormatDict
{
    static
    func repr(_ v:T, gene:Gene) -> String
}

extension MutatableFormatDict
{
    static
    func is_immutable(_:String) -> String?
    {
        return nil
    }
}

class BasicImmutableDict<T>
{
    //fileprivate
    var dict:[String: T] = [:]
    subscript(name:String) -> T?
    {
        get
        {
            return self.dict[name]
        }
    }
}

class BasicMutableDict<T>:BasicImmutableDict<T>
{
    class
    func repr(_ v:T, gene:Gene) -> String
    {
        return String(describing: v)
    }
}

class ObjectMutableDict<T: ObjectMutableDictElement>:BasicMutableDict<T>
{
    static
    func interpret(_ str:String, gene:Gene) -> T?
    {
        return T(str, gene: gene)
    }

    override static
    func repr(_ v:T, gene:Gene) -> String
    {
        return v.repr(gene: gene)
    }
}

final
class BoolDict:BasicMutableDict<Bool>, MutatableFormatDict
{
    static
    let absolute_defval:Bool = false
    static
    func interpret(_ str:String, gene:Gene) -> Bool?
    {
        if str == "true" || str == "True"
        {
            return true
        }
        else if str == "false" || str == "False"
        {
            return false
        }
        else if let n = IntDict.interpret(str, gene: gene)
        {
            return n != 0
        }
        else
        {
            return nil
        }
    }
}

final
class IntDict:BasicMutableDict<Int>, MutatableFormatDict
{
    static
    let absolute_defval:Int = 0
    static
    func interpret(_ str:String, gene:Gene) -> Int?
    {
        return Int(str, radix:gene.formatinfo.radix) // add arithmetic functionality later
    }
}

final
class FloatDict:BasicMutableDict<Double>, MutatableFormatDict
{
    static
    let absolute_defval:Double = 0
    static
    func interpret(_ str:String, gene:Gene) -> Double?
    {
        return Double(str) // add arithmetic functionality later
    }

    override static
    func repr(_ f:Double, gene:Gene) -> String
    {
        if f <= Double(Int.max) && abs(f.truncatingRemainder(dividingBy: 1)) < 0.00_000_1
        {

            return String(describing: Int(f))
        }
        else
        {
            return String(describing: f)
        }
    }
}

final
class BinomialDict:ObjectMutableDict<Binomial>, MutatableFormatDict
{
    static
    let absolute_defval:Binomial = Binomial(β_0: 0, β_1: 0)
}

final
class IntSetDict:BasicMutableDict<Set<Int>>, MutatableFormatDict
{
    static
    let absolute_defval:Set<Int> = Set()
    static
    func interpret(_ str:String, gene:Gene) -> Set<Int>?
    {
        return Set(str.characters.split(separator: ",").flatMap
        {
            IntDict.interpret($0.trim(), gene: gene)
        })
    }

    override static
    func repr(_ v:Set<Int>, gene:Gene) -> String
    {
        return v.map{String(describing: $0)}.joined(separator: ", ")
    }
}

final
class StrDict:BasicImmutableDict<String>, ImmutableFormatDict
{
    static
    let absolute_defval:String = "" // this is never used but we need it for the protocol
    static
    func interpret(_ str:String, gene:Gene) -> String?
    {
        return str
    }
}
