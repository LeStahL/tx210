/* The Team210 mic to visuals tool for DJs
 * Copyright (C) 2018  Alexander Kraus <nr4@z10.info>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

// WIN32 code
#ifdef _MSC_VER

int _fltused = 0;

#define ABS(x) ((x)<0?(-x):(x))
#define sign(x) ((x)<0?-1.:1.)

#define WIN32_LEAN_AND_MEAN
#define VC_EXTRALEAN
#include <windows.h>
#include <mmsystem.h>

#include <GL/gl.h>
#include "glext.h"

// Standard library and CRT rewrite for saving executable size
void *memset(void *ptr, int value, size_t num)
{
    for(int i=num-1; i>=0; i--)
        ((unsigned char *)ptr)[i] = value;
    return ptr;
}

size_t strlen(const char *str)
{
    int len = 0;
    while(str[len] != '\0') ++len;
    return len;
}

void *malloc( unsigned int size )
{
    return GlobalAlloc(GMEM_ZEROINIT, size) ;
}
#else 

#include <X11/X.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>

#include <GL/gl.h>
#include <GL/glx.h>
#include "glext.h"

#include <time.h>
#include <sys/time.h>

#include <dlfcn.h>

// #include <stdlib.h>
#include <string.h>
#endif

// TODO: remove
#include <stdio.h>

// fonts
#include "Pacifico-Regular.h"

// OpenGL extensions
PFNGLGETPROGRAMIVPROC glGetProgramiv;
PFNGLGETSHADERIVPROC glGetShaderiv;
PFNGLGETSHADERINFOLOGPROC glGetShaderInfoLog;
PFNGLCREATESHADERPROC glCreateShader;
PFNGLCREATEPROGRAMPROC glCreateProgram;
PFNGLSHADERSOURCEPROC glShaderSource;
PFNGLCOMPILESHADERPROC glCompileShader;
PFNGLATTACHSHADERPROC glAttachShader;
PFNGLLINKPROGRAMPROC glLinkProgram;
PFNGLUSEPROGRAMPROC glUseProgram;
PFNGLGETUNIFORMLOCATIONPROC glGetUniformLocation;
PFNGLUNIFORM2FPROC glUniform2f;
PFNGLUNIFORM1FPROC glUniform1f;
PFNGLGENFRAMEBUFFERSPROC glGenFramebuffers;
PFNGLBINDFRAMEBUFFERPROC glBindFramebuffer;
PFNGLFRAMEBUFFERTEXTURE2DPROC glFramebufferTexture2D;
PFNGLNAMEDRENDERBUFFERSTORAGEEXTPROC glNamedRenderbufferStorageEXT;
PFNGLUNIFORM1IPROC glUniform1i;

#ifdef _MSC_VER
PFNGLACTIVETEXTUREPROC glActiveTexture;
#endif

// TODO: remove below
void debug(int shader_handle)
{
    printf("debugging shader.\n");
    int compile_status = 0;
    glGetShaderiv(shader_handle, GL_COMPILE_STATUS, &compile_status);
    if(compile_status != GL_TRUE)
    {
        printf("FAILED.\n");
        int len = 12;
        glGetShaderiv(shader_handle, GL_INFO_LOG_LENGTH, &len);
        printf("log length: %d\n", len);
        GLchar CompileLog[1024];
        glGetShaderInfoLog(shader_handle, len, NULL, CompileLog);
        printf("error: %s\n", CompileLog);
    }
    else 
        printf("shader compilation successful.\n");
}
// TODO: remove above

//Shader globals
int w = 1366, h = 768,
    gfx_handle, gfx_program, 
    time_location, resolution_location, 
    font_texture_location, font_width_location;
    
// Demo globals
double t_start = 0., t_now = 0.;
unsigned int font_texture_handle;
int font_texture_location, font_texture_width_location;

// Pure opengl drawing code, cross-platform
void draw()
{
    glUniform1i(font_texture_location, 0);
    glUniform1f(font_width_location, font_texture_size);
    
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, font_texture_handle);
    
    glUniform1f(time_location, t_now-t_start);
    glUniform2f(resolution_location, w, h);
    
    glBegin(GL_QUADS);
    
    glVertex3f(-1,-1,0);
    glVertex3f(-1,1,0);
    glVertex3f(1,1,0);
    glVertex3f(1,-1,0);
    
    glEnd();
    
    glFlush();
}

#ifdef _MSC_VER
LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
    switch(uMsg)
    {
        case WM_KEYDOWN:
            switch(wParam)
            {
                case VK_ESCAPE:
                    ExitProcess(0);
                    break;
            }
            break;
            
        case WM_TIMER:
            HDC hdc = GetDC(hwnd);
                 
            SYSTEMTIME st_now;
            GetSystemTime(&st_now);            
            t_now = (float)st_now.wMinute*60.+(float)st_now.wSecond+(float)st_now.wMilliseconds/1000.;
            
            draw();
            
            SwapBuffers(hdc);
            
            break;
            
        default:
            break;
            
    }
    return DefWindowProc(hwnd, uMsg, wParam, lParam);
}
#endif

#ifdef _MSC_VER
int WINAPI demo(HINSTANCE hInstance, HINSTANCE hPrevInstance, PWSTR pCmdLine, int nCmdShow)
{
    //TODO: remove
    AllocConsole();
    freopen("CONIN$", "r", stdin);
    freopen("CONOUT$", "w", stdout);
    freopen("CONOUT$", "w", stderr);
    
    CHAR WindowClass[]  = "Team210 Demo Window";
    
    WNDCLASSEX wc = { 0 };
    wc.cbSize = sizeof(wc);
    wc.style = CS_OWNDC | CS_VREDRAW | CS_HREDRAW;
    wc.lpfnWndProc = &WindowProc;
    wc.cbClsExtra = 0;
    wc.cbWndExtra = 0;
    wc.hInstance = hInstance;
    wc.hIcon = LoadIcon(NULL, IDI_WINLOGO); 
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = NULL;
    wc.lpszMenuName = NULL;
    wc.lpszClassName = WindowClass;
    wc.hIconSm = NULL;
    
    RegisterClassEx(&wc);
    
    // Get full screen information
    HMONITOR hmon = MonitorFromWindow(0, MONITOR_DEFAULTTONEAREST);
    MONITORINFO mi = { sizeof(mi) };
    GetMonitorInfo(hmon, &mi);
    
    // Create the window.
    HWND hwnd = CreateWindowEx(
        0,                                                          // Optional window styles.
        WindowClass,                                                // Window class
        ":: NR4^QM/Team210 :: GO - MAKE A DEMO ::",                                 // Window text
        WS_POPUP | WS_VISIBLE,                                      // Window style
        mi.rcMonitor.left,
        mi.rcMonitor.top,
        mi.rcMonitor.right - mi.rcMonitor.left,
        mi.rcMonitor.bottom - mi.rcMonitor.top,                     // Size and position
        
        NULL,                                                       // Parent window    
        NULL,                                                       // Menu
        hInstance,                                                  // Instance handle
        0                                                           // Additional application data
    );
    
    // Show it
    ShowWindow(hwnd, TRUE);
    UpdateWindow(hwnd);
    
    // Create OpenGL context
    PIXELFORMATDESCRIPTOR pfd =
    {
        sizeof(PIXELFORMATDESCRIPTOR),
        1,
        PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER,    //Flags
        PFD_TYPE_RGBA,        // The kind of framebuffer. RGBA or palette.
        32,                   // Colordepth of the framebuffer.
        0, 0, 0, 0, 0, 0,
        0,
        0,
        0,
        0, 0, 0, 0,
        24,                   // Number of bits for the depthbuffer
        8,                    // Number of bits for the stencilbuffer
        0,                    // Number of Aux buffers in the framebuffer.
        PFD_MAIN_PLANE,
        0,
        0, 0, 0
    };
    
    HDC hdc = GetDC(hwnd);
    
    int  pf = ChoosePixelFormat(hdc, &pfd); 
    SetPixelFormat(hdc, pf, &pfd);
    
    HGLRC glrc = wglCreateContext(hdc);
    wglMakeCurrent (hdc, glrc);
    
    // OpenGL extensions
    glGetProgramiv = (PFNGLGETPROGRAMIVPROC) wglGetProcAddress("glGetProgramiv");
    glGetShaderiv = (PFNGLGETSHADERIVPROC) wglGetProcAddress("glGetShaderiv");
    glGetShaderInfoLog = (PFNGLGETSHADERINFOLOGPROC) wglGetProcAddress("glGetShaderInfoLog");
    glCreateShader = (PFNGLCREATESHADERPROC) wglGetProcAddress("glCreateShader");
    glCreateProgram = (PFNGLCREATEPROGRAMPROC) wglGetProcAddress("glCreateProgram");
    glShaderSource = (PFNGLSHADERSOURCEPROC) wglGetProcAddress("glShaderSource");
    glCompileShader = (PFNGLCOMPILESHADERPROC) wglGetProcAddress("glCompileShader");
    glAttachShader = (PFNGLATTACHSHADERPROC) wglGetProcAddress("glAttachShader");
    glLinkProgram = (PFNGLLINKPROGRAMPROC) wglGetProcAddress("glLinkProgram");
    glUseProgram = (PFNGLUSEPROGRAMPROC) wglGetProcAddress("glUseProgram");
    glGetUniformLocation = (PFNGLGETUNIFORMLOCATIONPROC) wglGetProcAddress("glGetUniformLocation");
    glUniform2f = (PFNGLUNIFORM2FPROC) wglGetProcAddress("glUniform2f");
    glUniform1f = (PFNGLUNIFORM1FPROC) wglGetProcAddress("glUniform1f");
    glGenFramebuffers = (PFNGLGENFRAMEBUFFERSPROC) wglGetProcAddress("glGenFramebuffers");
    glBindFramebuffer = (PFNGLBINDFRAMEBUFFERPROC) wglGetProcAddress("glBindFramebuffer");
    glFramebufferTexture2D = (PFNGLFRAMEBUFFERTEXTURE2DPROC) wglGetProcAddress("glFramebufferTexture2D");
    glNamedRenderbufferStorageEXT = (PFNGLNAMEDRENDERBUFFERSTORAGEEXTPROC) wglGetProcAddress("glNamedRenderbufferStorage");
    glActiveTexture = (PFNGLACTIVETEXTUREPROC) wglGetProcAddress("glActiveTexture");
    glUniform1i = (PFNGLUNIFORM1IPROC) wglGetProcAddress("glUniform1i");
    
    // Set render timer to 60 fps
    UINT_PTR t = SetTimer(hwnd, 1, 1000./60., NULL);
    
    // Get start time for relative time sync
    SYSTEMTIME st_start;
    GetSystemTime(&st_start);
    t_start = (float)st_start.wMinute*60.+(float)st_start.wSecond+(float)st_start.wMilliseconds/1000.;
#else
int main(int argc, char **args)
{
    XInitThreads();
    
    Display                 *display;
    Window                  root;
    GLint                   att[] = { GLX_RGBA, GLX_DEPTH_SIZE, 24, GLX_DOUBLEBUFFER, None };
    XVisualInfo             *vi;
    Colormap                cmap;
    XSetWindowAttributes    swa;
    Window                  win;
    GLXContext              glc;
    XWindowAttributes       gwa;
    XEvent                  xevent;

    display = XOpenDisplay(NULL);
    root = DefaultRootWindow(display);
    vi = glXChooseVisual(display, 0, att);
    cmap = XCreateColormap(display, root, vi->visual, AllocNone);
    swa.colormap = cmap;
    
    swa.event_mask = ExposureMask | KeyPressMask;
    win = XCreateWindow(display, root, 0, 0, w, h, 0, vi->depth, InputOutput, vi->visual, CWColormap | CWEventMask, &swa);
 
    Atom atoms[2] = { XInternAtom(display, "_NET_WM_STATE_FULLSCREEN", True), None };
    XChangeProperty(
        display, 
        win, 
        XInternAtom(display, "_NET_WM_STATE", True),
                    XA_ATOM, 32, PropModeReplace,(unsigned char*) atoms, 1
    );
    XMapWindow(display, win);
    glc = glXCreateContext(display, vi, NULL, GL_TRUE);
    glXMakeCurrent(display, win, glc);

    // OpenGL extensions
    void *gl = (void*)dlopen("libGL.so", RTLD_LAZY | RTLD_GLOBAL);
    glGetProgramiv = (PFNGLGETPROGRAMIVPROC) dlsym(gl, "glGetProgramiv");
    glGetShaderiv = (PFNGLGETSHADERIVPROC) dlsym(gl, "glGetShaderiv");
    glGetShaderInfoLog = (PFNGLGETSHADERINFOLOGPROC) dlsym(gl, "glGetShaderInfoLog");
    glCreateShader = (PFNGLCREATESHADERPROC) dlsym(gl, "glCreateShader");
    glCreateProgram = (PFNGLCREATEPROGRAMPROC) dlsym(gl, "glCreateProgram");
    glShaderSource = (PFNGLSHADERSOURCEPROC) dlsym(gl, "glShaderSource");
    glCompileShader = (PFNGLCOMPILESHADERPROC) dlsym(gl, "glCompileShader");
    glAttachShader = (PFNGLATTACHSHADERPROC) dlsym(gl, "glAttachShader");
    glLinkProgram = (PFNGLLINKPROGRAMPROC) dlsym(gl, "glLinkProgram");
    glUseProgram = (PFNGLUSEPROGRAMPROC) dlsym(gl, "glUseProgram");
    glGetUniformLocation = (PFNGLGETUNIFORMLOCATIONPROC) dlsym(gl, "glGetUniformLocation");
    glUniform2f = (PFNGLUNIFORM2FPROC) dlsym(gl, "glUniform2f");
    glUniform1f = (PFNGLUNIFORM1FPROC) dlsym(gl, "glUniform1f");
    glGenFramebuffers = (PFNGLGENFRAMEBUFFERSPROC) dlsym(gl, "glGenFramebuffers");
    glBindFramebuffer = (PFNGLBINDFRAMEBUFFERPROC) dlsym(gl, "glBindFramebuffer");
    glFramebufferTexture2D = (PFNGLFRAMEBUFFERTEXTURE2DPROC) dlsym(gl, "glFramebufferTexture2D");
    glNamedRenderbufferStorageEXT = (PFNGLNAMEDRENDERBUFFERSTORAGEEXTPROC) dlsym(gl, "glNamedRenderbufferStorage");
    glUniform1i = (PFNGLUNIFORM1IPROC) dlsym(gl, "glUniform1i");
    
    struct timeval tv;
    gettimeofday(&tv, NULL);
    t_start = (double)tv.tv_sec+(double)tv.tv_usec/1.e6;
    
#endif
    
    // Load shader
#undef VAR_IRESOLUTION
#undef VAR_ITIME
#undef VAR_IFONT
#undef VAR_IFONTWIDTH
#include "gfx.h"
#ifndef VAR_IRESOLUTION
    #define VAR_IRESOLUTION "iResolution"
#endif
#ifndef VAR_ITIME
    #define VAR_ITIME "iTime"
#endif
#ifndef VAR_IFONT
    #define VAR_IFONT "iFont"
#endif
#ifndef VAR_IFONTWIDTH
    #define VAR_IFONTWIDTH "iFontWidth"
#endif
    int gfx_size = strlen(gfx_frag),
        gfx_handle = glCreateShader(GL_FRAGMENT_SHADER);
    gfx_program = glCreateProgram();
    glShaderSource(gfx_handle, 1, (GLchar **)&gfx_frag, &gfx_size);
    glCompileShader(gfx_handle);
    debug(gfx_handle);
    glAttachShader(gfx_program, gfx_handle);
    glLinkProgram(gfx_program);
    glUseProgram(gfx_program);
    time_location =  glGetUniformLocation(gfx_program, VAR_ITIME);
    resolution_location = glGetUniformLocation(gfx_program, VAR_IRESOLUTION);
    font_texture_location = glGetUniformLocation(gfx_program, VAR_IFONT);
    font_width_location = glGetUniformLocation(gfx_program, VAR_IFONTWIDTH);
    
    glUseProgram(gfx_program);
    glViewport(0, 0, w, h);
    
    // Initialize font texture
    printf("font texture width is: %d\n", font_texture_size); // TODO: remove
    glGenTextures(1, &font_texture_handle);
    glBindTexture(GL_TEXTURE_2D, font_texture_handle);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, font_texture_size, font_texture_size, 0, GL_RGBA, GL_UNSIGNED_BYTE, font_texture);

    // Main loop
#ifdef _MSC_VER
    MSG msg;
    while(GetMessage(&msg, NULL, 0, 0) > 0)
    {
        TranslateMessage(&msg);
        DispatchMessage(&msg); 
    }
    
    return msg.wParam;
#else
    int x_file_descriptor = ConnectionNumber(display);
    fd_set x_file_descriptor_set;
    
    // Main loop
    while(1)
    {
        // Exit demo if any key is pressed.
        while(XPending(display))
        {
            XNextEvent(display, &xevent);
            if(xevent.type == KeyPress) 
                exit(0);
        }
        
        FD_ZERO(&x_file_descriptor_set);
        FD_SET(x_file_descriptor, &x_file_descriptor_set);
        
        struct timeval t;
        t.tv_usec = 1.e6/60.;
        t.tv_sec = 0;
        
        int num_ready_fds = select(x_file_descriptor + 1, &x_file_descriptor_set, NULL, NULL, &t);
        if (num_ready_fds == 0)    
        {            
            struct timeval tv_now;
            gettimeofday(&tv_now, NULL);
            t_now = (double)tv_now.tv_sec+(double)tv_now.tv_usec/1.e6;

            draw();
            
            glXSwapBuffers(display, win);
        }
    }
    return 0;
#endif
}
