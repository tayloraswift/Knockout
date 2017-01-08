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
    final
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
            if let v:T = Self.interpret(gene.defstr, gene: gene)//!
            {
                value = v
            }
            else
            {
                value = Self.absolute_defval
                // we should never need Self.absolute_defval but i am paranoid
                print("gene \(gene) has a bad default value '\(gene.defstr)'")
            }
            valid = false
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

class CustomReprDict<T>
{
    //fileprivate
    final
    var dict:[String: T] = [:]
    final
    subscript(name:String) -> T?
    {
        get
        {
            return self.dict[name]
        }
    }
}

class DefaultReprDict<T>:CustomReprDict<T>
{
    static
    func repr(_ v:T, gene:Gene) -> String
    {
        return String(describing: v)
    }
}

class ObjectReprDict<T: ObjectReprElement>:CustomReprDict<T>
{
    static
    func interpret(_ str:String, gene:Gene) -> T?
    {
        return T(str, gene: gene)
    }

    static
    func repr(_ v:T, gene:Gene) -> String
    {
        return v.repr(gene: gene)
    }
}

final
class BoolDict:DefaultReprDict<Bool>, MutatableFormatDict
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
class IntDict:DefaultReprDict<Int>, MutatableFormatDict
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
class FloatDict:CustomReprDict<Double>, MutatableFormatDict
{
    static
    let absolute_defval:Double = 0
    static
    func interpret(_ str:String, gene:Gene) -> Double?
    {
        return Double(str) // add arithmetic functionality later
    }

    static
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
class BinomialDict:ObjectReprDict<Binomial>, MutatableFormatDict
{
    static
    let absolute_defval:Binomial = Binomial(β_0: 0, β_1: 0)
}

final
class IntSetDict:CustomReprDict<Set<Int>>, MutatableFormatDict
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

    static
    func repr(_ v:Set<Int>, gene:Gene) -> String
    {
        return v.map{String(describing: $0)}.joined(separator: ", ")
    }
}

final
class StrDict:DefaultReprDict<String>, ImmutableFormatDict
{
    static
    let absolute_defval:String = "" // this is never used but we need it for the protocol
    static
    func interpret(_ str:String, gene:Gene) -> String?
    {
        return str
    }
}

final
class RulerDict:ObjectReprDict<Ruler>, MutatableFormatDict
{
    static
    let absolute_defval:Ruler = Ruler()
}
