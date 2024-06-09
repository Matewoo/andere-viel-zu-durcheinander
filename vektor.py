from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QKeySequence, QImage, QPainter, QColor, QPen
from PySide6.QtWidgets import QApplication, QMenuBar, QToolBar, QWidget, QFileDialog, QMainWindow, QMessageBox, QVBoxLayout, QInputDialog, QColorDialog
import sys
import math
from abc import ABC ,abstractmethod
# Datenstrukturen für Vektorgrafik


class Shape(ABC):
    def __init__(self, x, y, width, height, fill_color, border_color, border_width, zindex):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.fill_color = fill_color
        self.border_color = border_color
        self.border_width = border_width
        self.zindex = zindex

    @abstractmethod
    def painter(self):
        pass


class Rectangle(Shape):

    def painter(self):
        return super().painter()

    def contains(self, point):
        return self.x <= point.x() <= self.x + self.width and self.y <= point.y() <= self.y + self.height

class Circle:
    def __init__(self, x, y, radius, fill_color, border_color):
        self.x = x
        self.y = y
        self.radius = radius
        self.fill_color = fill_color
        self.border_color = border_color

    def contains(self, point):
        return (self.x - point.x())**2 + (self.y - point.y())**2 <= self.radius**2

class Star:
    def __init__(self, x, y, radius, points, fill_color, border_color, border_width):
        self.x = x
        self.y = y
        self.radius = radius
        self.points = points
        self.fill_color = fill_color
        self.border_color = border_color
        self.border_width = border_width

    def contains(self, point):
        # A simple bounding box check for demonstration purposes
        return self.x - self.radius <= point.x() <= self.x + self.radius and self.y - self.radius <= point.y() <= self.y + self.radius

class Scene:
    def __init__(self):
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

class MyPaintArea(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setMinimumWidth(640)
        self.setMinimumHeight(480)
        self.image: QImage = QImage(640, 480, QImage.Format_RGB32)
        self.image.fill(QColor(255, 255, 255))
        self.scene = Scene()
        self.selected_object = None
        self.last_mouse_position = QPointF()

    def load_image(self, filename):
        self.image = QImage(filename)
        self.update()

    def paintEvent(self, event):
        painter: QPainter = QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.render_scene(painter, QRectF(0, 0, self.width(), self.height()), QRectF(0, 0, 640, 480))
        painter.end()

    def render_scene(self, painter, viewport, world_rect):
        painter.setRenderHint(QPainter.Antialiasing)

        scale_x = viewport.width() / world_rect.width()
        scale_y = viewport.height() / world_rect.height()
        scale = min(scale_x, scale_y)

        painter.scale(scale, scale)
        painter.translate(-world_rect.left(), -world_rect.top())

        for obj in self.scene.objects:
            if isinstance(obj, Rectangle):
                pen = QPen(QColor(*obj.border_color))
                pen.setWidth(obj.border_width)  # Set the border width
                painter.setPen(pen)
                painter.setBrush(QColor(*obj.fill_color))
                painter.drawRect(obj.x, obj.y, obj.width, obj.height)
            elif isinstance(obj, Circle):
                painter.setBrush(QColor(*obj.fill_color))
                painter.setPen(QColor(*obj.border_color))
                painter.drawEllipse(obj.x - obj.radius, obj.y - obj.radius, 2 * obj.radius, 2 * obj.radius)
            elif isinstance(obj, Star):
                painter.setBrush(QColor(*obj.fill_color))
                painter.setPen(QColor(*obj.border_color))
                self.draw_star(painter, obj)

    def draw_star(self, painter, star):
        points = []
        angle = math.pi / star.points  # Winkel für einen Sternzacken

        for i in range(2 * star.points):
            r = star.radius if i % 2 == 0 else star.radius / 2
            theta = i * angle
            x = star.x + r * math.cos(theta)
            y = star.y + r * math.sin(theta)
            points.append(QPointF(x, y))
        
        painter.drawPolygon(points)

    def rectangle(self, x, y, width, height, fill_color, border_color, border_width, zindex):
        self.scene.add_object(Rectangle(x, y, width, height, fill_color, border_color, border_width, zindex))
        self.update()
    
    def circle(self, x,y, radius, fill_color, border_color):
        self.scene.add_object(Circle(x, y, radius, fill_color, border_color))
        self.update()

    def star(self, x, y, radius, points, fill_color, border_color, border_width):
        self.scene.add_object(Star(x, y, radius, points, fill_color, border_color, border_width))
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected_object = self.find_object_at(event.position())
            self.last_mouse_position = event.position()

    def mouseMoveEvent(self, event):
        if self.selected_object:
            dx = event.position().x() - self.last_mouse_position.x()
            dy = event.position().y() - self.last_mouse_position.y()
            self.last_mouse_position = event.position()

            if isinstance(self.selected_object, (Rectangle, Circle, Star)):
                self.selected_object.x += dx
                self.selected_object.y += dy

            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected_object = None

    def find_object_at(self, position):
        for obj in self.scene.objects:
            if obj.contains(position):
                return obj
        return None
    

    def draw_scene_1(self):
        self.scene.objects = []
        self.scene.add_object(Rectangle(200, 150, 200, 200, (255, 255, 255), (0, 255, 0)))
        self.scene.add_object(Circle(300, 250, 100, (255, 255, 255), (0, 0, 255)))
        self.update()

    def draw_scene_2(self):
        cord_x = 100
        cord_y = 100
        size = 100
        offset = 5
        self.scene.objects = []
        self.scene.add_object(Circle((cord_x+size/2), cord_y+size/2, size/2, (255, 0, 255), (0, 0, 255)))
        self.scene.add_object(Rectangle((cord_x+size+offset), cord_y, size, size, (100, 255, 255), (0, 255, 0)))
        self.scene.add_object(Rectangle((cord_x+size*2)+offset*2, cord_y, size, size, (100, 255, 255), (0, 255, 0)))
        self.scene.add_object(Circle(cord_x+size*3+size/2+offset*3, cord_y+size/2, size/2, (255, 0, 255), (0, 0, 255)))

        self.scene.add_object(Rectangle(cord_x, cord_y+size+offset, size, size, (100, 255, 255), (0, 255, 0)))
        self.scene.add_object(Rectangle(cord_x+size*3+offset*3, cord_y+size+offset, size, size, (100, 255, 255), (0, 255, 0)))

        self.scene.add_object(Circle((cord_x+size/2), cord_y+size*2+size/2+offset*2, size/2, (255, 0, 255), (0, 0, 255)))
        self.scene.add_object(Rectangle((cord_x+size+offset), cord_y+size*2+offset*2, size, size, (100, 255, 255), (0, 255, 0)))
        self.scene.add_object(Rectangle((cord_x+size*2)+offset*2, cord_y+size*2+offset*2, size, size, (100, 255, 255), (0, 255, 0)))
        self.scene.add_object(Circle(cord_x+size*3+size/2+offset*3, cord_y+size*2+size/2+offset*2, size/2, (255, 0, 255), (0, 0, 255)))
        self.update()

class MyWindow(QMainWindow):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.zindex = 0
        self.paint_area: MyPaintArea = MyPaintArea(self)
        layout = QVBoxLayout()
        layout.addWidget(self.paint_area)

        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        #menüs und aktionen
        self.file_menu: QMenuBar = self.menuBar().addMenu("File...")
        self.help_menu: QMenuBar = self.menuBar().addMenu("Help...")
        self.scene_menu: QMenuBar = self.menuBar().addMenu("Scene...")
        self.open_action = self.file_menu.addAction("Open File")
        self.open_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_O))
        self.saveAs_action = self.file_menu.addAction("Save As...")
        self.saveAs_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_S))
        self.quit_action = self.file_menu.addAction("Quit")
        self.quit_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_Q))
        self.info_action = self.help_menu.addAction("Info")
        self.info_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_I))
        self.scene_1_action = self.scene_menu.addAction("Scene 1")
        self.scene_1_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_1))
        self.scene_1_action.triggered.connect(self.paint_area.draw_scene_1)
        self.scene_2_action = self.scene_menu.addAction("Scene 2")
        self.scene_2_action.setShortcut(QKeySequence(Qt.CTRL | Qt.Key_2))
        self.scene_2_action.triggered.connect(self.paint_area.draw_scene_2)

        self.open_action.triggered.connect(self.load_file)
        self.saveAs_action.triggered.connect(self.save_file)
        self.info_action.triggered.connect(self.show_info)
        self.quit_action.triggered.connect(self.show_quit_warning)
        
        #toolbar
        self.nice_toolbar: QToolBar = self.addToolBar("Some Nice Tools")
        self.nice_toolbar.addAction("Open", self.load_file)
        self.nice_toolbar.addAction("Save", self.save_file)
        self.nice_toolbar.addAction("Info", self.show_info)
        self.nice_toolbar.addAction("Quit", self.show_quit_warning)
        self.nice_toolbar.addAction("Rectangle", self.values_Rectangle)
        self.nice_toolbar.addAction("Circle", self.values_Circle)
        self.nice_toolbar.addAction("Star", self.values_Star)

    def show_quit_warning(self):
        ret = QMessageBox.question(self, "Ufpasse!", "Möchtest Du das Programm wirklich schließen? :(", QMessageBox.Yes, QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.close()
        else:
            print("Programm wird fortgesetzt")
    
    def show_info(self):
        QMessageBox.information(self, "Info", "Eine super nützliche Information...", QMessageBox.Ok)

    def load_file(self):
        file_name, selected_filter = QFileDialog.getOpenFileName(self, "Open Image", "", "PNG Files (*.png)")
        if file_name:
            self.paint_area.load_image(file_name)

    def save_file(self):
        file_name, selected_filter = QFileDialog.getSaveFileName(self, "Save As", "picture", "PNG Files (*.png)")
        if file_name:
            self.paint_area.image.save(file_name)

    def values_Rectangle(self):
        x=QInputDialog.getInt(self,"X","X")
        y=QInputDialog.getInt(self,"Y","Y")
        width=QInputDialog.getInt(self,"Breite","Pixel")
        height=QInputDialog.getInt(self,"Höhe","Pixel")
        fill_color = QColorDialog.getColor(QColor(255, 255, 255), self, "Füllfarbe")
        if fill_color.isValid():
            fill_color = fill_color.getRgb()[:3]
        border_color = QColorDialog.getColor(QColor(255, 255, 255), self, "Randfarbe")
        if border_color.isValid():
            border_color = border_color.getRgb()[:3]
        border_width, _ =QInputDialog.getInt(self,"Randbreite","Pixel")
        self.zindex+=1
        print(self.zindex)
        print(border_width)
        self.paint_area.rectangle(x[0],y[0],width[0],height[0],fill_color,border_color, border_width, self.zindex)

    def values_Circle(self):
        x=QInputDialog.getInt(self,"X","X")
        y=QInputDialog.getInt(self,"Y","Y")
        radius=QInputDialog.getInt(self,"Radius","Pixel")
        fill_color=QInputDialog.getText(self,"Farbe","r,g,b")
        fill_color=tuple(map(int, fill_color[0].split(",")))
        border_color=QInputDialog.getText(self,"Randfarbe","r,g,b")
        border_color=tuple(map(int, border_color[0].split(",")))
        self.paint_area.circle(x[0],y[0],radius[0],fill_color,border_color)

    def values_Star(self):
        x=QInputDialog.getInt(self,"X","X")
        y=QInputDialog.getInt(self,"Y","Y")
        radius=QInputDialog.getInt(self,"Radius","Pixel")
        points=QInputDialog.getInt(self,"Ecken","Anzahl")
        fill_color=QInputDialog.getText(self,"Farbe","r,g,b")
        fill_color=tuple(map(int, fill_color[0].split(",")))
        border_color=QInputDialog.getText(self,"Randfarbe","r,g,b")
        border_color=tuple(map(int, border_color[0].split(",")))
        border_width=QInputDialog.getInt(self,"Randbreite","Pixel")
        self.paint_area.star(x[0],y[0],radius[0],points[0],fill_color,border_color,border_width[0])

if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)
    main_window: MyWindow = MyWindow(None)
    main_window.setWindowTitle("Vektorgraphik Editor")
    main_window.show()
    app.exec()
