# model.py - model loading.

import  numpy           as np
import  pywavefront

from    OpenGL.GL       import *
from    .               import gl

_mesh_layout = {
    "T2F_N3F_V3F":  ((3, 8, 5), (3, 8, 2), (2, 8, 0)),
}

class Mesh:
    def __init__ (self, mesh):
        mat     = mesh.materials[0]

        self.vertices   = np.array(mat.vertices,    dtype=GLfloat)
        #self.indices    = np.array(mesh.faces,      dtype=GLuint)
        self.layout     = _mesh_layout[mat.vertex_format]
        per_vertex      = self.layout[0][1]
        self.count      = len(mat.vertices) // per_vertex
        self.diffuse    = mat.texture.path
        self.specular   = mat.texture_specular_color.path

    def make_vao (self, prg):
        vao     = gl.VAO()
        vbo     = gl.Buffer("vbo", self.vertices)
        # No EBO for now, as pywf duplicates all the vertices
        #ebo     = gl.Buffer("ebo", self.indices)
        layout  = self.layout

        vbo.bind()
        vao.bind()
        vao.add_attrib(prg.b_pos,       *layout[0])
        vao.add_attrib(prg.b_normal,    *layout[1])
        vao.add_attrib(prg.b_tex,       *layout[2])
        #vao.add_ebo(ebo)
        vao.add_primitive(GL_TRIANGLES, 0, self.count)
        vao.unbind()

        self.vao    = vao

class Model:
    def __init__ (self, path):
        obj         = pywavefront.Wavefront(path)

        self.meshes = [Mesh(m) for m in obj.mesh_list]

    def make_vaos (self, prg):
        self.vaos   = [m.make_vao(prg) for m in self.meshes]
