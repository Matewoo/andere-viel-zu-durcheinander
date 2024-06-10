from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QKeySequence, QImage, QPainter, QColor, QPen
from PySide6.QtWidgets import QApplication, QMenuBar, QToolBar, QWidget, QFileDialog, QMainWindow, QMessageBox, QVBoxLayout, QInputDialog, QColorDialog, QDialog, QFormLayout, QLineEdit, QPushButton, QDialogButtonBox
import sys
import math
from abc import ABC ,abstractmethod
# Datenstrukturen für Vektorgrafik


class Shape(ABC):
    def __init__(self, x, y, fill_color, border_color, border_width, zindex, isclicked):
        self.x = x
        self.y = y
        self.fill_color = fill_color
        self.border_color = border_color
        self.border_width = border_width
        self.zindex = zindex
        self.isclicked = isclicked

    @abstractmethod
    def painter(self):
        pass
    
    def contains(self):
        pass

    def box(self):
        pass


class Rectangle(Shape):

    def __init__(self, x, y, width, height, fill_color, border_color, border_width, zindex, isclicked):
        super().__init__(x, y, fill_color, border_color, border_width, zindex, isclicked)
        self.width = width
        self.height = height
        self.box = False
    def painter(self):
        return super().painter()

    def contains(self, point):
        return self.x <= point.x() <= self.x + self.width and self.y <= point.y() <= self.y + self.height

class Circle(Shape):
    def __init__(self, x, y, radius, fill_color, border_color, border_width, zindex):
        super().__init__(x, y, fill_color, border_color, border_width, zindex)
        self.radius = radius

    def painter(self):
        return super().painter()

    def contains(self, point):
        return (self.x - point.x())**2 + (self.y - point.y())**2 <= self.radius**2

class Star:
    def __init__(self, x, y, radius, points, fill_color, border_color, border_width, zindex):
        super().__init__(x, y, fill_color, border_color, border_width, zindex)
        self.radius = radius
        self.points = points

    def painter(self):
        return super().painter()

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
        self.last_object = None
        self.special_object = None
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
                if obj.isclicked == True:
                    pen.setColor(QColor(255,0,0))
                pen.setWidth(obj.border_width)  # Set the border width
                painter.setPen(pen)
                painter.setBrush(QColor(*obj.fill_color))
                painter.drawRect(obj.x, obj.y, obj.width, obj.height)
                if obj.box ==True:
                    pen = QPen(QColor(255,0,0))
                    pen.setWidth(5)
                    painter.drawLine(obj.x, obj.y, obj.width, obj.height)
            elif isinstance(obj, Circle):
                pen = QPen(QColor(*obj.border_color))
                pen.setWidth(obj.border_width)
                painter.setPen(pen)
                painter.setBrush(QColor(*obj.fill_color))
                painter.drawEllipse(obj.x - obj.radius, obj.y - obj.radius, 2 * obj.radius, 2 * obj.radius)
            elif isinstance(obj, Star):
                pen = QPen(QColor(*obj.border_color))
                pen.setWidth(obj.border_width)
                painter.setPen(pen)
                painter.setBrush(QColor(*obj.fill_color))
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

    def rectangle(self, x, y, width, height, fill_color, border_color, border_width, zindex, isclicked):
        self.scene.add_object(Rectangle(x, y, width, height, fill_color, border_color, border_width, zindex, isclicked))
        self.update()
    
    def circle(self, x,y, radius, fill_color, border_color, border_width, zindex):
        self.scene.add_object(Circle(x, y, radius, fill_color, border_color, border_width, zindex))
        self.update()

    def star(self, x, y, radius, points, fill_color, border_color, border_width, zindex):
        self.scene.add_object(Star(x, y, radius, points, fill_color, border_color, border_width, zindex))
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected_object = self.find_object_at(event.position())
            if self.selected_object:
                self.last_object = self.selected_object
                self.selected_object.isclicked = True
                self.update()
            else:
                self.last_object.isclicked = False
                self.update()
            print(self.selected_object)
            self.last_mouse_position = event.position()

        if event.button() == Qt.RightButton:
            if not self.special_object == None:
                self.special_object.box == False
                self.special_object = None

                self.special_object = self.find_object_at(event.position())
                if self.special_object:
                    self.special_object.box = True
                self.last_mouse_position = event.position()


    def mouseMoveEvent(self, event):
        if self.selected_object:
            dx = event.position().x() - self.last_mouse_position.x()
            dy = event.position().y() - self.last_mouse_position.y()
            self.last_mouse_position = event.position()

            if isinstance(self.selected_object, (Rectangle, Circle, Star)):
                self.selected_object.x += dx
                self.selected_object.y += dy
        
        if self.special_object:
            self.special_object.box=True
        
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
        dialog = RectInput(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            val = dialog.get_values()
            self.zindex+=1
            print(self.zindex)
            self.paint_area.rectangle(val[0],val[1],val[2],val[3],val[4],val[5],val[6], self.zindex, False)

    def values_Circle(self):
        dialog = CircleInput(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            val = dialog.get_values()
            self.zindex+=1
            print(self.zindex)
            self.paint_area.circle(val[0],val[1],val[2],val[3],val[4],val[5], self.zindex, False)

        

    def values_Star(self):
        dialog = StarInput(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            val = dialog.get_values()
            print(val)
            self.zindex+=1
            print(self.zindex)
            self.paint_area.circle(val[0],val[1],val[2],val[3],val[4],val[5], self.zindex)

class RectInput(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Rechteck")
        self.layout = QFormLayout(self)
        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        self.width_input = QLineEdit()
        self.height_input= QLineEdit()
        self.füllfarbe = (0,0,0)
        self.randfarbe = (0,0,0)
        self.border_width = QLineEdit()


        self.layout.addRow("Position X:", self.x_input)
        self.layout.addRow("Position Y:", self.y_input)
        self.layout.addRow("Breite:", self.width_input)
        self.layout.addRow("Höhe:",self.height_input)

        self.button_füll = QPushButton("Füllfarbe wählen")
        self.button_füll.clicked.connect(self.pick_color_füll)
        self.layout.addRow("Füllfarbe:", self.button_füll)

        self.button_rand = QPushButton("Randfarbe wählen")
        self.button_rand.clicked.connect(self.pick_color_rand)
        self.layout.addRow("Randfarbe:",self.button_rand)

        self.layout.addRow("Randbreite:", self.border_width)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        
    def pick_color_füll(self):
        color = ((QColorDialog.getColor(QColor(255, 255, 255), self, "Füllfarbe wählen")).getRgb())[:3]
        self.füllfarbe = color
        print(color)

    def pick_color_rand(self):
        color = ((QColorDialog.getColor(QColor(255, 255, 255), self, "Randfarbe wählen")).getRgb())[:3]
        self.randfarbe = color
        print(color)

    def get_values(self):
        x = int(self.x_input.text())
        y = int(self.y_input.text())
        width = int(self.width_input.text())
        height = int(self.height_input.text())
        border_width = int(self.border_width.text())
        return(x, y, width, height, self.füllfarbe, self.randfarbe, border_width)
    
class CircleInput(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Kreis")
        self.layout = QFormLayout(self)
        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        self.radius_input = QLineEdit()
        self.füllfarbe = (0,0,0)
        self.randfarbe = (0,0,0)
        self.border_width = QLineEdit()


        self.layout.addRow("Position X:", self.x_input)
        self.layout.addRow("Position Y:", self.y_input)
        self.layout.addRow("Radius:", self.radius_input)

        self.button_füll = QPushButton("Füllfarbe wählen")
        self.button_füll.clicked.connect(self.pick_color_füll)
        self.layout.addRow("Füllfarbe:", self.button_füll)

        self.button_rand = QPushButton("Randfarbe wählen")
        self.button_rand.clicked.connect(self.pick_color_rand)
        self.layout.addRow("Randfarbe:",self.button_rand)

        self.layout.addRow("Randbreite:", self.border_width)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        
    def pick_color_füll(self):
        color = ((QColorDialog.getColor(QColor(255, 255, 255), self, "Füllfarbe wählen")).getRgb())[:3]
        self.füllfarbe = color
        print(color)

    def pick_color_rand(self):
        color = ((QColorDialog.getColor(QColor(255, 255, 255), self, "Randfarbe wählen")).getRgb())[:3]
        self.randfarbe = color
        print(color)

    def get_values(self):
        x = int(self.x_input.text())
        y = int(self.y_input.text())
        radius = int(self.radius_input.text())
        border_width = int(self.border_width.text())
        return(x, y, radius, self.füllfarbe, self.randfarbe, border_width)
    
class StarInput(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Stern")
        self.layout = QFormLayout(self)
        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        self.radius_input = QLineEdit()
        self.points_input = QLineEdit()
        self.füllfarbe = (0,0,0)
        self.randfarbe = (0,0,0)
        self.border_width = QLineEdit()


        self.layout.addRow("Position X:", self.x_input)
        self.layout.addRow("Position Y:", self.y_input)
        self.layout.addRow("Radius:", self.radius_input)
        self.layout.addRow("Ecken:",self.points_input)

        self.button_füll = QPushButton("Füllfarbe wählen")
        self.button_füll.clicked.connect(self.pick_color_füll)
        self.layout.addRow("Füllfarbe:", self.button_füll)

        self.button_rand = QPushButton("Randfarbe wählen")
        self.button_rand.clicked.connect(self.pick_color_rand)
        self.layout.addRow("Randfarbe:",self.button_rand)

        self.layout.addRow("Randbreite:", self.border_width)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        
    def pick_color_füll(self):
        color = ((QColorDialog.getColor(QColor(255, 255, 255), self, "Füllfarbe wählen")).getRgb())[:3]
        self.füllfarbe = color
        print(color)

    def pick_color_rand(self):
        color = ((QColorDialog.getColor(QColor(255, 255, 255), self, "Randfarbe wählen")).getRgb())[:3]
        self.randfarbe = color
        print(color)

    def get_values(self):
        x = int(self.x_input.text())
        y = int(self.y_input.text())
        radius = int(self.radius_input.text())
        points = int(self.points_input.text())
        border_width = int(self.border_width.text())
        return(x, y, radius, points, self.füllfarbe, self.randfarbe, border_width)


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)
    main_window: MyWindow = MyWindow(None)
    main_window.setWindowTitle("Vektorgraphik Editor")
    main_window.show()
    app.exec()
    
