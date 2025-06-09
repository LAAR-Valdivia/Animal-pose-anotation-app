# Autor: Joseba Iribarren L.
# Función: Facilitar la identificación de partes de animales

import tkinter as tk
import os
import csv
from tkinter import filedialog, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk


class PhotoViewer:
    def __init__(self, master):

        # Settings
        self.tamano_oval = 3
        self.ancho_base_imagen = 1300
        self.largo_base_imagen = 700 

        self.master_ancho = 1400
        self.master_largo = 800

        self.master = master
        self.master.title("Visualizador de Fotos")
        self.master.geometry(str(self.master_ancho)+'x'+str(self.master_largo))

        self.current_image = None
        self.image_list = []
        self.current_index = -1
        self.original_image = None
        self.click_coordinates = []
        self.click_ovals = []
        self.click_ovals_id = []
        self.ancho_imagen = self.ancho_base_imagen
        self.largo_imagen = self.largo_base_imagen
        items = None

        self.zoom_factor = 1
        self.ZOOM_STEP = 0.5

        # Bounding Box variables
        self.drawing_mode = "bbox"  # "points" o "bbox"
        self.bounding_boxes = []
        self.current_bbox = None
        self.bbox_start = None
        self.bbox_rectangles = []
        self.bbox_id = 0

        self.bbox_rectangles_label = []


        # Frame para botones
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(side=tk.TOP, pady=10)
        
        # Botones
        self.open_button = tk.Button(self.button_frame, text="Open folder", command=self.open_folder)
        self.open_button.pack(side=tk.LEFT, padx=5)

        self.prev_button = tk.Button(self.button_frame, text="Previous", command=self.show_previous)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(self.button_frame, text="Next", command=self.show_next)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_coordinates)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.oval_size = tk.Button(self.button_frame, text="Oval size", command=self.oval_size_changer)
        self.oval_size.pack(side=tk.LEFT, padx=5)

        self.zoom_in_button = tk.Button(self.button_frame, text="Zoom in", command=self.zoom_in)
        self.zoom_in_button.pack(side=tk.LEFT, padx=5)

        self.zoom_out_button = tk.Button(self.button_frame, text="Zoom out", command=self.zoom_out)
        self.zoom_out_button.pack(side=tk.LEFT, padx=5)

        self.restore_button = tk.Button(self.button_frame, text="Restore", command=self.Restore)
        self.restore_button.pack(side=tk.LEFT, padx=5)


        # Separador
        separator = tk.Frame(self.button_frame, width=2, bg="gray")
        separator.pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Botones para Bounding Box
        self.mode_button = tk.Button(self.button_frame, text="Mode: bbox", command=self.toggle_mode, bg="lightgreen")
        self.mode_button.pack(side=tk.LEFT, padx=5)

        self.clear_bbox_button = tk.Button(self.button_frame, text="Delete last BBoxe", command=self.delete_last_bbox)
        self.clear_bbox_button.pack(side=tk.LEFT, padx=5)



        # Etiqueta para mostrar coordenadas
        self.bottom_frame = tk.Frame(self.master, bg="black")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.coord_label = tk.Label(self.bottom_frame, text="Coordenadas: ", fg="white", bg="black", font=("Arial", 12, "bold"))
        self.coord_label.pack(side=tk.LEFT, padx=5)
        self.coord_click = tk.Label(self.bottom_frame, text="Click: ", fg="white", bg="black", font=("Arial", 12, "bold"))
        self.coord_click.pack(side=tk.LEFT, padx=5)

        # Imagen 
        self.imagen_label = tk.Label(self.bottom_frame, text="Image", fg="white", bg="black", font=("Arial", 12, "bold"))
        self.imagen_label.pack(side=tk.LEFT, padx=5)
        
        # colores
        self.position_colors = tk.Label(self.bottom_frame, text="5-Cola", fg="#90EE90", bg="black", font=("Arial", 8, "bold"))
        self.position_colors.pack(side=tk.RIGHT, padx=0)
        self.position_colors = tk.Label(self.bottom_frame, text="4-Fin Aleta", fg="red", bg="black", font=("Arial", 8, "bold"))
        self.position_colors.pack(side=tk.RIGHT, padx=0)
        self.position_colors = tk.Label(self.bottom_frame, text="3-Inicio Aleta", fg="#FFD700", bg="black", font=("Arial", 8, "bold"))
        self.position_colors.pack(side=tk.RIGHT, padx=0)
        self.position_colors = tk.Label(self.bottom_frame, text="2-Espiraculo", fg="#00FFFF", bg="black", font=("Arial", 8, "bold"))
        self.position_colors.pack(side=tk.RIGHT, padx=0)
        self.position_colors = tk.Label(self.bottom_frame, text="1-Cabeza", fg="#FF00FF", bg="black", font=("Arial", 8, "bold"))
        self.position_colors.pack(side=tk.RIGHT, padx=0)





        # Canvas para la imagen
        self.container = tk.Frame(self.master)
        self.container.pack(side="left", fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.container, bg="black")
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)
        self.draw_dot_pattern()

        # EN PROCESO ==================================================================================================================
        # Barra de desplazamiento vertical
        self.v_scrollbar = ttk.Scrollbar(self.container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Barra de desplazamiento horizontal
        self.h_scrollbar = ttk.Scrollbar(self.bottom_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configura el canvas para que use las barras de desplazamiento
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        # ===============================================================================================================================

        # funciones del mouse
        self.canvas.bind("<Motion>", self.show_pixel_coord)
        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.canvas.bind("<ButtonPress-3>", self.on_right_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)







    # SECCION DE FUNCIONES =============================================================================================================
    # ==================================================================================================================================
    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_name_list = os.listdir(folder_path)
            self.image_list = [os.path.join(folder_path, f) for f in self.image_name_list
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            if self.image_list:
                self.current_index = 0
                self.load_image()  # Cambié aquí para usar load_image consistentemente
            else:
                tk.messagebox.showinfo("Información", "No se encontraron imágenes en la carpeta seleccionada.")

    
    def load_image(self):
        """Método unificado para cargar y mostrar imágenes"""
        if 0 <= self.current_index < len(self.image_list):
            # Limpiar canvas y resetear zoom
            self.canvas.delete("all")
            self.zoom_factor = 1.0
            self.ancho_imagen = self.ancho_base_imagen
            self.largo_imagen = self.largo_base_imagen
            
            # Actualizar etiqueta del nombre de imagen
            self.imagen_label.config(text=str(self.image_name_list[self.current_index]))
            
            # Cargar imagen
            image_path = self.image_list[self.current_index]
            self.original_image = Image.open(image_path)
            self.current_image = self.resize_image(self.original_image, self.ancho_imagen, self.largo_imagen)
            
            # Mostrar imagen en canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_image)
            self.canvas.config(scrollregion=(0, 0, self.current_image.width(), self.current_image.height()))
            
            # Actualizar título
            self.master.title(f"Visualizador de Fotos - {os.path.basename(image_path)}")
            
            # Establecer dimensiones redimensionadas
            self.resized_width = self.current_image.width()
            self.resized_height = self.current_image.height()
            
            # Dibujar patrón de puntos
            self.draw_dot_pattern()
            
            # Restaurar óvalos de la imagen actual
            self.restore_ovals_for_current_image()
            
            # Restaurar bounding boxes de la imagen actual
            self.restore_bboxes_for_current_image()

    def show_image(self, ancho, largo):
        """Método para mostrar imagen con dimensiones específicas (usado en zoom)"""
        if 0 <= self.current_index < len(self.image_list):
            image_path = self.image_list[self.current_index]

            self.imagen_label.config(text=str(self.image_name_list[self.current_index]))

            self.original_image = Image.open(image_path)
            self.current_image = self.resize_image(self.original_image, ancho, largo)
            
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_image)
            self.canvas.config(scrollregion=(0, 0, self.current_image.width(), self.current_image.height()))

            self.master.title(f"Visualizador de Fotos - {os.path.basename(image_path)}")
            self.resized_width = self.current_image.width()
            self.resized_height = self.current_image.height()
            
            # Dibujar patrón de puntos
            self.draw_dot_pattern()

    def resize_image(self, image, ancho, largo):
        image_save_proyect = image.resize(
        (ancho, largo),
        Image.Resampling.LANCZOS)
        self.resized_image = ImageTk.PhotoImage(image_save_proyect)
        return self.resized_image

    def show_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_image()  # Usar load_image en lugar de load_image con parámetros

    def show_next(self):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.load_image()  # Usar load_image en lugar de load_image con parámetros

    def toggle_mode(self):
        """Alterna entre modo puntos y modo bounding box"""
        if self.drawing_mode == "points":
            self.drawing_mode = "bbox"
            self.mode_button.config(text="Mode: BBox", bg="lightgreen")
        else:
            self.drawing_mode = "points"
            self.mode_button.config(text="Mode: Points", bg="lightblue")
        print(f"Modo actual: {self.drawing_mode}")

    def on_click(self, event):
        """Maneja los clics según el modo actual"""
        if self.drawing_mode == "points":
            self.save_pixel_coord(event)
        elif self.drawing_mode == "bbox":
            self.start_bbox(event)

    def on_right_click(self, event):
        """Maneja el clic derecho según el modo actual"""
        if self.drawing_mode == "points":
            self.delete_pixel_coord(event)
        elif self.drawing_mode == "bbox":
            self.delete_last_bbox(event)

    def on_drag(self, event):
        """Maneja el arrastre para dibujar bounding box"""
        if self.drawing_mode == "bbox" and self.bbox_start:
            self.update_bbox(event)

    def on_release(self, event):
        """Maneja la liberación del botón para finalizar bounding box"""
        if self.drawing_mode == "bbox" and self.bbox_start:
            self.finish_bbox(event)

    def start_bbox(self, event):
        """Inicia el dibujo de un bounding box"""
        if self.original_image:
            self.bbox_start = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
            
            # Crear rectángulo temporal
            if self.current_bbox:
                self.canvas.delete(self.current_bbox)
            
            self.current_bbox = self.canvas.create_rectangle(
                self.bbox_start[0], self.bbox_start[1], 
                self.bbox_start[0], self.bbox_start[1],
                outline="red", width=2, fill="", tags="temp_bbox"
            )

    def update_bbox(self, event):
        """Actualiza el bounding box mientras se arrastra"""
        if self.bbox_start and self.current_bbox:
            current_x = self.canvas.canvasx(event.x)
            current_y = self.canvas.canvasy(event.y)
            
            self.canvas.coords(
                self.current_bbox,
                self.bbox_start[0], self.bbox_start[1],
                current_x, current_y
            )

    def finish_bbox(self, event):
        """Finaliza el dibujo del bounding box y lo guarda"""
        if self.bbox_start and self.current_bbox and self.original_image:
            end_x = self.canvas.canvasx(event.x)
            end_y = self.canvas.canvasy(event.y)
            
            # Calcular coordenadas en la imagen original
            img_width, img_height = self.original_image.size
            scale_x = img_width / self.resized_width
            scale_y = img_height / self.resized_height
            
            # Convertir coordenadas del canvas a coordenadas de imagen original
            orig_x1 = int(self.bbox_start[0] * scale_x)
            orig_y1 = int(self.bbox_start[1] * scale_y)
            orig_x2 = int(end_x * scale_x)
            orig_y2 = int(end_y * scale_y)
            
            # Asegurar que las coordenadas estén en orden correcto
            min_x, max_x = min(orig_x1, orig_x2), max(orig_x1, orig_x2)
            min_y, max_y = min(orig_y1, orig_y2), max(orig_y1, orig_y2)
            
            # Asegurar que estén dentro de los límites de la imagen
            min_x = max(0, min(min_x, img_width))
            min_y = max(0, min(min_y, img_height))
            max_x = max(0, min(max_x, img_width))
            max_y = max(0, min(max_y, img_height))
            
            # Solo guardar si el bounding box tiene un tamaño mínimo
            if abs(max_x - min_x) > 10 and abs(max_y - min_y) > 10:
                # Cambiar color del rectángulo a verde (confirmado)
                self.canvas.itemconfig(self.current_bbox, outline="lime", width=1, tags="bbox")
                
                # Guardar bounding box
                current_image_name = os.path.basename(self.image_list[self.current_index])

                # Aumentar el ID del bounding box
                self.bbox_id += 1

                bbox_data = {
                    'image': current_image_name,
                    'x1': self.bbox_start[0],
                    'y1': self.bbox_start[1], 
                    'x2': end_x,
                    'y2': end_y,
                    'orig_x1': min_x,
                    'orig_y1': min_y,
                    'orig_x2': max_x,
                    'orig_y2': max_y,
                    'width': max_x - min_x,
                    'height': max_y - min_y,
                    'zoom_proportion': self.ancho_base_imagen / self.ancho_imagen,
                    'id': self.current_bbox,
                    'id_bbox': self.bbox_id
                }
                
                self.bounding_boxes.append(bbox_data)
                self.bbox_rectangles.append({
                    'id': self.current_bbox,
                    'image': current_image_name,
                    'coords': [self.bbox_start[0], self.bbox_start[1], end_x, end_y],
                    'id_bbox': self.bbox_id
                })

                # agregar text de id del bbox creado
                self.add_bbox_text()

                print(f"Bounding box guardado: ({min_x}, {min_y}) -> ({max_x}, {max_y}), Tamaño: {max_x-min_x}x{max_y-min_y}")
            else:
                # Eliminar rectángulo si es muy pequeño
                self.canvas.delete(self.current_bbox)
                print("Bounding box muy pequeño, no guardado")
            
            # Resetear variables
            self.bbox_start = None
            self.current_bbox = None

        # Cambiar modo a puntos al terminar el bbos
        if self.drawing_mode == "bbox":
            self.drawing_mode = "points"
            self.mode_button.config(text="Mode: Points", bg="lightblue")

    def add_bbox_text(self):
        self.canvas.delete("text_id_bbox")
        text_id = self.canvas.create_text(
        self.bbox_start[0] ,  
        self.bbox_start[1] - 10,
        text=str(self.bbox_id),
        anchor='nw',
        fill='white',
        font=('Arial', 6),
        tags="text_id_bbox"
        )
    
    def restore_bboxes_for_current_image(self):
        """Restaura los bounding boxes guardados para la imagen actual"""
        if hasattr(self, 'image_name_list') and self.current_index >= 0:
            current_image_name = str(self.image_name_list[self.current_index])
            for bbox in self.bounding_boxes:
                if bbox['image'] == current_image_name:
                    # Convertir coordenadas según el zoom actual
                    zoom_prop = bbox['zoom_proportion']
                    current_zoom = self.ancho_imagen / self.ancho_base_imagen
                    
                    x1 = bbox['x1'] * zoom_prop * current_zoom / zoom_prop
                    y1 = bbox['y1'] * zoom_prop * current_zoom / zoom_prop  
                    x2 = bbox['x2'] * zoom_prop * current_zoom / zoom_prop
                    y2 = bbox['y2'] * zoom_prop * current_zoom / zoom_prop
                    
                    rect_id = self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline="lime", width=1, fill="", tags="bbox"
                    )
                    self.bbox_rectangles.append({
                        'id': rect_id,
                        'image': current_image_name,
                        'coords': [x1, y1, x2, y2]
                    })

    def delete_last_bbox(self, event=None):
        """Elimina el último bounding box creado en la imagen actual"""
        if self.bounding_boxes:
            current_image_name = os.path.basename(self.image_list[self.current_index])

            # baja en uno el id del identificador
            self.bbox_id -= 1
            # choa texto de id
            self.canvas.delete("text_id_bbox")
            
            # Buscar el último bounding box de la imagen actual
            for i in range(len(self.bounding_boxes) - 1, -1, -1):
                if self.bounding_boxes[i]['image'] == current_image_name:
                    bbox_deleted = self.bounding_boxes.pop(i)
                    
                    # Eliminar del canvas
                    self.canvas.delete(bbox_deleted['id'])
                    
                    # Eliminar de la lista de rectángulos
                    self.bbox_rectangles = [rect for rect in self.bbox_rectangles 
                                          if rect['id'] != bbox_deleted['id']]
                    
                    print(f"Bounding box eliminado: {bbox_deleted['orig_x1']}, {bbox_deleted['orig_y1']} -> {bbox_deleted['orig_x2']}, {bbox_deleted['orig_y2']}")
                    
                    self.delete_ovals_by_bbox_id(target_bbox_id = self.bbox_id+1)
                    break
                    

    def delete_ovals_by_bbox_id(self, target_bbox_id):
        """Elimina todos los óvalos y coordenadas que tengan id_bbox igual a target_bbox_id"""
        current_image_name = os.path.basename(self.image_list[self.current_index])

        # Crear nuevas listas con los elementos que se conservarán
        updated_click_coordinates = []
        updated_click_ovals = []

        for coord in self.click_coordinates:
            if coord[5] == target_bbox_id and coord[0] == current_image_name:
                oval_id = coord[4]
                self.canvas.delete(oval_id)  # Borrar del canvas
                if oval_id in self.click_ovals_id:
                    self.click_ovals_id.remove(oval_id)
            else:
                updated_click_coordinates.append(coord)

        for oval in self.click_ovals:
            if not (oval['id_bbox'] == target_bbox_id and oval['image'] == current_image_name):
                updated_click_ovals.append(oval)

        # Actualizar las listas con los elementos no eliminados
        self.click_coordinates = updated_click_coordinates
        self.click_ovals = updated_click_ovals


    def restore_ovals_for_current_image(self):
        """Restaura los óvalos guardados para la imagen actual"""
        if hasattr(self, 'image_name_list') and self.current_index >= 0:
            current_image_name = str(self.image_name_list[self.current_index])
            for oval in self.click_ovals:
                if oval['image'] == current_image_name:
                    self.oval_id = self.canvas.create_oval(
                        oval['coords'][0] * oval['zoom_proportion'], 
                        oval['coords'][1] * oval['zoom_proportion'], 
                        oval['coords'][2] * oval['zoom_proportion'], 
                        oval['coords'][3] * oval['zoom_proportion'],
                        fill=oval['fill']
                    )

    def show_pixel_coord(self, event):
        if self.original_image:
            img_width, img_height = self.original_image.size

            scale_x = img_width / self.resized_width
            scale_y = img_height / self.resized_height

            x = self.canvas.canvasx(event.x) * scale_x
            y = self.canvas.canvasy(event.y) * scale_y

            x = max(0, min(x, img_width))
            y = max(0, min(y, img_height))

            x = int(round(x))
            y = int(round(y))

            self.coord_label.config(text=f"Coordenadas: X: {x}, Y: {y}")
        else:
            self.coord_label.config(text="Coordenadas: N/A")
    
    def save_pixel_coord(self, event):
        if self.bbox_id > 0:
            if self.original_image:
                position = simpledialog.askinteger("Enter a position (1 - 5)", "Position")
                if position in range(1,6):

                    self.img_width, self.img_height = self.original_image.size

                    scale_x = self.img_width / self.resized_width
                    scale_y = self.img_height / self.resized_height

                    x = self.canvas.canvasx(event.x) * scale_x
                    y = self.canvas.canvasy(event.y) * scale_y

                    x = max(0, min(x, self.img_width))
                    y = max(0, min(y, self.img_height))

                    x = int(round(x))
                    y = int(round(y))

                    self.coord_click.config(text=f"Click: X: {x}, Y: {y}")

                    colors = {
                        1: "#FF00FF",
                        2: "#00FFFF",
                        3: "#FFD700",
                        4: "red",
                        5: "#90EE90"
                    }

                    # agregar ovalo
                    self.oval_id = self.canvas.create_oval(self.canvas.canvasx(event.x)-self.tamano_oval, 
                                                        self.canvas.canvasy(event.y)-self.tamano_oval, 
                                                        self.canvas.canvasx(event.x)+self.tamano_oval, 
                                                        self.canvas.canvasy(event.y)+self.tamano_oval, 
                                        fill=colors[position])
                    
                    # agregar texto al ultimo ovalo de id de bbox
                    self.add_point_text(x = self.canvas.canvasx(event.x), y = self.canvas.canvasx(event.y))

                    self.click_ovals.append({'image': os.path.basename(self.image_list[self.current_index]), 
                            'id': self.oval_id,
                            'coords': self.canvas.coords(self.oval_id),
                            'fill': colors[position],
                            'zoom_proportion': self.ancho_base_imagen/self.ancho_imagen,
                            'id_bbox': self.bbox_id})
                    
                    self.click_ovals_id.append(self.oval_id)

                    self.click_coordinates.append([os.path.basename(self.image_list[self.current_index]), position, int(x), int(y), self.oval_id, self.bbox_id])

                    print(f"Posicion {position} guardada en: {x}, {y}")
                else:
                    self.coord_click.config(text="Click: N/A")

    def add_point_text(self, x, y):
        self.canvas.delete("text_id_bbox_point")
        text_id = self.canvas.create_text(
        x + 5,  
        y + 5,
        text=str(self.bbox_id),
        anchor='nw',
        fill='white',
        font=('Arial', 6),
        tags="text_id_bbox_point"
        )
    
    def delete_pixel_coord(self, event):
        if self.click_coordinates:
            coordenate_deleted = self.click_coordinates.pop()

            # Buscar y eliminar el óvalo correspondiente
            current_image_name = os.path.basename(self.image_list[self.current_index])
            for i, oval in enumerate(self.click_ovals):
                if (oval['image'] == current_image_name and 
                    oval['id'] == coordenate_deleted[4]):
                    self.canvas.delete(oval['id'])
                    self.click_ovals.pop(i)
                    break
            
            # También eliminar de la lista de IDs
            if coordenate_deleted[4] in self.click_ovals_id:
                self.click_ovals_id.remove(coordenate_deleted[4])

            print(f"Last position deleted: {coordenate_deleted[2:4]}")
        else:
            print("There is no more positions to delete")



    def save_coordinates(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")])
        if filename:
            self.save_coordinates_to_csv(filename)

    def save_coordinates_to_csv(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Escribir headers
            csv_writer.writerow(['Imagen', 'Type', 'Position', 'X', 'Y', 'X2', 'Y2', 'id_geo', 'id_bbox'])
            
            # Escribir coordenadas de puntos
            for coord in self.click_coordinates:
                csv_writer.writerow([coord[0], 'point', coord[1], coord[2], coord[3], '', '', coord[4], coord[5]])
            
            # Escribir bounding boxes
            for bbox in self.bounding_boxes:
                csv_writer.writerow([
                    bbox['image'], 'bbox', '', 
                    bbox['orig_x1'], bbox['orig_y1'], 
                    bbox['orig_x2'], bbox['orig_y2'],
                    bbox['id'],
                    bbox['id_bbox']
                ])
        
        print(f"Datos guardados en {filename}")
        print(f"Puntos guardados: {len(self.click_coordinates)}")
        print(f"Bounding boxes guardados: {len(self.bounding_boxes)}")
        


    def oval_size_changer(self):
        oval_size = simpledialog.askinteger(f"Current {self.tamano_oval}", f"Oval size (Current {self.tamano_oval}):")
        if isinstance(oval_size, int):
            self.tamano_oval = oval_size
        else:
            print('Oval size must be a integer')


    
    def zoom_in(self):
        self.zoom_factor += self.ZOOM_STEP
        self.ancho_imagen = int(self.ancho_base_imagen * self.zoom_factor)
        self.largo_imagen = int(self.largo_base_imagen * self.zoom_factor)

        self.proportion = self.zoom_factor

        self.canvas.delete("all")
        self.show_image(self.ancho_imagen, self.largo_imagen)
        self.restore_bboxes_for_current_image()

        for oval in self.click_ovals:
            if oval['image'] == str(self.image_name_list[self.current_index]):
                self.oval_id = self.canvas.create_oval(oval['coords'][0]*oval['zoom_proportion']*self.proportion, 
                                        oval['coords'][1]*oval['zoom_proportion']*self.proportion, 
                                        oval['coords'][2]*oval['zoom_proportion']*self.proportion, 
                                        oval['coords'][3]*oval['zoom_proportion']*self.proportion,
                                        fill=oval['fill'])

    
    def zoom_out(self):
        self.zoom_factor -= self.ZOOM_STEP
        self.ancho_imagen = int(self.ancho_base_imagen * self.zoom_factor)
        self.largo_imagen = int(self.largo_base_imagen * self.zoom_factor)

        self.proportion = self.zoom_factor

        self.canvas.delete("all")

        self.show_image(self.ancho_imagen, self.largo_imagen)
        self.restore_bboxes_for_current_image()

        for oval in self.click_ovals:
            if oval['image'] == str(self.image_name_list[self.current_index]):
                self.oval_id = self.canvas.create_oval(oval['coords'][0]*oval['zoom_proportion']*self.proportion, 
                                        oval['coords'][1]*oval['zoom_proportion']*self.proportion, 
                                        oval['coords'][2]*oval['zoom_proportion']*self.proportion, 
                                        oval['coords'][3]*oval['zoom_proportion']*self.proportion,
                                        fill=oval['fill'])
        
    def Restore(self, zoom = 1, move = True):
        self.zoom_factor = zoom
        self.ancho_imagen = self.ancho_base_imagen
        self.largo_imagen = self.largo_base_imagen
        self.proportion = 1.0
        self.canvas.delete("all")
        self.show_image(self.ancho_imagen, self.largo_imagen)
        
        if move:
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)

        self.restore_bboxes_for_current_image()

        for oval in self.click_ovals:
            if oval['image'] == str(self.image_name_list[self.current_index]):
                self.oval_id = self.canvas.create_oval(oval['coords'][0]*oval['zoom_proportion'], 
                                        oval['coords'][1]*oval['zoom_proportion'], 
                                        oval['coords'][2]*oval['zoom_proportion'], 
                                        oval['coords'][3]*oval['zoom_proportion'],
                                        fill=oval['fill'])


    
    def draw_dot_pattern(self):
        """Dibuja un patrón de puntos en el canvas."""
        dot_spacing = 100  # Espacio entre los puntos
        dot_size = .5  # Tamaño de los puntos (diámetro)
        for x in range(dot_spacing-2, 2000-2, dot_spacing):  # Recorrer el ancho del canvas
            for y in range(dot_spacing-2, 2000-2, dot_spacing):  # Recorrer el alto del canvas
                self.canvas.create_oval(x - dot_size, y - dot_size, x + dot_size, y + dot_size, fill="lightgray", outline="")




# Correr la app
if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoViewer(root)
    root.mainloop()