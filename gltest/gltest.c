#include <err.h>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

#include <glad/glad.h>
#include <GLFW/glfw3.h>

void
handle_glfw_error (int err, const char *descr)
{
    errx(1, "glfw error %d: %s", err, descr);
}

GLint
read_file (const char *path, char *buf, size_t len)
{
    int     f;
    int     rv;

    f = open(path, O_RDONLY);
    if (f < 0)
        err(1, "can't open %s", path);

    rv = read(f, buf, len);
    if (rv < 0)
        err(1, "can't read %s:", path);

    if (rv == len)
        errx(1, "not enough room for %s", path);

    close(f);

    return rv;
}

int
main (int argc, char **argv)
{
    GLFWwindow *window;
    char        buf[8192];
    GLint       len;
    GLchar      *bufptr[1];
    GLint       *lenptr[1];
    GLuint      shader;
    GLint       status;

    if (!glfwInit())
        errx(1, "failed to init glfw");
    glfwSetErrorCallback(handle_glfw_error);

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    window  = glfwCreateWindow(800, 600, "Hello world", NULL, NULL);

    if (!window)
        errx(1, "failed to create window");

    glfwMakeContextCurrent(window);
    gladLoadGL();

    len         = read_file("../glsl/f-box.glsl", buf, sizeof(buf));
    shader      = glCreateShader(GL_FRAGMENT_SHADER);
    bufptr[0]   = buf;
    lenptr[0]   = &len;
    glShaderSource(shader, 1, bufptr, &len);
    glCompileShader(shader);
    glGetShaderiv(shader, GL_COMPILE_STATUS, &status);
    if (!status) {
        glGetShaderInfoLog(shader, sizeof(buf), NULL, buf);
        errx(1, "failed to compile shader: %s", buf);
    }
    printf("compiled shader successfully\n");

    glfwDestroyWindow(window);
    glfwTerminate();
}
