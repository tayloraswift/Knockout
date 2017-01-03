#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec2 uv_map;

out vec2 uv_coord;

void main()
{
    gl_Position = vec4(position.xyz, 1.0);
    uv_coord = uv_map;
}
