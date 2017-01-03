import CJPEG

public 
typealias PixelChannel8 = UInt8

public
typealias BitmapData = (pixels:[PixelChannel8], h:Int32, k:Int32)

fileprivate 
func jpeg_create_decompress(_ info:inout jpeg_decompress_struct) -> () // to replace libjpeg’s complex macro
{
    jpeg_CreateDecompress(&info, JPEG_LIB_VERSION, MemoryLayout<jpeg_decompress_struct>.size)
}

public
func read_jpeg(_ path:Cpath) -> BitmapData? {
    let path = unix_path(path)
    
    guard let f:UnsafeMutablePointer<FILE> = fopen(path, "rb") 
    else {
        print("Error, could not open file '\(path)'")
        return nil
    }
    defer { fclose(f) }
    
    var error:jpeg_error_mgr = jpeg_error_mgr()
    var info:jpeg_decompress_struct = jpeg_decompress_struct()
    
    info.err = jpeg_std_error(&error) // error logging
    
    jpeg_create_decompress(&info)
    defer { jpeg_destroy_decompress(&info) }
    
    jpeg_stdio_src(&info, f)
    jpeg_read_header(&info, 1)
    jpeg_start_decompress(&info)
    
    let h:UInt32 = info.output_width
    let k:UInt32 = info.output_height
    let m:UInt32 = UInt32(info.num_components)
    
    guard m == 3
    else
    {
        print("JPEG file \(path) has \(m) color channels. It should have 3: R, G, and B. Go home JPEG, you’re drunk.")
        return nil
    }
    
    let memory_stride:UInt32 = h*m
    let pixels:[PixelChannel8] = [PixelChannel8](repeating: 0, count: Int(h*k*m))
    let P:UnsafeMutablePointer<PixelChannel8> = UnsafeMutablePointer<PixelChannel8>(mutating: pixels)
    var strip:[UnsafeMutablePointer<PixelChannel8>?] = [P]
    
    while info.output_scanline < k
    {
        strip[0] = P.advanced(by: Int(info.output_scanline*memory_stride))
        jpeg_read_scanlines(&info, &strip, 1)
    }
    
    jpeg_finish_decompress(&info)
    
    return (pixels: pixels, h: Int32(h), k: Int32(k))
}
