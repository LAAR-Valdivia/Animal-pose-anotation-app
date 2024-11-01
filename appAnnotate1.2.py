
# Autor: Joseba Iribarren L.
# Función: Facilitar la identificación de partes de animales

import tkinter as tk
import os
import csv
import shutil
from pathlib import Path
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
        self.folder_path = None
        items = None

        self.zoom_factor = 1


       
        

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
        


        self.oval_size = tk.Button(self.button_frame, text="Oval size", command=self.oval_size_changer)
        self.oval_size.pack(side=tk.LEFT, padx=5)

        self.restore_button = tk.Button(self.button_frame, text="Restore", command=self.Restore)
        self.restore_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(self.button_frame, text="Save", command=self.save_coordinates, bg='pink')
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.zoom_scale = tk.Scale(self.button_frame, from_=1.0, to=5.0, resolution=0.25, orient="horizontal", command=self.update_zoom)
        self.zoom_scale.set(1.0)
        self.zoom_scale.pack(side=tk.LEFT, padx=5)

        




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

        # Vincular la rueda del mouse a la función de zoom
        self.canvas.bind("<MouseWheel>", self.mouse_wheel)


        # Barra de desplazamiento vertical
        self.v_scrollbar = ttk.Scrollbar(self.container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Barra de desplazamiento horizontal
        self.h_scrollbar = ttk.Scrollbar(self.bottom_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configura el canvas para que use las barras de desplazamiento
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # funciones del mouse
        self.canvas.bind("<Motion>", self.show_pixel_coord)
        self.canvas.bind("<ButtonPress-1>", lambda event: self.save_pixel_coord(event))
        self.canvas.bind("<ButtonPress-2>", lambda event: self.mouse_on_canvas(event))
        self.canvas.bind("<ButtonPress-3>", lambda event: self.delete_pixel_coord(event))

















    # SECCION DE FUNCIONES =============================================================================================================
    # ==================================================================================================================================
    def open_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.image_name_list = os.listdir(self.folder_path)
            self.image_list = [os.path.join(self.folder_path, f) for f in self.image_name_list
                            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            if self.image_list:
                self.current_index = 0
                self.show_image(self.ancho_base_imagen, self.largo_base_imagen)
            else:
                tk.messagebox.showinfo("Información", "No se encontraron imágenes en la carpeta seleccionada.")

    
    def show_image(self, ancho, largo):
        if 0 <= self.current_index < len(self.image_list):
            image_path = self.image_list[self.current_index]

            self.imagen_label.config(text=str(self.image_name_list[self.current_index]))

            self.original_image = Image.open(image_path)
            self.current_image = self.resize_image(self.original_image, ancho, largo)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_image)
            self.master.title(f"Visualizador de Fotos - {os.path.basename(image_path)}")
            self.resized_width = self.resized_image.width()
            self.resized_height = self.resized_image.height()

    def resize_image(self, image, ancho, largo):
        image_save_proyect = image.resize(
        (ancho, largo),
        Image.Resampling.LANCZOS)
        self.resized_image = ImageTk.PhotoImage(image_save_proyect)
        return self.resized_image

    def show_previous(self):
        if self.current_index > 0:
            self.canvas.delete("all")
            self.current_index -= 1
            self.Restore()

    def show_next(self):
        if self.current_index < len(self.image_list) - 1:
            self.canvas.delete("all")
            self.current_index += 1
            self.Restore()

    def load_image(self, ancho, largo):
        self.imagen_label.config(text=str(self.image_name_list[self.current_index]))

        if self.current_image:
            self.current_image = None
            self.original_image = None

        image_path = self.image_list[self.current_index]
        self.original_image = Image.open(image_path)
        self.current_image = self.resize_image(self.original_image, ancho, largo)
        self.canvas.config(width=self.current_image.width(), height=self.current_image.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.current_image)
        self.master.title(f"Visualizador de Fotos - {os.path.basename(image_path)}")






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

                self.oval_id = self.canvas.create_oval(self.canvas.canvasx(event.x)-self.tamano_oval, 
                                                       self.canvas.canvasy(event.y)-self.tamano_oval, 
                                                       self.canvas.canvasx(event.x)+self.tamano_oval, 
                                                       self.canvas.canvasy(event.y)+self.tamano_oval, 
                                       fill=colors[position])
                self.click_ovals.append({'image': os.path.basename(self.image_list[self.current_index]), 
                         'id': self.oval_id,
                         'coords': self.canvas.coords(self.oval_id),
                         'fill': colors[position],
                         'zoom_proportion': self.ancho_base_imagen/self.ancho_imagen})
                
                self.click_ovals_id.append(self.oval_id)

                self.click_coordinates.append([os.path.basename(self.image_list[self.current_index]), position, int(x), int(y), self.oval_id])

                print(f"Posicion {position} guardada en: {x}, {y}")
            else:
                self.coord_click.config(text="Click: N/A")
    
    def delete_pixel_coord(self, event):
        if self.click_coordinates:
            coordenate_deleted = self.click_coordinates.pop()

            ultimo_ovalo = self.click_ovals.pop()
            self.canvas.delete(ultimo_ovalo)

            ultimo_ovalo_id = self.click_ovals_id.pop()
            self.canvas.delete(ultimo_ovalo_id)

            print(f"Last position deleted: {coordenate_deleted[2:4]}")

            self.update()
        else:
            print("There is no more positions to delete")



    def save_coordinates(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV files", "*.csv")])
        if filename:
            self.save_coordinates_to_csv(filename)


    def save_coordinates_to_csv(self, filename):
        try:
            with open(filename, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['Imagen', 'Position', 'X', 'Y', 'point_id'])
                
                for coord in self.click_coordinates:
                    csv_writer.writerow(coord)

            revised_folder = os.path.join(self.folder_path, 'revised')
            if not os.path.exists(revised_folder):
                os.makedirs(revised_folder) 
            
            lista_imagenes = [elemento[0] for elemento in self.click_coordinates]
            print(lista_imagenes)

            for ruta_imagen in lista_imagenes:
                archivo = Path(self.folder_path + '/' + ruta_imagen)
                
                # Verificar si el archivo existe antes de moverlo
                if archivo.exists() and archivo.is_file():
                    shutil.move(str(archivo), str(revised_folder + '\\' + archivo.name))
                    print(f'Movido: {archivo.name} a {revised_folder}')
                else:
                    print(f'El archivo {archivo} no existe o no es un archivo válido.')
        except Exception as e:
            print(f'Ocurrió un error: {e}')


        


    def oval_size_changer(self):
        oval_size = simpledialog.askinteger(f"Current {self.tamano_oval}", f"Oval size (Current {self.tamano_oval}):")
        if isinstance(oval_size, int):
            self.tamano_oval = oval_size
        else:
            print('Oval size must be a integer')



    def mouse_wheel(self, event):
        # Determinar el cambio en el zoom
        if event.delta > 10:
            self.zoom_scale.set(min(self.zoom_scale.get() + 0.5, 5.0))  # Aumentar zoom
        else:
            self.zoom_scale.set(max(self.zoom_scale.get() - 0.5, 1))  # Disminuir zoom

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # Obtener las dimensiones del canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Comprobar si el mouse está dentro del canvas
        if 0 <= x <= canvas_width and 0 <= y <= canvas_height:
            print(f"El mouse está dentro del canvas en ({x}, {y})")

            self.update_zoom(self.zoom_scale.get(), x, y)
    

 
    def update_zoom(self, value, x = None , y = None):
        self.zoom_factor = float(value)

        self.ancho_imagen  = int(round(self.ancho_base_imagen * self.zoom_factor))
        self.largo_imagen  = int(round(self.largo_base_imagen * self.zoom_factor))

        self.proportion = self.ancho_imagen/self.ancho_base_imagen

        self.canvas.delete("all")
        self.show_image(self.ancho_imagen, self.largo_imagen)

        if x  is not None and y is not None:
            self.canvas.xview_moveto(x)
            self.canvas.yview_moveto(y)

    def mouse_on_canvas(self, event):
        # Obtener las coordenadas del mouse
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # Obtener las dimensiones del canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Comprobar si el mouse está dentro del canvas
        if 0 <= x <= canvas_width and 0 <= y <= canvas_height:
            print(f"El mouse está dentro del canvas en ({x}, {y})")
        else:
            print(f"El mouse está fuera del canvas en ({x}, {y})")








        for oval in self.click_ovals:
                if oval['image'] == str(self.image_name_list[self.current_index]):
                    self.oval_id = self.canvas.create_oval(oval['coords'][0]*oval['zoom_proportion']*self.proportion, 
                                            oval['coords'][1]*oval['zoom_proportion']*self.proportion, 
                                            oval['coords'][2]*oval['zoom_proportion']*self.proportion, 
                                            oval['coords'][3]*oval['zoom_proportion']*self.proportion,
                                            fill=oval['fill'])
        


        # Calcular la posición del canvas en relación al mouse
        current_x_view = self.canvas.xview()[0] * self.canvas.winfo_width()
        current_y_view = self.canvas.yview()[0] * self.canvas.winfo_height()

        # Calcular el nuevo desplazamiento
        new_x_view = (self.mouse_x + current_x_view) / 2
        new_y_view = (self.mouse_y + current_y_view) / 2

        # Mover el canvas centrando en el mouse
        self.canvas.xview_moveto(new_x_view / self.canvas.winfo_reqwidth())
        self.canvas.yview_moveto(new_y_view / self.canvas.winfo_reqheight())


    
    def Restore(self):
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.zoom_scale.set(1.0)
        self.update_zoom(1.0)



    def update(self):
        self.ancho_imagen  = int(round(self.ancho_imagen))
        self.largo_imagen  = int(round(self.largo_imagen))

        self.proportion = self.ancho_imagen/self.ancho_base_imagen

        self.canvas.delete("all")
        self.show_image(self.ancho_imagen, self.largo_imagen)

        for oval in self.click_ovals:
            if oval['image'] == str(self.image_name_list[self.current_index]):
                self.oval_id = self.canvas.create_oval(oval['coords'][0]*oval['zoom_proportion']*self.proportion, 
                                        oval['coords'][1]*oval['zoom_proportion']*self.proportion, 
                                        oval['coords'][2]*oval['zoom_proportion']*self.proportion, 
                                        oval['coords'][3]*oval['zoom_proportion']*self.proportion,
                                        fill=oval['fill'])



    
    def draw_dot_pattern(self):
        dot_spacing = 100  
        dot_size = .5 
        for x in range(dot_spacing-2, 2000-2, dot_spacing):  
            for y in range(dot_spacing-2, 2000-2, dot_spacing): 
                self.canvas.create_oval(x - dot_size, y - dot_size, x + dot_size, y + dot_size, fill="lightgray", outline="")




# Correr la app
if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoViewer(root)
    root.mainloop()


# import readline
# readline.clear_history()
