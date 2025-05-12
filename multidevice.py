import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog

class ChatMulticast:
    def __init__(self):
        # Configuración multicast
        self.MULTICAST_GROUP = '224.1.1.1'  # Grupo estándar para multicast
        self.PORT = 5007
        
        # Pedir nombre de usuario
        self.usuario = simpledialog.askstring("Nombre", "¿Cómo te llamas?") or "Anónimo"
        
        # Configurar interfaz
        self.setup_ui()
        
        # Configurar red
        self.setup_network()
        
        # Iniciar hilo de recepción
        threading.Thread(target=self.recibir_mensajes, daemon=True).start()
    
    def setup_ui(self):
        """Crea la interfaz gráfica del chat"""
        self.root = tk.Tk()
        self.root.title(f"Chat - {self.usuario}")
        
        # Área de mensajes
        self.area_mensajes = scrolledtext.ScrolledText(self.root, state='disabled')
        self.area_mensajes.pack(padx=10, pady=10)
        
        # Frame para entrada y botón
        frame_entrada = tk.Frame(self.root)
        frame_entrada.pack(padx=10, pady=10)
        
        self.entrada = tk.Entry(frame_entrada, width=40)
        self.entrada.pack(side=tk.LEFT)
        self.entrada.bind("<Return>", lambda e: self.enviar_mensaje())
        
        tk.Button(frame_entrada, text="Enviar", command=self.enviar_mensaje).pack(side=tk.LEFT)
        
        # Manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_chat)
    
    def setup_network(self):
        """Configura la conexión de red multicast"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.PORT))
        
        # Unirse al grupo multicast
        grupo = socket.inet_aton(self.MULTICAST_GROUP)
        mreq = grupo + socket.inet_aton('0.0.0.0')
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    def recibir_mensajes(self):
        """Escucha constantemente mensajes entrantes"""
        while True:
            try:
                datos, direccion = self.sock.recvfrom(1024)
                mensaje = datos.decode('utf-8')
                self.mostrar_mensaje(mensaje)
            except:
                break
    
    def enviar_mensaje(self):
        """Envía un mensaje al grupo multicast"""
        texto = self.entrada.get()
        if texto:
            mensaje_completo = f"{self.usuario}: {texto}"
            self.sock.sendto(mensaje_completo.encode('utf-8'), (self.MULTICAST_GROUP, self.PORT))
            self.entrada.delete(0, tk.END)
    
    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje en el área de chat"""
        self.area_mensajes.config(state='normal')
        self.area_mensajes.insert(tk.END, mensaje + "\n")
        self.area_mensajes.config(state='disabled')
        self.area_mensajes.see(tk.END)
    
    def cerrar_chat(self):
        """Cierra la conexión correctamente"""
        self.sock.close()
        self.root.destroy()
    
    def iniciar(self):
        """Inicia la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    chat = ChatMulticast()
    chat.iniciar()