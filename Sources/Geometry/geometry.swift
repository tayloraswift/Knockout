import SGLOpenGL
import Taylor

public 
typealias Size   = (h:Int32, k:Int32)

public
class Mesh 
{
    var indices:[GLuint]
    var coordinates:[GLfloat]
    
    fileprivate
    let n:GLsizei
    
    fileprivate
    var VBO:GLuint = 0
    fileprivate
    var EBO:GLuint = 0
    fileprivate
    var VAO:GLuint = 0
    
    public
    let program:GLuint
    
    private
    let coordinate_size:Int = MemoryLayout<GLfloat>.size
    private
    let index_size     :Int = MemoryLayout<GLuint>.size
    
    public
    init?(shader                :Shader, 
          coordinates           :[GLfloat], 
          indices input_indices :[GLuint]?  = nil, 
          layout                :[Int]      = [3]) 
    {
        guard layout.count <= 16 
        else
        {
            print("Error: \(layout.count) attributes were given but most graphics card only support up to 16")
            return nil
        }
        let n:Int // number of indices
        let k:Int = coordinates.count // number of coordinates stored
        let m:Int = layout.reduce(0, +) // coordinates per point
        guard (k % m) == 0 && k > 0 
        else
        {
            print("Error: \(k) coordinates were given, but \(k) is not divisible by \(m)-tuples")
            return nil
        }
        let p:Int = k/m
        
        if let input_indices = input_indices 
        {
            n = input_indices.count
            guard input_indices.max() ?? 0 < GLuint(p) 
            else
            {
                print("Error: indices contains value \(input_indices.max() ?? 0) but there are only \(p) points")
                return nil
            }
        }

        else
        {   
            n = p
        }
        
        guard (n % 3) == 0 && n > 0
        else
        {
            print("Error: \(n) is not divisible by 3, so the EBO cannot form triangles")
            return nil
        }
        
        self.n = GLsizei(n)
        indices = input_indices ?? (0..<n).map{GLuint($0)}
        self.coordinates = coordinates
        
        let coordinate_stride:GLsizei = GLsizei(coordinate_size * m)
        
        
        glGenVertexArrays(n: 1, arrays: &VAO)
        glBindVertexArray(array: VAO)
        
        // create VBO
        glGenBuffers(n: 1, buffers: &VBO)
        glBindBuffer(target: GL_ARRAY_BUFFER, buffer: VBO)
        glBufferData(target: GL_ARRAY_BUFFER, 
                     size  : coordinate_size * k,
                     data  : coordinates, 
                     usage : GL_DYNAMIC_DRAW)
        
        var offset:Int = 0
        for (i, l) in layout.enumerated().map({ (GLuint($0), GLint($1)) })
        {
            glVertexAttribPointer(index     : i, 
                                  size      : l, 
                                  type      : GL_FLOAT, 
                                  normalized: false, 
                                  stride    : coordinate_stride, 
                                  pointer   : UnsafeRawPointer(bitPattern: offset * coordinate_size))
            glEnableVertexAttribArray(index : i)
            offset += Int(l)
        }
        
        // Create EBO
        glGenBuffers(n: 1, buffers: &EBO)
        glBindBuffer(target: GL_ELEMENT_ARRAY_BUFFER, buffer: EBO)
        glBufferData(target: GL_ELEMENT_ARRAY_BUFFER, 
                     size  : index_size * n,
                     data  : indices, 
                     usage : GL_STATIC_DRAW)
        
        glBindVertexArray(array: 0)
        glBindBuffer(target: GL_ARRAY_BUFFER, buffer: 0)
        glBindBuffer(target: GL_ELEMENT_ARRAY_BUFFER, buffer: 0)
        
        self.program = shader.program
    }
    
    public
    func update_coordinates(_ new_coordinates:[GLfloat])
    {
        assert(coordinates.count == new_coordinates.count)
        glBindBuffer(target: GL_ARRAY_BUFFER, buffer: VBO)
        glBufferSubData(target: GL_ARRAY_BUFFER, 
                        offset: 0,
                        size  : coordinate_size * new_coordinates.count,
                        data  : new_coordinates)
    }
    
    public
    func uniform(_ set_uniform:() -> Void ) 
    {
        glUseProgram(program: program)
        set_uniform()
    }
    
    public
    func show(mode:GLenum = GL_TRIANGLES)
    {
        glUseProgram(program: program)
        glBindVertexArray(array: VAO)
        glDrawElements(mode, n, GL_UNSIGNED_INT, nil)
        glBindVertexArray(array: 0)
    }
    
    deinit
    {
        glDeleteBuffers(n: 1, buffers: &VBO)
        glDeleteBuffers(n: 1, buffers: &EBO)
        glDeleteVertexArrays(n: 1, arrays: &VAO)
    }
    
}

public 
class Textures
{
    private
    var textures:[GLuint]
    private
    var pixel_layouts:[GLenum] = [GLenum]()
    private
    var pixel_results:[GLenum] = [GLenum]()
    
    private
    var sizes:[Size] = [Size]()
    
    public
    init(_ texture_input:[(texture_data:BitmapData, pixel_layout:GLenum, pixel_result:GLenum)])
    {
        let n:Int = texture_input.count
        textures = [GLuint](repeating: 0, count: n)
        glGenTextures(GLsizei(n), &textures)
        
        for (texture, texture_input) in zip(textures, texture_input)
        {
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexImage2D(
                        target          : GL_TEXTURE_2D, 
                        level           : 0, 
                        internalformat  : GL_RGB, 
                        width           : GLsizei(texture_input.texture_data.h), 
                        height          : GLsizei(texture_input.texture_data.k), 
                        border          : 0, //always 0
                        format          : texture_input.pixel_result, 
                        type            : texture_input.pixel_layout, 
                        pixels          : texture_input.texture_data.pixels)

            glBindTexture(GL_TEXTURE_2D, 0)
            
            pixel_layouts.append(texture_input.pixel_layout)
            pixel_results.append(texture_input.pixel_result)
            sizes.append((texture_input.texture_data.h, texture_input.texture_data.k))
        }
    }
    
    public 
    func update(t:Int, texture_data:BitmapData)
    {
        glBindTexture(GL_TEXTURE_2D, textures[t])
        if sizes[t] == (texture_data.h, texture_data.k)
        {
            glTexSubImage2D(
                            target          : GL_TEXTURE_2D, 
                            level           : 0, 
                            xoffset         : 0, 
                            yoffset         : 0, 
                            width           : GLsizei(texture_data.h), 
                            height          : GLsizei(texture_data.k), 
                            format          : pixel_results[t], 
                            type            : pixel_layouts[t], 
                            pixels          : texture_data.pixels)
        }
        else
        {
            sizes[t] = (texture_data.h, texture_data.k)
            glTexImage2D(
                            target          : GL_TEXTURE_2D, 
                            level           : 0, 
                            internalformat  : GL_RGB, 
                            width           : GLsizei(texture_data.h), 
                            height          : GLsizei(texture_data.k), 
                            border          : 0, //always 0
                            format          : pixel_results[t], 
                            type            : pixel_layouts[t], 
                            pixels          : texture_data.pixels)
        }
        glBindTexture(GL_TEXTURE_2D, 0)
    }
    
    fileprivate
    func use(uniforms:[GLint], _ f:() -> ())
    {
        for (i, (texture, uniform)) in zip(textures, uniforms).enumerated()
        {
            glActiveTexture(texture: GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, texture)
            glUniform1i(uniform, GLint(i))
        }
        f()
        glActiveTexture(texture: GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, 0)
    }
    
    deinit
    {
        glDeleteTextures(GLsizei(textures.count), &textures)
    }
}

public
class Textured_mesh:Mesh 
{
    public
    let textures:Textures
    
    private
    let uniforms:[GLint]
    
    public
    init?(shader                :Shader, 
          coordinates           :[GLfloat], 
          indices input_indices :[GLuint]?  = nil, 
          layout                :[Int]      = [3],
          textures texturesobj  :Textures,
          texture_uniforms      :[String]) 
    {
        textures = texturesobj
        uniforms = texture_uniforms.map{ name in glGetUniformLocation(shader.program, name) }
        
        super.init(shader       : shader,
                   coordinates  : coordinates,
                   indices      : input_indices,
                   layout       : layout)
    }

    public override
    func show(mode:GLenum = GL_TRIANGLES)
    {
        textures.use(uniforms: uniforms,
        {
            super.show(mode: mode)
        })
    }
}
