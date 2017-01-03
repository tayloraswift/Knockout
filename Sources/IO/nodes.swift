import Taylor

public
func t()
{
    let gene = Gene(name: "foo", format: AttrFormat.binomial, defstr: "", formatinfo: GeneFormatInfo(symbol: "C"))
    print(Binomial("21K + 3 - 1K -+ K", gene: gene).repr(gene: gene))
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
    let formatinfo:GeneFormatInfo

    init(name:String, format:AttrFormat, defstr:String, formatinfo:GeneFormatInfo)
    {
        self.name = name
        self.format = format
        self.defstr = defstr
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

    init(_ genes:[Gene])
    {
        var D:[String: Gene] = [:]
        for gene in genes
        {
            D[gene.name] = gene
        }
        self.DNA_lookup = D
        self.DNA = genes
    }

    init(_ attrs:(name:String, format:AttrFormat, defstr:String)...)
    {
        self.init(attrs.map{Gene(name: $0, format: $1, defstr: $2, formatinfo: GeneFormatInfo())})
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

protocol Element
{
    static var name:String { get }
    static var DNA:ElementDNA { get }
}

/////////////

class Node: Element
{
    static
    let name:String = "_nullbox"
    static
    let DNA:ElementDNA = ElementDNA()

    private
    var _ATTRS_:[String: String]

    private
    let _typedicts_ = ( bool        : BoolDict(),
                        int         : IntDict(),
                        float       : FloatDict(),
                        binomial    : BinomialDict(),
                        int_set     : FloatDict(),

                        float_array : FloatDict(),
                        str         : StrDict())

    init(_ attributes:[String: String])
    {
        self._ATTRS_ = attributes
        self.load_attributes()
    }

    private
    func load_attributes()
    {
        for gene in type(of: self).DNA // this discards extraneous attributes (bad for forwards compatibility)
        {
            self._assign(gene: gene, valstr: self._ATTRS_[gene.name] ?? gene.defstr)
        }
    }

    func assign(name:String, valstr:String)
    {
        if let gene = type(of: self).DNA.get(name: name)
        {
            self._assign(gene: gene, valstr: valstr)
        }
    }

    private
    func _assign(gene:Gene, valstr:String)
    {
        self.select_dict(format: gene.format)
        .assign(gene: gene, valstr: valstr, strdict: &self._ATTRS_)
    }

    private
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
