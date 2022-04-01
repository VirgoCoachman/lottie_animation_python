#!./venv/bin/python3
import sys
import os

from lottie.utils import script
from lottie import objects
from lottie.utils import animation as anutils
from lottie import Point, Color

import tornado.web
from tornado import httputil
from tornado.escape import json_decode
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler, url

points = [
    (80, 40),
    (95, 100),
    (108, 100),
    (230, 100),
    (290, 245),
    (400, 245),
    (300, 313),
    (423, 412),
    (245, 354),
    (60, 200),
    (380, 80),
]


class ImageHandler(RequestHandler):
    
    def get(self, art):
        background_image = objects.assets.Image().load("./images/mappy.jpg")
        an = objects.Animation(180)
        an.assets.append(background_image)

        layer = objects.ShapeLayer()
        # layer = objects.ImageLayer(background_image.id)
        
        an.add_layer(layer)
        an.add_layer(objects.ImageLayer(background_image.id))

        group = layer.add_shape(objects.Group())
        bez = group.add_shape(objects.Path())
        les_points = list(points)
        while len(les_points) > 0:
            point = les_points.pop()
            bez.shape.value.add_point(Point(point[0], point[1]))

        group.add_shape(objects.Stroke(Color(1, 0, 0), 10))


        group = layer.add_shape(objects.Group())
        sh = anutils.generate_path_segment(bez.shape.value, 0, 180, 60, 180, 60, True)
        group.add_shape(sh)
        group.add_shape(objects.Stroke(Color(0, 1, 0), 20))

        # print(an.to_dict())
        script.script_main(an, path=".", basename=art, formats=["json"])
       
        
        
class LottiePlayerHandler(RequestHandler):
    def get(self):
        self.render("index.html")
    
        
class App(Application):
    def __init__(self):
        handlers = [
            url(r"/img/(?P<art>.+)$", ImageHandler, name="image"),
            url(r"/", LottiePlayerHandler, name="lottie")
        ]
        
        settings = {
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "debug": True,
        }
        
        tornado.web.Application.__init__(self, handlers)
        

def main():
    app = App()
    port = 5000
    
    app.listen(port)
    print("The server is listening on http://localhost:"+str(port))
    IOLoop().instance().start()
    
if __name__ == "__main__":
    main()
