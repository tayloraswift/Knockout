import SGLOpenGL

func read_gl_errors(hide:Bool = false) 
{
    while true 
    {
        let e = SGLOpenGL.glGetError()
        if e == SGLOpenGL.GL_NO_ERROR 
        {
            break
        }
        else if !hide 
        {
            print(String(e, radix: 16))
        }
    }
}
