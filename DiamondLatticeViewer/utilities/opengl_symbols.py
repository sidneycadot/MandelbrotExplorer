"""Import OpenGL names in a controlled way.

PyOpenGL provides a lot of constants and functions. The usual way to deal with this is to do:

    from OpenGL.GL import *

However, this brings in other symbols as well, leading to local namespace pollution.

For that reason, we provide this file that imports precisely the things we want from OpenGL.GL.
Client code can now do:

    from utilities.opengl_symbols import *

Working like this, no spurious symbols are imported into the local namespace.

The disadvantage is that this file needs to explicitly import all symbols that we need, and thus requires some
maintenance effort.
"""

# noinspection PyUnresolvedReferences

from OpenGL.GL import (

    # OpenGL constants.

    GL_COMPILE_STATUS,
    GL_FALSE, GL_TRUE,
    GL_INT, GL_FLOAT,
    GL_ARRAY_BUFFER,
    GL_STATIC_DRAW,
    GL_CULL_FACE,
    GL_TRIANGLES,
    GL_TEXTURE_2D,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_LINEAR,
    GL_REPEAT,
    GL_RGB,
    GL_UNSIGNED_BYTE,
    GL_TRIANGLE_STRIP,
    GL_DEPTH_TEST,
    GL_BACK,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_VERTEX_SHADER,
    GL_GEOMETRY_SHADER,
    GL_FRAGMENT_SHADER,
    GL_LINK_STATUS,

    # OpenGL functions.

    glCreateProgram,
    glCreateShader,
    glAttachShader,
    glShaderSource,
    glLinkProgram,
    glCompileShader,
    glGetUniformLocation,
    glGetShaderiv,
    glGetProgramiv,
    glGenBuffers,
    glGenVertexArrays, glVertexAttribPointer,
    glVertexAttribIPointer,
    glBindBuffer,
    glBufferData,
    glEnableVertexAttribArray,
    glBindVertexArray,
    glEnable, glDisable,
    glUseProgram,
    glUniform1f, glUniform1ui, glUniformMatrix4fv,
    glDrawArraysInstanced,
    glDeleteVertexArrays,
    glDeleteBuffers,
    glDeleteProgram,
    glDeleteShader,
    glGenTextures,
    glTexParameteri,
    glBindTexture,
    glTexImage2D,
    glGenerateMipmap,
    glDrawArrays,
    glPointSize,
    glClearColor,
    glCullFace,
    glClear,
    glViewport,
    glGetShaderInfoLog,
    glGetProgramInfoLog
)
