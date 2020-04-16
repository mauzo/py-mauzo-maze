# model.py - model loading.

import  glm
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

        self.diffuse    = glm.vec3(mat.diffuse)
        self.specular   = mat.specular[0]
        self.shininess  = mat.shininess
        self.emission   = glm.vec3(mat.emissive)

        if mat.texture:
            self.diffuseT   = gl.Texture(file=mat.texture.path)
        else:
            self.diffuseT   = None
        if mat.texture_specular_color:
            self.specularT  = gl.Texture(file=mat.texture_specular_color.path)
        else:
            self.specularT  = None

    def make_vao (self):
        vao     = gl.VAO()
        vbo     = gl.Buffer("vbo", self.vertices)
        # No EBO for now, as pywf duplicates all the vertices
        #ebo     = gl.Buffer("ebo", self.indices)
        layout  = self.layout
        attrs   = gl.shader_attribs()

        vbo.bind()
        vao.bind()
        vao.add_attrib(attrs["b_pos"],      *layout[0])
        vao.add_attrib(attrs["b_normal"],   *layout[1])
        vao.add_attrib(attrs["b_tex"],      *layout[2])
        #vao.add_ebo(ebo)
        vao.add_primitive(GL_TRIANGLES, 0, self.count)
        vao.unbind()

        self.vao    = vao

    def use (self, prg):
        prg.u_material_diffuse(self.diffuse)
        prg.u_material_specular(self.specular)
        prg.u_material_shininess(self.shininess)
        prg.u_emission(self.emission)

        self.vao.use()

    def render (self):
        self.vao.render()

class Model:
    def __init__ (self, path):
        obj         = pywavefront.Wavefront(path)

        self.meshes = [Mesh(m) for m in obj.mesh_list]
        for m in self.meshes:
            m.make_vao()

    def render (self, prg):
        for m in self.meshes:
            m.use(prg)
            m.render()
