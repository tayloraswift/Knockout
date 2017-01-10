import Taylor

/*
Every element in our data model is build around a set of typed **attributes**. These attributes are stored as strings in the XML source representation of the data, and stored as typed Swift primitives or structs in the working model. Attributes are read against something called **DNA**, which is stored in an `ElementDNA` object at the class level. DNA contains the list of names and types of the attributes that we expect to read from the XML attribute dictionary, plus default values for those attributes if they are not explicitly defined (which is a common case). Each attribute corresponds to a `Gene` struct which contains this information. There is one `Gene` for each attribute that is expected to be read from that class of element. `Gene` and `ElementDNA` are defined in `nodes.swift`.

The typical life cycle of a document object looks something like this:
                  parse XML                               load attributes
    source:String     →    attribute dict:[String: String]        →      object:Element    →   source:String
               deserialization                            initialization             serialization

# Parsing XML
    This is handled by the `swiftxml` module. Parsing yields the class that the element belongs to, as well as an attribute dictionary containing its attributes in the form of type-erased strings.

# Load attributes
    This is performed by the method `Element.load_attributes()` defined in `nodes.swift`. We loop through the class’s `DNA` and for each gene, we attempt to (1) extract, (2) interpret, and (3) store the attribute data in the object’s data core.

    ## Extraction
        Extraction is the most complicated part of attribute loading. Before we talk about extraction we must first explain the concept of the **display dictionary**.

        ### Aside — The display dictionary
            The display dictionary (stored on the instance property `Element()._DISPL_:[String: DisplayInfo]`) does not store the typed attribute values themselves. It stores *representations* of those values, along with information about whether the value was explicitly defined, and if so, whether it was valid or not.

            We never do work on the display dictionary, in fact, once we initialize it, we only ever modify it if an **immutable property** is set (we will explain immutable properties later). The purpose of the display dictionary is to allow us to easily convert the element back to XML/HTML string representation.

        ## Aside — Mutable and immutable attributes
            When we work with element attributes, we make a distinction between **mutable** and **immutable properties**. A mutable property is any property that can be set in the user interface, without having to go through a string interpretation. That’s just another way of saying that if the data type is string-literal-convertible, it is considered mutable. Any attribute that is not mutable is immutable. In reality, almost all attributes are mutable.

            The important difference between the two is that mutable attributes are two-way, meaning you can convert them both to and from strings, while immutable attributes are one-way—you can convert a string into an immutable attribute value, but you cannot convert it back to a string.

            A good example of an immutable attribute type is the `fx` function type. A user can type an expression and we will interpret it as a lambda, but we cannot easily get back the original string expression from the lambda. The only way to change it is to push a new string into the attribute field.

        When we extract, we first check to see if the attribute (identified by its name, given in the DNA property `Gene().name:String`) is defined in the attribute dict. Generally, only a few attributes are ever explicitly defined. A typical element may have over a dozen genes, but each instance may have only two or three defined attributes. If the attribute is defined, we pass the string value on to the interpret phase.

        If the attribute is undefined, we pass the attribute’s **default value**, which is defined in its gene (`Gene().defstr:String`), since it never changes for elements of the same class.

    ## Interpretation
        When we interpret attribute string values, we convert them into Swift primitives and objects. Interpretation requires knowing the type of the value that the attribute is supposed to represent. This information is of course stored in the attribute DNA, on the property `Gene().format:AttrFormat`. The Swift type of the DNA `format` field is an enum `AttrFormat`, defined in `nodes.swift`. It is important to note that attribute types are not the same as Swift types, though each one is usually represented as a Swift type. Once we know the attribute type, we can call up the correct initializer to convert the string value into a true value. Interpretation can be as simple as filtering a string and calling `Int.init()` on it, though it can get quite involved for complex structures like `Binomial` (fittingly defined in `binomial.swift`.

    ## TypeDict architecture

Attributes are converted to typed form by sending them through the `assign()` method attached to every storage dictionary.

# DNA and subclasses

# Why???
    Dear maintainer,
    You are looking at the second-most complex (the bidirectional text layout algorithm takes the lead) and the first-most critical component of this application. This documentation will help you understand how it works, and why it exists. Please read it through before working on this module. This code was hard to write; it deserves to be easy to read.

    The attribute model is admittedly complex, in fact, back in the Python prototyping phase, every time I stopped working on it, I would forget how it worked after a few weeks, and whenever something broke, I would have to come back and stare at it at 2 A.M. and work out just how the damn thing was set up because for fuck’s sake, I didn’t understand any of it, and I wrote the fucking thing. (That’s part of the motivation for writing this piece of documentation, along with a general goal of making this app more accessible for new contributors.)

    Yet, I still consider it one of the most elegant systems I designed for this typesetter. To understand why Knockout’s attribute model is a strength, I have to tell the story of how Knockout was first written.

    In the early days, back when the codebase was still almost completely Python, Knockout didn’t have a unified attribute model. Every class (`Paragraph`, `Image`, `Table`, etc) had its own initializer, that took an array of parsed XML strings, cast them to Python `int`s and `float`s, and wrote them to instance properties hardcoded into the class.

    This was “efficient”, as there were never any hash table lookups (this is a lie, everything in Python is a hash table, but you didn’t hear it from me), but it was painfully inflexible. Want to add a `width` property to the paragraphs? You had to add another parameter in the initializer, copy and paste another `interpret_int()` function, and assign it to a new `self.` instance property. This was brittle enough in Python; it would have been even worse in a language like C or Swift, with variable declarations and function signatures coming into play. There was no support for default values. `None` traps roamed free.

    The most annoying thing was the was the monster `__init__(...........)` methods, so instead, I started passing dictionaries of XML attributes and values instead of each string fragment individually without context. These dictionaries are the predecessors of the attribute dicts in modern Knockout (the `_ attributes:[String: String]` parameter on `Element.init()`). This didn’t fix a lot of the other problems that plagued this system. There were still walls of boilerplate in every class. Initializers looked a lot like this:

    ```
    def __init__(self, attrs):
        self.linespacing    = interpret_float(attrs['linespacing'])
        self.indent         = interpret_float(attrs['indent'])
        self.indent_lines   = set(map(interpret_int, attrs['indent_lines'].split(',')))
        self.margin_top     = interpret_float(attrs['margin_bottom'])
        self.margin_bottom  = interpret_float(attrs['margin_bottom'])
        self.margin_left    = interpret_float(attrs['margin_left'])
        self.margin_right   = interpret_float(attrs['margin_right'])
        ...
    ```

    Equivalent Swift code would have looked even worse. Plus what happened if `'linespacing'` wasn’t in `attrs`? Unsurprisingly this crashed the app a lot. If you wanted to rename `'indent_lines'` to `'indent_for'`, you had to change the name in *two* data structures, or else it would crash, and I think we can all agree that crashing is not good.

    The most logical thing to do about the boilerplate was to make use of Python’s `getattr()` and `setattr()` builtins to automatically initialize the instance properties. That way you didn’t have to worry about keeping the names in sync. The code would have looked like this:

    ```
    def __init__(self, attrs):
        for name, value in attrs.items():
            setattr(self, name, interpret_float(value))
    ```

    Anyone with a hint of software engineering sense is probably crying right now. For one, this shit *only* flies in a hyperdynamic language like Python. The only reason Python has `setattr()` is because literally everything in Python is a hash map — I lied to you earlier, remember? Swift has never had, and almost certainly never will, have anything remotely resembling `setattr()`. C is still sleeping, so I won’t bother asking it about `setattr()`.

    There’s an even bigger problem here. See that `interpret_float()` up there? *Every* attribute is getting cast to a `float`. I could probably live with letting the integer attributes get cast to floating points — after all, Javascript programmers don’t seem to struggle with universal floaters — but what do we do about the `set`? This shut the door on complex attributes. Plus, this meant the entire attribute model was dictated by the XML. If an XML tag didn’t have exactly the right attributes, shit hit the fan. What would happen if the parser was sent a string like `'<p __init__="42">'`? Yikes!

    The issue was that *not all of the initializer code was boilerplate*. I needed some kind of way to specify the *type* that the attribute represented, so that everything isn’t automatically assumed to be a `float`. The attribute names needed to be written down, since letting the XML run the show was just asking for trouble. And while we were at it, wouldn’t it be nice to be able to specify some kind of *default value* for attributes in case the `attrs` dictionary didn’t pull through? Plus, element tags were getting awfully verbose: think `'<p linespacing="1" indent="0" indent_lines="" margin_top="10" margin_bottom="10" margin_left="0" margin_right="0">'`!

    Since this information wasn’t supposed to change between instances — it would be weird if each paragraph expected different parameters — it made sense to stuff it in at the class level. The initializer could then just read off of this list of “expected attributes”, cast them to the right type, and store them as instance properties. If the initializer didn’t receive an input for a particular attribute, no problem — it just substituted the default value defined for that attribute. Thus, DNA was born.

    DNA gets its name from the Blender structure, although Blender’s DNA works at a bit lower level than Knockout’s does and is really more intended as a forwards and backwards compatibility system. DNA is exactly what it sounds like. It’s the template for each class, what it expects to see in its corresponding XML representation. DNA is technically a sort of metaclassing, although a smart macro could probably flatten it. Although DNA was introduced to solve a specific problem, it has yielded enormous dividends. DNA can be run in reverse. Before, along with a horrific initializer, every class had an equally gnarly `__repr__()` method that did the work of converting the object back into an XML string. DNA made this task easy. You could write a decent serializer in one line of Python code using DNA. Here’s what it looks like:

    ```
    return self.__class__.name + ' ' + ' '.join(a[0] + '="' + str(attrs[a[0]]) + '"' for a in self.__class__.DNA if a[0] in attrs)
    ```

    (The current Swift implementation, `Element().description{get}`, spans about 18 lines, mostly for readability and edge cases.)

    DNA didn’t stop there. With DNA, every initializer looked the same (that’s why it’s a kind of metaclassing). So did every serializer. The variable factors all lived in the DNA itself. That meant that you didn’t need class initializers or serializers anymore — I could just use an initializer and serializer in a common base class. Although it’s irrelevant in Python, this also means that these methods can be resolved statically at compile-time, though you still need a dynamic class-level lookup to get the DNA itself. DNA has the added benefit of making Knockout extremely extensible. All you have to do to write a new element is write the layout and rendering code. You don’t have to worry about loading attributes, you can just define some DNA at the top of the class and all the attributes you need will just, work.

    Another takeaway is that, while the first iteration of DNA worked with `setattr()`, it didn’t have to. Dumping DNA attribute values into the instance namespace was just asking for a name collision with, you know, actual instance properties. It also hurt code readability because it was hard to tell if a `self.` reference was a DNA attribute or an instance member. Every iteration of DNA since has namespaced the DNA attributes into at least one member dictionary. Accessing an attribute thus involves a hash map lookup, but then again, accessing *any* member of a Python object involves a hash map lookup. All we really did was go from one hash map lookup to two hash map lookups. Like, hoe, it’s still O(1). (That’s bad advice kids, forget you read that.)

    The original Princess (Knockout 0.9) prototype pooled all the attributes into a single dictionary, which worked well with a healthy amount of pythonic duck-typing. The current Swift implementation uses about a dozen member dictionaries (all prefixed with `Element()._typedicts_.`) which offers type safety at the expense of a slightly more involved implementation.

    There are a few more aspects of the attribute model that warrant explanation, such as the concept of mutable and immutable attributes. As you can expect, they have to do with how data is written to and extracted from the data model. Princess actually had three kinds of attributes — literal, reformatted, and immutable attributes — mutable attributes are the descendants of the union of literal and reformatted attributes. I think they’re pretty well explained at the top of this documentation.

    Good luck,
    -T-
*/

protocol AssignableFormatDict: class
{
    func assign(valstr:String?, gene:Gene, dispdict:inout [String: Node.DisplayInfo])
    func extract(_ gene:Gene) -> String?
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
    subscript(name:String) -> T?
    {
        return self.dict[name]
    }

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
        dispdict[gene.name] = Node.DisplayInfo(str: valid ? Self.is_immutable(inputstr) : valstr,
                                               exists: exists, valid: valid)
    }

    final
    func extract(_ gene:Gene) -> String?
    {
        return nil
    }

    static
    func is_immutable(_ inputstr:String) -> String?
    // apparently static extension methods are able to override other static extension methods
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

    final
    func extract(_ gene:Gene) -> String?
    {
        guard let v:T = self[gene.name]
        else
        {
            return nil
        }
        return Self.repr(v, gene: gene)
    }
}

class CustomReprDict<T>
{
    //fileprivate
    final
    var dict:[String: T] = [:]
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
class FloatArrayDict:CustomReprDict<[Double]>, MutatableFormatDict
{
    static
    let absolute_defval:[Double] = []
    static
    func interpret(_ str:String, gene:Gene) -> [Double]?
    {
        return str.characters.split_on_whitespace().flatMap{FloatDict.interpret($0, gene: gene)}
    }

    static
    func repr(_ v:[Double], gene:Gene) -> String
    {
        return v.map{FloatDict.repr($0, gene: gene)}.joined(separator: " ")
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
