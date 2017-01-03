import Taylor

import var Cairo.CAIRO_FONT_SLANT_NORMAL
import var Cairo.CAIRO_FONT_WEIGHT_BOLD
import var Cairo.CAIRO_FONT_WEIGHT_NORMAL

import GLFW

import Geometry
import SwiftCairo

import var SGLOpenGL.GL_BGRA
import var SGLOpenGL.GL_UNSIGNED_INT_8_8_8_8_REV
import var SGLOpenGL.GL_COLOR_BUFFER_BIT
import var SGLOpenGL.GL_COLOR_ATTACHMENT0
import var SGLOpenGL.GL_VERTEX_SHADER
import var SGLOpenGL.GL_FRAGMENT_SHADER
import var SGLOpenGL.GL_SRC_ALPHA
import var SGLOpenGL.GL_ONE_MINUS_SRC_ALPHA
import var SGLOpenGL.GL_BLEND
import func SGLOpenGL.glViewport
import func SGLOpenGL.glClearColor
import func SGLOpenGL.glClear
import func SGLOpenGL.glBlendFunc
import func SGLOpenGL.glEnable

import func IO.t

IO.t()

func error_callback(_ error:Int32, _ description:UnsafePointer<CChar>?)
{
    var message:String
    if let description = description {
        message = String(cString: description)
    }
    else {
        message = ""
    }
    print("Error \(error): \(message)")
}

typealias Window = OpaquePointer?

typealias FloatCoordinate = (x:Float, y:Float)
typealias IntCoordinate = (x:Int, y:Int)
typealias IntCoordinateOffset = (h:Int, k:Int)
typealias IntRectangle = (x:Int, y:Int, h:Int, k:Int)

func - (p1:IntCoordinate, p2:IntCoordinate) -> IntCoordinate
{
    return IntCoordinate(x: p1.x - p2.x, y: p1.y - p2.y)
}

fileprivate
typealias RegionInfo = (fell_on_partition:UInt8, view:View)
// 0 = no partition, 1 = h partition, 2 = v partition

fileprivate
func == (region1:RegionInfo, region2:RegionInfo) -> Bool
{
    return region1.fell_on_partition == region2.fell_on_partition && region1.view === region2.view
}

class Interface
{
    private
    var associated_window:Window
    let view:View
    private
    var window_size:IntCoordinateOffset

    private
    let shader = Shader(shaders_by_path:
                        [("Sources/Geometry/shader.vert", GL_VERTEX_SHADER),
                         ("Sources/Geometry/shader.frag", GL_FRAGMENT_SHADER)])

    private
    var mouse_drags:(anchor:IntCoordinate, button:Int)?

    var _letter:Character = "\u{0}" // testing

    static private
    let CURSORS =
    (
         normal: glfwCreateStandardCursor(GLFW_ARROW_CURSOR),
         hresize: glfwCreateStandardCursor(GLFW_HRESIZE_CURSOR),
         vresize: glfwCreateStandardCursor(GLFW_VRESIZE_CURSOR)
    )
    private
    var current_region_active:RegionInfo
    private
    var current_region_hover:RegionInfo
    {
        didSet
        {
            self.choose_cursor(region: current_region_hover)
        }
    }

    init(view V:View, size:IntCoordinateOffset, window:Window)
    {
        V.assemble(size: size, shader: shader)
        self.view = V
        self.window_size = size
        self.current_region_hover = RegionInfo(0, V)
        self.current_region_active = self.current_region_hover
        self.attach(to: window)
        self.choose_cursor(region: self.current_region_hover)
    }

    private
    func choose_cursor(region:RegionInfo)
    {
        if region.fell_on_partition != 0
        {
            glfwSetCursor(self.associated_window,
                          region.fell_on_partition == 1 ? Interface.CURSORS.hresize : Interface.CURSORS.vresize)
        }
        else
        {
            glfwSetCursor(self.associated_window, Interface.CURSORS.normal)
        }
    }

    func resize_proportionally(to size:Size)
    {
        self.window_size = IntCoordinateOffset(h: Int(size.h), k: Int(size.k))
        view.reassemble(size: self.window_size)
    }

    func hover(_ p:IntCoordinate)
    {
        if let _ = self.mouse_drags
        {
            if current_region_active.fell_on_partition != 0
            {
                current_region_active.view.pan(p, against: self.window_size, bumper_radius: 30)
            }
        }
        else
        {
            current_region_hover = self.bisect(p)
        }
    }

    func press(_ p:IntCoordinate)
    {
        self.mouse_drags = (anchor: p, button: 1)
        self.current_region_active = self.bisect(p)
        assert(self.current_region_hover == self.current_region_active)
    }

    func press_mid(_ p:IntCoordinate)
    {
        self.mouse_drags = (anchor: p, button: 2)
        self.current_region_active = self.bisect(p)
        assert(self.current_region_hover == self.current_region_active)
    }

    func press_right(_ p:IntCoordinate)
    {
        self.mouse_drags = (anchor: p, button: 3)
    }

    func release()
    {
        self.mouse_drags = nil
    }

    private
    func bisect(_ p:IntCoordinate) -> RegionInfo
    {
        var V:View = self.view
        while true
        {
            if let (fell_on_partition, next) = V.which(p, partition_radius: 4)
            {
                V = next
                if fell_on_partition != 0
                {
                    return RegionInfo(fell_on_partition, V)
                }
            }
            else
            {
                return RegionInfo(0, V)
            }
        }
    }

    private
    func attach(to window:Window)
    {
        glfwSetWindowUserPointer(window, UnsafeMutableRawPointer(
                    Unmanaged.passUnretained(self).toOpaque()))
        self.associated_window = window
    }

    static
    func reconstitute(from window:Window) -> Interface
    {
        return Unmanaged<Interface>
                    .fromOpaque(glfwGetWindowUserPointer(window))
                    .takeUnretainedValue()
    }
}

func hover_link(window:Window, x:Double, y:Double)
{
    Interface.reconstitute(from: window).hover(IntCoordinate(Int(x), Int(y)))
}

func press_link(window:Window, button:Int32, action:Int32, mods:Int32)
{
    let interface = Interface.reconstitute(from: window)
    if action == GLFW_PRESS
    {
        var x:Double = 0, y:Double = 0
        glfwGetCursorPos(window, &x, &y)
        let p:IntCoordinate = IntCoordinate(Int(x), Int(y))
        switch button
        {
            case GLFW_MOUSE_BUTTON_LEFT:
                interface.press(p)
            case GLFW_MOUSE_BUTTON_MIDDLE:
                interface.press_mid(p)
            case GLFW_MOUSE_BUTTON_RIGHT:
                interface.press_right(p)
            default:
                break
        }
    }
    else // if action == GLFW_RELEASE
    {
        interface.release()
    }
}

class View
{
    private
    var partition:Double = 0 // normalized to window, not view
    private
    var vertical:Bool = false

    private
    var rectangle:IntRectangle = IntRectangle(x: 0, y: 0, h: 0, k: 0)

    typealias Leaves = (View, View)
    private
    var leaves:Leaves?
    var surface:Layer? // we should probably use an enum for this radio behavior but whatever

    subscript(path: Int...) -> View // remove this later, this is only to help testing
    {
        var V:View = self
        for i in path
        {
            if let leaves = V.leaves
            {
                V = i == 0 ? leaves.0 : leaves.1
            }
            else
            {
                break
            }
        }
        return V
    }

    fileprivate
    func _color_me(_ r:Double, _ g:Double, _ b:Double, _ a:Double = 1)
    {
        guard let surface = self.surface
        else
        {
            print("Warning: View at \(self.rectangle) is not a leaf")
            return
        }
        surface.cr.set_source_rgba(r, g, b, a)
        surface.cr.paint()
        surface.transfer()
        surface.apply()
    }

    convenience
    init(containing L:Leaves? = nil, partition:Double, is_vertical:Bool = false)
    {
        self.init()
        self.vertical = is_vertical
        self.leaves = L ?? Leaves(View(), View())
        assert(0...1 ~= partition)
        self.partition = partition
    }

    fileprivate
    func which(_ p:IntCoordinate, partition_radius:Int) -> RegionInfo?
    {
        assert((self.leaves == nil) != (self.surface == nil))
        if let leaves = self.leaves
        {
            let fall:Int = vertical ?
                    p.y - self.rectangle.y - leaves.0.rectangle.k : p.x - self.rectangle.x - leaves.0.rectangle.h
            if fall < -partition_radius
            {
                return RegionInfo(0, leaves.0)
            }
            else if fall > partition_radius
            {
                return RegionInfo(0, leaves.1)
            }
            else
            {
                return RegionInfo(1 + (self.vertical ? 1 : 0), self)
            }
        }
        else
        {
            return nil
        }
    }

    private
    func calculate_rectangles(from R:IntRectangle, against N:IntCoordinateOffset, leaves:Leaves) -> (IntRectangle, IntRectangle)
    {
        var (R1, R2):(IntRectangle, IntRectangle)
        if self.vertical
        {
            R1 = IntRectangle(x: R.x, y: R.y, h: R.h, k: Int(Double(N.k) * self.partition) - R.y)
            R2 = IntRectangle(x: R.x, y: R.y + R1.k, h: R.h, k: R.k - R1.k)
        }
        else
        {
            R1 = IntRectangle(x: R.x, y: R.y, h: Int(Double(N.h) * self.partition) - R.x, k: R.k)
            R2 = IntRectangle(x: R.x + R1.h, y: R.y, h: R.h - R1.h, k: R.k)
        }
        return (R1, R2)
    }

    private
    func assemble(rect:IntRectangle, against N:IntCoordinateOffset, shader:Shader)
    {
        self.rectangle = rect
        if let leaves = self.leaves
        {
            let (R1, R2):(IntRectangle, IntRectangle) = calculate_rectangles(from: rect, against: N, leaves: leaves)
            leaves.0.assemble(rect: R1, against: N, shader: shader)
            leaves.1.assemble(rect: R2, against: N, shader: shader)
        }
        else
        {
            self.surface = Layer(rect: rect, against: N, shader: shader)
            guard self.surface != nil
            else
            {
                fatalError("Failed to make Cairo layer")
            }
        }
    }

    fileprivate
    func assemble(size:IntCoordinateOffset, shader:Shader)
    {
        self.assemble(rect: IntRectangle(x: 0, y: 0, h: size.h, k: size.k), against: size, shader: shader)
    }

    private
    func reassemble(rect: IntRectangle, against N:IntCoordinateOffset)
    {
        self.rectangle = rect
        assert((self.leaves == nil) != (self.surface == nil))
        if let leaves = self.leaves
        {
            let (R1, R2):(IntRectangle, IntRectangle) = calculate_rectangles(from: rect, against: N, leaves: leaves)
            leaves.0.reassemble(rect: R1, against: N)
            leaves.1.reassemble(rect: R2, against: N)
        }
        else if let surface = self.surface
        {
            surface.size32 = Size(h: Int32(rect.h), k: Int32(rect.k))
            surface.fit_mesh_to(rect: rect, against: N)
        }
    }

    fileprivate
    func reassemble(size:IntCoordinateOffset)
    {
        self.reassemble(rect: IntRectangle(x: 0, y: 0, h: size.h, k: size.k), against: size)
    }

    fileprivate
    func pan(_ p:IntCoordinate, against N:IntCoordinateOffset, bumper_radius:Int)
    // this function can ONLY be called on a View that has child Views
    {
        assert(self.leaves != nil)
        var advance:Int
        let factor:Double
        let (u, v):(Int, Int)
        if self.vertical
        {
            advance = p.y
            factor = Double(N.k)
            u = self.rectangle.y
            v = u + self.rectangle.k
        }
        else
        {
            advance = p.x
            factor = Double(N.h)
            u = self.rectangle.x
            v = u + self.rectangle.h
        }
        let lower_limit = max(Int(self.get_partition_before() * factor), u) + bumper_radius
        let upper_limit = min(Int(self.get_partition_after() * factor), v) - bumper_radius

        if advance < lower_limit
        {
            advance = lower_limit
        }
        else if advance > upper_limit
        {
            advance = upper_limit
        }
        let partition:Double = Double(advance)/factor
        if partition != self.partition
        {
            self.partition = partition
            self.reassemble(rect: self.rectangle, against: N)
        }
    }

    static private
    func _partition_before_set_limit(limit:inout Double, new_limit:Double, next_paths:inout[View], leaves:Leaves)
    {
        next_paths.append(leaves.1)
        limit = max(new_limit, limit)
    }

    static private
    func _partition_after_set_limit(limit:inout Double, new_limit:Double, next_paths:inout[View], leaves:Leaves)
    {
        next_paths.append(leaves.0)
        limit = min(new_limit, limit)
    }

    private
    func _get_partition(starting_paths:[View], limit:inout Double,
                        advance_func: (inout Double, Double, inout[View], Leaves) -> ()
                        )
    // this function can ONLY be called on a View that has child Views
    {
        assert(self.leaves != nil)
        var paths = starting_paths
        var next_paths:[View] = [View]()
        while !paths.isEmpty
        {
            for view in paths
            {
                if let leaves = view.leaves
                {
                    if view.vertical == self.vertical
                    {
                        advance_func(&limit, view.partition, &next_paths, leaves)
                    }
                    else
                    {
                        next_paths.append(leaves.0)
                        next_paths.append(leaves.1)
                    }
                }
            }
            paths = next_paths
            next_paths.removeAll()
        }
    }

    private
    func get_partition_before() -> Double
    {
        var limit:Double = 0
        _get_partition(starting_paths: [self.leaves!.0], limit: &limit, advance_func: View._partition_before_set_limit)
        return limit
    }

    private
    func get_partition_after() -> Double
    {
        var limit:Double = 1
        _get_partition(starting_paths: [self.leaves!.1], limit: &limit, advance_func: View._partition_after_set_limit)
        return limit
    }
}

private
func normalize_to_float(a:Int, u:Int) -> Float
{
    return Float(a)*2/Float(u) - 1
}

private
func rectangle_anchors(rect:IntRectangle, against:IntCoordinateOffset) -> (FloatCoordinate, FloatCoordinate)
{
    let r1:FloatCoordinate = (normalize_to_float(a: rect.x, u: against.h),
                              normalize_to_float(a: rect.y, u: against.k))
    let r2:FloatCoordinate = (normalize_to_float(a: rect.x + rect.h, u: against.h),
                              normalize_to_float(a: rect.y + rect.k, u: against.k))
    return (r1, r2)
}

class Layer {
    static private
    let pixel_layout    = GL_UNSIGNED_INT_8_8_8_8_REV
    static private
    let pixel_result    = GL_BGRA

    var size32:Size {
        didSet
        {
            pixels = Layer.pixel_buffer(size32)
            (surface, cr) = make_cairo_canvases(&pixels, size32)
        }
    }

    private
    let mesh:Textured_mesh
    private
    var pixels :[PixelChannel8]
    var surface:Cairo_surface
    var cr     :Cairo_context

    init?(rect:IntRectangle, against:IntCoordinateOffset, shader:Shader)
    {
        size32   = Size(h: Int32(rect.h), k: Int32(rect.k))
        pixels        = Layer.pixel_buffer(size32)
        let textures:Textures = Textures([(pixels, size32.h, size32.k)].flatMap{ $0 }.map
                                            { ($0, Layer.pixel_layout, Layer.pixel_result) })

        let (r1, r2) = rectangle_anchors(rect: rect, against: against)
        guard let mesh = Textured_mesh(shader: shader,
                            coordinates: Layer.make_coordinates(r1, r2),
                            indices: [0, 1, 3, 1, 2, 3],
                            layout: [3, 2],
                            textures: textures,
                            texture_uniforms: ["texture1"])
        else
        {
            print("Failed to create cairo layer")
            return nil
        }
        self.mesh = mesh
        (surface, cr) = make_cairo_canvases(&pixels, size32)
    }

    static private
    func make_coordinates(_ r1:FloatCoordinate, _ r2:FloatCoordinate) -> [Float]
    {
        return [r1.x, -r1.y, 0,     0, 0,
                r1.x, -r2.y, 0,     0, 1,
                r2.x, -r2.y, 0,     1, 1,
                r2.x, -r1.y, 0,     1, 0 ]
    }

    static private
    func pixel_buffer(_ size32:Size) -> [PixelChannel8]
    {
        return [PixelChannel8](repeating: 0, count: Int(size32.h)*Int(size32.k)*4) // bytes_per_pixel = 4
    }

    func fit_mesh_to(rect:IntRectangle, against:IntCoordinateOffset)
    {
        let (r1, r2) = rectangle_anchors(rect: rect, against: against)
        mesh.update_coordinates(Layer.make_coordinates(r1, r2))
    }

    func transfer()
    {
        mesh.textures.update(t: 0, texture_data: (pixels, size32.h, size32.k))
    }

    func apply()
    {
        mesh.show()
    }
}

let _display_text:String = open_text_file("Package.swift") ?? "Hello world!"

func demo_draw(cr:Cairo_context)
{
    cr.move_to(350, 250)
    cr.arc(x: 350, y: 250, r: 200)
    cr.set_source_rgba(1, 1, 1, 0.2)
    cr.fill()
    cr.select_font_face(fontname: "Fira Sans",
                        slant: CAIRO_FONT_SLANT_NORMAL,
                        weight: CAIRO_FONT_WEIGHT_BOLD)
    cr.set_font_size(48)
    cr.set_source_rgb(1, 0.1, 0.3)
    cr.move_to(10, 70)
    cr.show_text(open_text_file("Package.swift") ?? "Hello world!")
}

func draw_framerate(cr:Cairo_context, n:String, x:Double = 10, y:Double = 160)
{
    cr.select_font_face(fontname: "Fira Sans",
                        slant: CAIRO_FONT_SLANT_NORMAL,
                        weight: CAIRO_FONT_WEIGHT_NORMAL)
    cr.set_font_size(24)
    cr.move_to(x, y)
    cr.show_text(n)
}

func resize_cb(window:Window, h:Int32, k:Int32)
{
    glViewport(0, 0, h, k)
    Interface.reconstitute(from: window).resize_proportionally(to: (h, k))
}

func key_cb(window:Window, key:Int32, scancode:Int32, action:Int32, mode:Int32)
{
    if action == GLFW_PRESS
    {
        switch key
        {
            case GLFW_KEY_ESCAPE:
                glfwSetWindowShouldClose(window, 1)
                print("hi")
            case GLFW_KEY_LEFT:
                break
            default:
                break
        }
    }
}

func char_cb(window:Window, codepoint:UInt32)
{
    Interface.reconstitute(from: window)
    ._letter = Character(UnicodeScalar(codepoint) ?? "\u{0}")
}

func main()
{
    guard glfwInit() == 1
    else
    {
            fatalError("glfwInit() failed")
    }
    defer { glfwTerminate() }
    glfwSetErrorCallback(error_callback);

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_ANY_PROFILE)
    glfwWindowHint(GLFW_RESIZABLE, 1)
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, 1)

    let initial_size:IntCoordinateOffset = (1200, 600)

    guard let window = glfwCreateWindow(Int32(initial_size.h),
                                        Int32(initial_size.k),
                                        "Swiftgron", nil, nil)
    else
    {
        fatalError("glfwCreateWindow failed")
    }
    defer { glfwDestroyWindow(window) }

    glfwMakeContextCurrent(window)
    glfwSwapInterval(1)

    // put together a test view
    let view:View = View(containing: (View(containing: (View(), View(partition: 0.36) ), partition: 0.3), View(partition: 0.5, is_vertical: true)), partition: 0.66666)
    let interface:Interface = Interface(view: view, size: initial_size, window: window)
    let (_left, _left_center, _center, _right_top, _right_bottom) = (view[0, 0], view[0, 1, 0], view[0, 1, 1], view[1, 0], view[1, 1])
    let _left_surf = _left.surface!

    glfwSetFramebufferSizeCallback(window, resize_cb)
    glfwSetKeyCallback(window, key_cb)
    glfwSetCharCallback(window, char_cb)
    glfwSetCursorPosCallback(window, hover_link)
    glfwSetMouseButtonCallback(window, press_link)

    let X = MovingAverage<Double>(samples: 24)

    glfwSetTime(0)
    var prev_lap:Double = 0
    var lap:Double = 0
    var Δt:Double

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    //glEnable(cap: GL_BLEND )
    while glfwWindowShouldClose(window) == 0
    {
        glfwWaitEvents()
        glClearColor(0.3, 0.5, 1, 1)
        glClear(mask: GL_COLOR_BUFFER_BIT)

        _left_surf.cr.set_source_rgb(0, 0, 0)
        _left_surf.cr.paint()
        demo_draw(cr: _left_surf.cr)

        lap = glfwGetTime()
        Δt = lap - prev_lap
        prev_lap = lap
        X.push(1/Δt)
        draw_framerate(cr: _left_surf.cr, n: "\(Int(round(X.average))) FPS")
        draw_framerate(cr: _left_surf.cr, n: String(interface._letter), x: 10, y: 190)

        _right_top._color_me(1, 0, 1)
        _right_bottom._color_me(1, 1, 1)
        _left_center._color_me(0, 1, 1)
        _center._color_me(0.4, 0.3, 1)
        _left_surf.transfer()
        _left_surf.apply()

        glfwSwapBuffers(window)
    }
}

main()
