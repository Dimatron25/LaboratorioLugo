import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import database
import pdf_generator
import backup
from datetime import datetime

conn = database.conectar()
cursor = conn.cursor()

root = tk.Tk()
root.title("Laboratorio Lugo - México")
root.geometry("900x600")
root.configure(bg="#f0f0f0")

def registrar_paciente():
    def guardar():
        nombre = entry_nombre.get()
        curp = entry_curp.get()
        edad = entry_edad.get()
        tel = entry_tel.get()
        direc = entry_direc.get()
        if not nombre or not curp:
            messagebox.showwarning("Advertencia", "Nombre y CURP son obligatorios")
            return
        try:
            cursor.execute("INSERT INTO pacientes (nombre, curp, edad, telefono, direccion) VALUES (?, ?, ?, ?, ?)",
                           (nombre, curp, edad, tel, direc))
            conn.commit()
            messagebox.showinfo("Éxito", "Paciente registrado correctamente")
            ventana_pac.destroy()
            cargar_pacientes()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "CURP ya registrado")

    ventana_pac = tk.Toplevel(root)
    ventana_pac.title("Nuevo Paciente")
    ventana_pac.geometry("400x300")

    tk.Label(ventana_pac, text="Nombre Completo:").pack(pady=5)
    entry_nombre = tk.Entry(ventana_pac, width=30)
    entry_nombre.pack()

    tk.Label(ventana_pac, text="CURP:").pack(pady=5)
    entry_curp = tk.Entry(ventana_pac, width=30)
    entry_curp.pack()

    tk.Label(ventana_pac, text="Edad:").pack(pady=5)
    entry_edad = tk.Entry(ventana_pac, width=30)
    entry_edad.pack()

    tk.Label(ventana_pac, text="Teléfono:").pack(pady=5)
    entry_tel = tk.Entry(ventana_pac, width=30)
    entry_tel.pack()

    tk.Label(ventana_pac, text="Dirección:").pack(pady=5)
    entry_direc = tk.Entry(ventana_pac, width=30)
    entry_direc.pack()

    tk.Button(ventana_pac, text="Guardar", command=guardar, bg="green", fg="white").pack(pady=20)

def cargar_pacientes():
    for row in tree_pac.get_children():
        tree_pac.delete(row)
    cursor.execute("SELECT id, nombre, curp, edad, telefono FROM pacientes")
    for row in cursor.fetchall():
        tree_pac.insert("", "end", values=row)

def nuevo_examen():
    selected = tree_pac.selection()
    if not selected:
        messagebox.showwarning("Advertencia", "Seleccione un paciente")
        return
    paciente_id = tree_pac.item(selected[0])['values'][0]

    tipo = simpledialog.askstring("Examen", "Tipo de examen:")
    if not tipo: return
    precio = simpledialog.askfloat("Precio", "Precio (MXN):")
    if not precio: return

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    cursor.execute("INSERT INTO examenes (paciente_id, tipo, fecha, precio, estado_pago) VALUES (?, ?, ?, ?, ?)",
                   (paciente_id, tipo, fecha, precio, "pendiente"))
    conn.commit()
    messagebox.showinfo("Éxito", "Examen registrado")
    cargar_examenes()

def cargar_examenes():
    for row in tree_exam.get_children():
        tree_exam.delete(row)
    cursor.execute('''
        SELECT e.id, p.nombre, e.tipo, e.fecha, e.precio, e.estado_pago
        FROM examenes e
        JOIN pacientes p ON e.paciente_id = p.id
        ORDER BY e.fecha DESC
    ''')
    for row in cursor.fetchall():
        tree_exam.insert("", "end", values=row)

def registrar_pago():
    selected = tree_exam.selection()
    if not selected:
        messagebox.showwarning("Advertencia", "Seleccione un examen")
        return
    examen_id = tree_exam.item(selected[0])['values'][0]
    cursor.execute("SELECT precio, pagado, estado_pago, paciente_id FROM examenes WHERE id = ?", (examen_id,))
    precio, pagado, estado, paciente_id = cursor.fetchone()
    restante = precio - pagado

    monto = simpledialog.askfloat("Pago", f"Falta por pagar: $ {restante:.2f} MXN\nIngrese monto:")
    if not monto or monto <= 0: return

    nuevo_pagado = pagado + monto
    nuevo_estado = "pagado" if nuevo_pagado >= precio else "parcial"

    cursor.execute("UPDATE examenes SET pagado = ?, estado_pago = ? WHERE id = ?", (nuevo_pagado, nuevo_estado, examen_id))
    conn.commit()

    cursor.execute("SELECT * FROM examenes WHERE id = ?", (examen_id,))
    examen = cursor.fetchone()
    cursor.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
    paciente = cursor.fetchone()

    examen_dict = {
        'id': examen[0], 'paciente_id': examen[1], 'tipo': examen[2],
        'fecha': examen[3], 'precio': examen[5], 'pagado': examen[6], 'estado_pago': examen[7]
    }
    paciente_dict = {
        'nombre': paciente[1], 'curp': paciente[2], 'telefono': paciente[4]
    }

    pdf_path = pdf_generator.generar_recibo(examen_dict, paciente_dict)
    messagebox.showinfo("Pago", f"Pago registrado. Recibo guardado en:\n{pdf_path}")

def hacer_copia():
    backup.hacer_backup()
    messagebox.showinfo("Backup", "Copia de seguridad creada")

tk.Label(root, text="LABORATORIO LUGO - MÉXICO", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

frame_botones = tk.Frame(root, bg="#f0f0f0")
frame_botones.pack(pady=10)
tk.Button(frame_botones, text="Nuevo Paciente", command=registrar_paciente, width=15, bg="blue", fg="white").grid(row=0, column=0, padx=5)
tk.Button(frame_botones, text="Nuevo Examen", command=nuevo_examen, width=15, bg="orange", fg="white").grid(row=0, column=1, padx=5)
tk.Button(frame_botones, text="Registrar Pago", command=registrar_pago, width=15, bg="green", fg="white").grid(row=0, column=2, padx=5)
tk.Button(frame_botones, text="Backup", command=hacer_copia, width=15, bg="gray", fg="white").grid(row=0, column=3, padx=5)

tk.Label(root, text="Pacientes Registrados", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)
columns_pac = ("ID", "Nombre", "CURP", "Edad", "Teléfono")
tree_pac = ttk.Treeview(root, columns=columns_pac, show="headings", height=8)
for col in columns_pac:
    tree_pac.heading(col, text=col)
    tree_pac.column(col, width=120)
tree_pac.pack(pady=5, fill="x", padx=20)

tk.Label(root, text="Exámenes Realizados", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)
columns_exam = ("ID", "Paciente", "Examen", "Fecha", "Precio (MXN)", "Estado")
tree_exam = ttk.Treeview(root, columns=columns_exam, show="headings", height=10)
for col in columns_exam:
    tree_exam.heading(col, text=col)
    tree_exam.column(col, width=120)
tree_exam.pack(pady=5, fill="x", padx=20)

cargar_pacientes()
cargar_examenes()

root.mainloop()