#!./venv/bin/python3
import math
import os

import tornado.web
from lottie import Point, Color
from lottie import objects
from lottie.utils import animation as anutils
from lottie.utils import script
from lottie.utils.animation import follow_path
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler, url

points = [
    (80, 40),
    (95, 100),
    (230, 100),
    (230, 245),
    (400, 245),
    (300, 313),
    (423, 412),
    (245, 354),
    (60, 200),
    (380, 80),
]

DUREE = 200
MARGE_COIN = 2
INDEX_HTML = "index.html"


def calculate_distance(a: Point, b: Point):
    return math.sqrt((b[0] - a[0]) ** 2 + (b[1] -a[1]) ** 2)


def nearest_point(a: Point, vertex: Point) -> Point:
    distance = calculate_distance(a, vertex)
    middle = Point((a[0] + vertex[0]) / 2, (a[1] + vertex[1]) / 2)

    if distance <= MARGE_COIN:
        return middle

    else:
        return nearest_point(middle, vertex)

def get_points_around_vertex(a: Point, vertex: Point, c: Point):
    a1 = nearest_point(a, vertex)
    b1 = nearest_point(c, vertex)
    # points.append(a1,b1)

    print("#"*20)
    print(a1)
    print(vertex)
    print(b1)
    print("#" * 20)
    return a1, b1

def add_points_to_bezier(bez, les_points):
    size = len(les_points) - 2
    previous = None
    for i in range(size + 1):
        if i == 0:
            bez.shape.value.add_point(Point(les_points[i][0], les_points[i][1]))
            previous = les_points[i]

        else:
            before_point, after_point = get_points_around_vertex(previous, les_points[i], les_points[i + 1])

            bez.shape.value.add_point(Point(before_point.x, before_point.y))
            bez.shape.value.add_point(Point(les_points[i][0], les_points[i][1]))
            bez.shape.value.add_point(Point(after_point.x, after_point.y))
    bez.shape.value.add_point(Point(les_points[size + 1][0], les_points[size + 1][1]))


class FollowPathHandler(RequestHandler):
    def get(self, art):
        background_image = objects.assets.Image().load("./static/images/mappy.jpg")
        an = objects.Animation(DUREE)
        an.assets.append(background_image)

        layer = objects.ShapeLayer()

        an.add_layer(layer)
        an.add_layer(objects.ImageLayer(background_image.id))

        group = layer.add_shape(objects.Group())
        ball = group.add_shape(objects.Ellipse())
        ball.size.value = Point(20, 20)
        
        les_points = list(points)

        group.add_shape(objects.Fill(Color(1, 0, 0)))

        group = layer.add_shape(objects.Group())
        bez = group.add_shape(objects.Path())

        add_points_to_bezier(bez, les_points)

        group.add_shape(objects.Stroke(Color(0, 1, 0), 10))

        sequence = 3 * int(DUREE / len(les_points) - 1)
        i = 0 - sequence
        while i < DUREE:
            i = i + sequence
            follow_path(ball.position, bez.shape.value, 0, 60, 30, False, Point(0, 0))
            follow_path(ball.position, bez.shape.value, 60, 120, 30, False, Point(0, 0))
            follow_path(ball.position, bez.shape.value, 120, 180, 30, False, Point(0, 0))

        # print(an.to_dict())
        script.script_main(an, path="./static/", basename=art, formats=["json"])
        
        self.render(INDEX_HTML)




class ImageHandler(RequestHandler):
    
    def get(self, art):
        background_image = objects.assets.Image().load("./static/images/mappy.jpg")
        an = objects.Animation(180)
        an.assets.append(background_image)

        layer = objects.ShapeLayer()

        an.add_layer(layer)
        an.add_layer(objects.ImageLayer(background_image.id))

        group = layer.add_shape(objects.Group())
        bez = group.add_shape(objects.Path())
        les_points = list(points)

        add_points_to_bezier(bez, les_points)

        group.add_shape(objects.Stroke(Color(1, 0, 0), 10))


        group = layer.add_shape(objects.Group())
        sh = anutils.generate_path_segment(bez.shape.value, 0, 180, 60, 180, 30, False)
        group.add_shape(sh)
        group.add_shape(objects.Stroke(Color(0, 1, 0), 20))

        # print(an.to_dict())
        script.script_main(an, path="./static/", basename=art, formats=["json"])
        
        self.render(INDEX_HTML)
        
        
class LottiePlayerHandler(RequestHandler):
    def get(self):
        self.render(INDEX_HTML)
    
        
class App(Application):
    def __init__(self):
        handlers = [
            url(r"/img/(?P<art>.+)$", ImageHandler, name="image"),
            url(r"/follow_path/(?P<art>.+)$", FollowPathHandler, name="follow_path"),
            url(r"/", LottiePlayerHandler, name="lottie")
        ]
        
        settings = {
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "debug": True,
        }
        
        tornado.web.Application.__init__(self, handlers, **settings)
        

def main():
    app = App()
    port = 5000
    
    app.listen(port)
    print("The server is listening on http://localhost:"+str(port))
    IOLoop().instance().start()
    
if __name__ == "__main__":
    main()
