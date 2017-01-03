import Taylor
import SGLOpenGL

public 
class Shader 
{
    private 
    typealias Status_func = (GLuint, GLenum, UnsafeMutablePointer<GLint>) -> ()
    private 
    typealias Log_func = (GLuint, GLint, UnsafeMutablePointer<GLsizei>, UnsafeMutablePointer<GLchar>) -> ()
    
    public private(set)
    var program:GLuint = 0
    
    public 
    init(_ shaders:[(source:String, type:GLenum)]) 
    {
        program = glCreateProgram()
        Shader._link_program(program: program, 
            shaders: shaders.flatMap
                {   (source, type) -> GLuint? in 
                    Shader._compile_shader(source, type)
                }
            )
    }
    
    public convenience
    init(shaders_by_path:[(path:String, type:GLenum)]) 
    {
        self.init(shaders_by_path.flatMap(
        {(path, type) in 
            if let source:String = open_text_file(path) 
            {
                return (source: source, type: type) 
            }
            else 
            {
                return nil
            }
        })
        )
    }
    
    private static
    func _compile_shader(_ source:String, _ shader_type:GLenum) -> GLuint? 
    {
        let shader:GLuint = glCreateShader(type: shader_type)
        
        // this is inefficient cause we got the String from a CString originally
        source.withCString
        { 
            var shader_sources = [$0] // we only have one shader
            glShaderSource(shader: shader, 
                           count : GLsizei(shader_sources.count), 
                           string: &shader_sources,
                           length: [-1])
        }
        glCompileShader(shader: shader)
        
        if let error_msg:String = _compile_success(object: shader, stage: GL_COMPILE_STATUS, 
                         status: { glGetShaderiv(shader: $0, 
                                                 pname : $1, 
                                                 params: $2) 
                                 },
                         log   : { glGetShaderInfoLog(shader : $0, 
                                                      bufSize: $1, 
                                                      length : $2, 
                                                      infoLog: $3) 
                                 }) 
        {
            print(error_msg)
            return nil
        }
        else 
        {
            return shader
        }
        
    }
    
    private static 
    func _link_program(program:GLuint, shaders:[GLuint]) 
    {
        for shader in shaders 
        {
            glAttachShader(program, shader)
            defer { glDeleteShader(shader: shader) }
        }
        glLinkProgram(program: program)
        
        if let error_msg:String = _compile_success(object: program, stage: GL_LINK_STATUS, 
                         status: { glGetProgramiv($0, $1, $2) },
                         log   : { glGetProgramInfoLog($0, $1, $2, $3) }) 
        {
            print(error_msg)
        }
    }
    
    private static 
    func _compile_success(object:GLuint, stage: GLenum, 
            status:Status_func ,
            log   :Log_func
            ) -> String? 
    {
        var success:GLint = 0
        status(object, stage, &success)
        if success == 1 
        {
            return nil
        }
        else 
        {
            var message_length:GLsizei = 0
            status(object, GL_INFO_LOG_LENGTH, &message_length)
            guard message_length > 0 
            else 
            {
                return ""
            }
            var error_message = [GLchar](repeating: 0, 
                                         count: Int(message_length))
            log(object, message_length, &message_length, &error_message)
            return String(cString: error_message)
        }
    }
}
