
"""

Process images with glsl shaders in a loop (offscreen).
(includes code from several vispy examples :) )

"""


from vispy import gloo
from vispy import app
from vispy.util.ptime import time
from vispy.gloo.util import _screenshot
import vispy.io as io

import PIL.Image
import numpy as np


#app.use_app('glfw')
app.use_app('egl')

#the shader:
vertex = """
attribute vec2 a_position;
attribute vec2 a_texcoord;
varying vec2 v_texcoord;

void main (void)
{
    v_texcoord = a_texcoord;
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""

fragment = """
uniform sampler2D u_tex1;
varying vec2 v_texcoord;

void main()
{

    vec2 texcoord = vec2(v_texcoord.x, 1.0-v_texcoord.y);

    float dx = (0.5-texcoord.x)*.01;

    vec2 offset = vec2(dx, 0.);
    vec4 col  = texture2D(u_tex1, texcoord + offset);

    gl_FragColor = col;
    
}
"""


data = np.zeros(4, dtype=[('a_position', np.float32, 2),
                          ('a_texcoord', np.float32, 2)])

data['a_position'] = np.array([[-1, -1], [+1, -1], [-1, +1], [+1, +1]])

data['a_texcoord'] = [(0, 0), (1, 0), (0, 1), (1, 1)]


class Canvas(app.Canvas):
    def __init__(self, size=(960, 540)):
       
        app.Canvas.__init__(self, show=False, size=size)
        self._t0 = time()
        
        self._rendertex = gloo.Texture2D(shape=self.size[::-1] + (4,))
        self._fbo = gloo.FrameBuffer(self._rendertex, gloo.RenderBuffer(self.size[::-1]))
        self.program = gloo.Program(vertex, fragment)
            
    
    def process_frame(self, tex):
        print('process_frame w/shader')
        with self._fbo:
            
            self.program['u_tex1'] = gloo.Texture2D(tex, interpolation='linear')
            self.program.bind(gloo.VertexBuffer(data))
            
            self.program.draw('triangle_strip')
        
            self.sc = _screenshot((0, 0, self.size[0], self.size[1]),alpha = False)

        self._time = time() - self._t0
        


if __name__ == '__main__':
    
    pil_img = PIL.Image.open('landscape.jpg') #img from: https://www.flickr.com/photos/75487768@N04
    img = np.float32(pil_img)/255.
    
    c = Canvas()
  
    n_frames = 60

    for i in range(n_frames):

        c.process_frame(img)
        
        img = c.sc

        io.write_png('./out/frame_%03d.png' % (i+1), img)

    print('done!')


   
    
    
