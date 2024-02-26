
#version 410 core

layout(location = 0) in vec2 vec;

void main()
{
  // Make 4D vertex from 2D value.
  gl_Position = vec4(vec, 0.0, 1.0);
}
