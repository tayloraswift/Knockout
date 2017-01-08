import Taylor

public
func t()
{
    // all this does is test the binomials because i didn’t write actual tests for them
    let gene = Gene(name: "foo", format: AttrFormat.binomial, defstr: "", formatinfo: GeneFormatInfo(symbol: "C"))
    print(Binomial("21K + 3 - 1K -+ K", gene: gene).repr(gene: gene))

    for _ in 0..<10
    {
        var a:Node = Page([:])
        a = Node([:])
        a = Node([:])
        print(type(of: a).name)
        a = Page([:])
        print(type(of: a).name)
        _ = a
    }
}

enum AttrFormat
{
    case bool, int, float, binomial, int_set // reformatted
    case float_array, str//, rgba, one_D, multi_D, function, font_tag, para_tag // string storage
}

struct Gene
{
    let name:String
    let format:AttrFormat
    let defstr:String
    let imply:Bool
    let formatinfo:GeneFormatInfo

    init(name:String, format:AttrFormat, defstr:String,
        imply:Bool = false, formatinfo:GeneFormatInfo = GeneFormatInfo())
    {
        self.name = name
        self.format = format
        self.defstr = defstr
        self.imply = imply
        self.formatinfo = formatinfo
    }
}

struct GeneFormatInfo
{
    let radix:Int
    let symbol:UnicodeScalar
    let varsymbols:[UnicodeScalar]

    init(radix:Int = 10, symbol:UnicodeScalar = "K", varsymbols:[UnicodeScalar] = ["x"])
    {
        self.radix = radix
        self.symbol = symbol
        self.varsymbols = varsymbols
    }
}

struct ElementDNA: Sequence
{
    private
    let DNA:[Gene]
    private
    let DNA_lookup:[String: Gene]

    init(_ genes:Gene...)
    {
        var D:[String: Gene] = [:]
        for gene in genes
        {
            D[gene.name] = gene
        }
        self.DNA_lookup = D
        self.DNA = genes
        print("new")
    }

    subscript(i:Int) -> Gene
    {
        return self.DNA[i]
    }

    func get(name:String) -> Gene?
    {
        return self.DNA_lookup[name]
    }

    func makeIterator() -> IndexingIterator<[Gene]>
    {
        return self.DNA.makeIterator()
    }
}

/////////////

protocol ObjectMutableDictElement
{
    init(_:String, gene:Gene)
    func repr(gene:Gene) -> String
}

/////////////

protocol Element
{
    static var name:String { get }
    static var DNA:ElementDNA { get }
}

/////////////

class Node: Element
{
    private struct _Node_DNA // for some reason structs in classes are automatically static
    {
        static let name:String = "_nullbox"
        static let DNA:ElementDNA = ElementDNA()
    }
    class var name:String { return _Node_DNA.name }
    class var DNA:ElementDNA { return _Node_DNA.DNA }

    typealias DisplayInfo = (str:String?, exists:Bool, valid:Bool)

    private final
    var _DISPL_:[String: Node.DisplayInfo] = [:]

    private final
    let _typedicts_ = ( bool        : BoolDict(),
                        int         : IntDict(),
                        float       : FloatDict(),
                        binomial    : BinomialDict(),
                        int_set     : IntSetDict(),

                        float_array : FloatDict(),
                        str         : StrDict())

    init(_ attributes:[String: String])
    {
        self.load_attributes(attributes)
    }

    private final
    func load_attributes(_ attributes:[String: String])
    {
        for gene in type(of: self).DNA // this discards extraneous attributes (bad for forwards compatibility)
        {
            self._assign(valstr: attributes[gene.name], gene: gene)
        }
    }

    final
    func assign(valstr:String, name:String)
    {
        if let gene = type(of: self).DNA.get(name: name)
        {
            self._assign(valstr: valstr, gene: gene)
        }
    }

    private final
    func _assign(valstr:String?, gene:Gene)
    {
        self.select_dict(format: gene.format)
        .assign(valstr: valstr, gene: gene, dispdict: &self._DISPL_)
    }

    private final
    func select_dict(format:AttrFormat) -> AssignableFormatDict
    {
        switch format
        {
            case .bool:
                return self._typedicts_.bool
            case .int:
                return self._typedicts_.int
            case .float:
                return self._typedicts_.float
            case .binomial:
                return self._typedicts_.binomial
            case .int_set:
                return self._typedicts_.int_set

            case .float_array:
                return self._typedicts_.float_array
            case .str:
                return self._typedicts_.str
        }
    }
}

class Page:Node
{
    private struct _Node_DNA
    {
        static let name:String = "doc"
        static let DNA:ElementDNA = ElementDNA()
    }
    override class var name:String { return _Node_DNA.name }
    override class var DNA:ElementDNA { return _Node_DNA.DNA }
}
