import sys
import random
from PyQt5 import QtWidgets, QtGui, QtCore
from grafos_ui import Ui_MainWindow
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem

class Nodo(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, id, app):
        super().__init__(-radius, -radius, 2 * radius, 2 * radius)  # Dibujar el nodo centrado
        self.setBrush(QtGui.QBrush(QtGui.QColor("lightblue")))
        self.setPen(QtGui.QPen(QtCore.Qt.black))
        self.id = id
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)
        self.text_item = QGraphicsTextItem(f"Nodo {self.id}", self)
        self.text_item.setPos(-10, -10)  # Ajusta la posición del texto para que no se superponga con el nodo
        self.app = app  # Referencia a la aplicación para actualizar las aristas
        self.aristas = []  # Para guardar las aristas conectadas a este nodo

    def agregar_arista(self, arista):
        self.aristas.append(arista)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # Cuando se mueva el nodo, actualizar las aristas
            for arista in self.aristas:
                arista.actualizar_posiciones()
        return super().itemChange(change, value)

class Arista(QGraphicsLineItem):
    def __init__(self, nodo1, nodo2, peso, scene):
        super().__init__()
        self.nodo1 = nodo1
        self.nodo2 = nodo2
        self.peso = peso
        self.scene = scene

        # Agregar el peso de la arista como un texto
        self.text_item = QGraphicsTextItem(str(self.peso))
        self.scene.addItem(self.text_item)

        # Agregar la línea y actualizar posiciones
        self.actualizar_posiciones()

        # Establecer el evento de clic para engrosar la arista y los nodos conectados
        self.setFlag(QGraphicsLineItem.ItemIsSelectable)
        self.setPen(QtGui.QPen(QtCore.Qt.black))

    def actualizar_posiciones(self):
        x1, y1 = self.nodo1.scenePos().x(), self.nodo1.scenePos().y()
        x2, y2 = self.nodo2.scenePos().x(), self.nodo2.scenePos().y()

        # Actualizar la línea de la arista
        self.setLine(x1, y1, x2, y2)

        # Colocar el texto en el centro de la línea
        self.text_item.setPos((x1 + x2) / 2, (y1 + y2) / 2)

    def mousePressEvent(self, event):
        # Engrosar la línea y los nodos conectados al hacer clic en la arista
        self.setPen(QtGui.QPen(QtCore.Qt.red, 3))  # Cambia el color y grosor de la arista
        self.nodo1.setPen(QtGui.QPen(QtCore.Qt.red, 3))  # Engrosar el nodo1
        self.nodo2.setPen(QtGui.QPen(QtCore.Qt.red, 3))  # Engrosar el nodo2
        super().mousePressEvent(event)  # Llama al evento de clic original

class GrafoApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(GrafoApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Crear un QLabel
        self.lblTitulo2 = QtWidgets.QLabel(self)
        self.lblTitulo2.setGeometry(10, 10, 100, 100)  # Ajusta la posición y tamaño del QLabel

        # Cargar la imagen
        pixmap = QtGui.QPixmap("Recurso-1-8.png")

        # Redimensionar la imagen (por ejemplo, a 100x100 píxeles)
        pixmap = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio)

        # Usar el graphicsView existente
        self.graphicsView = self.ui.graphicsView

        # Configurar la escena del QGraphicsView
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        # Conectar el botón para generar el grafo
        self.ui.btnPintarGrafo.clicked.connect(self.dibujar_grafo)

        # Conectar el clic en la barra de título del QTableWidget para llenar con valores aleatorios
        self.ui.tableWidget.horizontalHeader().sectionClicked.connect(self.llenar_matriz_aleatoria)

        # Lista para almacenar los nodos y las aristas
        self.nodos = []
        self.aristas = []

    def dibujar_grafo(self):
        try:
            # Limpiar la escena y listas
            self.scene.clear()
            self.nodos.clear()
            self.aristas.clear()

            # Obtener la nueva matriz de la UI y dibujar el grafo
            matriz = self.obtener_matriz()

            # Dibujar nodos y aristas
            self.dibujar_nodos_y_aristas(matriz)

            # Generar matriz de adyacencia
            matriz_adyacencia = self.generar_matriz_adyacencia(matriz)

            # Generar las k-trayectorias usando la matriz de adyacencia
            self.generar_k_trayectorias(matriz_adyacencia, 2)  # Con k=2
            self.generar_k_trayectorias(matriz_adyacencia, 3)  # Con k=3
        except Exception as e:
            print(f"Error al dibujar el grafo: {e}")

    def generar_matriz_adyacencia(self, matriz):
        """Genera la matriz de adyacencia a partir de la matriz de pesos"""
        try:
            num_nodos = len(matriz)
            matriz_adyacencia = [[0] * num_nodos for _ in range(num_nodos)]

            for i in range(num_nodos):
                for j in range(num_nodos):
                    if matriz[i][j] > 0:
                        matriz_adyacencia[i][j] = 1

            # Muestra la matriz de adyacencia en la UI
            self.mostrar_matriz_en_ui(matriz_adyacencia, self.ui.MatrizAdyacencia)
            return matriz_adyacencia
        except Exception as e:
            print(f"Error al generar la matriz de adyacencia: {e}")
            return []

    def obtener_matriz(self):
        try:
            filas = self.ui.tableWidget.rowCount()
            columnas = self.ui.tableWidget.columnCount()
            matriz = []
            for i in range(filas):
                fila = []
                for j in range(columnas):
                    item = self.ui.tableWidget.item(i, j)
                    valor = int(item.text()) if item and item.text().isdigit() else 0
                    fila.append(valor)
                matriz.append(fila)
            return matriz
        except Exception as e:
            print(f"Error al obtener la matriz: {e}")
            return []

    def dibujar_nodos_y_aristas(self, matriz):
        try:
            num_nodos = len(matriz)
            radius = 20

            # Definir los límites para la posición aleatoria de los nodos
            width = self.graphicsView.width() - 100
            height = self.graphicsView.height() - 100

            # Dibujar nodos
            for i in range(num_nodos):
                x = random.randint(50, width)  # Coordenada x aleatoria
                y = random.randint(50, height)  # Coordenada y aleatoria
                nodo = Nodo(x, y, radius, i + 1, self)
                nodo.setPos(x, y)  # Posicionar el nodo en la escena
                self.scene.addItem(nodo)
                self.nodos.append(nodo)

            # Dibujar aristas
            for i in range(num_nodos):
                for j in range(i + 1, num_nodos):
                    peso = matriz[i][j]
                    if peso > 0:
                        nodo1 = self.nodos[i]
                        nodo2 = self.nodos[j]

                        # Crear y agregar arista
                        arista = Arista(nodo1, nodo2, peso, self.scene)
                        self.aristas.append(arista)
                        self.scene.addItem(arista)

                        # Agregar aristas a los nodos para que se actualicen al moverlos
                        nodo1.agregar_arista(arista)
                        nodo2.agregar_arista(arista)

        except Exception as e:
            print(f"Error al dibujar nodos y aristas: {e}")

    def llenar_matriz_aleatoria(self, index):
        """Llena toda la matriz con valores aleatorios entre 0 y 100, con 0 en las diagonales."""
        try:
            filas = self.ui.tableWidget.rowCount()
            columnas = self.ui.tableWidget.columnCount()
            probabilidad_no_conexion = 0.3  # Probabilidad de que no haya conexión entre dos nodos

            for i in range(filas):
                for j in range(columnas):
                    if i == j:
                        self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem('0'))  # No aristas a sí mismo
                    else:
                        if random.random() < probabilidad_no_conexion:
                            self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem('0')) # Sin conexión
                        else:
                            valor_aleatorio = random.randint(1, 100)  # Valor aleatorio entre 1 y 100
                            self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(valor_aleatorio)))
        except Exception as e:
            print(f"Error al llenar la matriz: {e}")

    def generar_k_trayectorias(self, matriz_adyacencia, k):
        """Genera las k-trayectorias a partir de la matriz de adyacencia."""
        try:
            #Inicializa la matriz de k-trayectorias con ceros
            num_nodos = len(matriz_adyacencia)
            k_trayectorias = [[0] * num_nodos for _ in range(num_nodos)]

            for i in range(num_nodos):
                for j in range(num_nodos):
                    k_trayectorias[i][j] = self.calcular_k_trayectoria(matriz_adyacencia, i, j, k)

            # Muestra la k-trayectoria en la UI
            if k == 2:
                self.mostrar_matriz_en_ui(k_trayectorias, self.ui.MatrizK2)
            elif k == 3:
                self.mostrar_matriz_en_ui(k_trayectorias, self.ui.MatrizK3)
        except Exception as e:
            print(f"Error al generar k-trayectorias: {e}")

    def calcular_k_trayectoria(self, matriz_adyacencia, origen, destino, k):
        """Calcula la k-trayectoria entre dos nodos."""
        if k == 1:
            return matriz_adyacencia[origen][destino]
        else:
            suma = 0
            for intermedio in range(len(matriz_adyacencia)):
                suma += self.calcular_k_trayectoria(matriz_adyacencia, origen, intermedio, k - 1) * matriz_adyacencia[intermedio][destino]
                #[origen][intermedio] * [intermedio][destino]
            return suma

    def mostrar_matriz_en_ui(self, matriz, table_widget):
        """Muestra la matriz en un QTableWidget."""
        try:
            filas = len(matriz)
            columnas = len(matriz[0])
            table_widget.setRowCount(filas)
            table_widget.setColumnCount(columnas)

            for i in range(filas):
                for j in range(columnas):
                    table_widget.setItem(i, j, QtWidgets.QTableWidgetItem(str(matriz[i][j])))
        except Exception as e:
            print(f"Error al mostrar la matriz en la UI: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GrafoApp()
    window.show()
    sys.exit(app.exec_())
