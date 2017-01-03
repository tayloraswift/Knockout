#version 330 core

in vec2 uv_coord;

out vec4 color;

uniform sampler2D texture1;

void main()
{
    color = texture(texture1, uv_coord) * vec4(1, 1, 1, 0.5);
}
