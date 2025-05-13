import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import paramiko
import os
import sys
import ctypes





class SSHApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SSH Local File Manager")
        self.sftp = None
        self.transport = None


        status_frame = tk.Frame(root)
        status_frame.pack(pady=5)
        self.status_dot = tk.Canvas(status_frame, width=20, height=20, highlightthickness=0)
        self.status_dot.create_oval(5, 5, 15, 15, fill='red', tags="dot")
        self.status_dot.pack(side=tk.LEFT)
        self.status_label = tk.Label(status_frame, text="Disconnected", fg="red")
        self.status_label.pack(side=tk.LEFT)
        self.set_status("Disconnected", "red")

        #Login
        self.host_entry = self._add_labeled_entry("Host:", "127.0.0.1")
        self.port_entry = self._add_labeled_entry("Port:", "22")
        self.user_entry = self._add_labeled_entry("Username:", "")
        self.pass_entry = self._add_labeled_entry("Password:", "", show="*")

        #Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Connect", command=self.connect).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="List Files", command=self.list_files).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Upload", command=self.upload_file).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Download", command=self.download_file).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Disconnect", command=self.disconnect).pack(side=tk.LEFT, padx=5)

        #File List
        self.remote_listbox = tk.Listbox(root, width=50, height=10)
        self.remote_listbox.pack(padx=10, pady=5)

    def _add_labeled_entry(self, label, default, show=None):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=2, anchor="w")
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        entry = tk.Entry(frame, show=show)
        entry.insert(0, default)
        entry.pack(side=tk.LEFT)
        return entry
    def set_app_id(name="ssh.gui"):
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(name)
        except Exception as e:
            print("Unable to set AppUserModelID:", e)


    def connect(self):
        try:
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            username = self.user_entry.get()
            password = self.pass_entry.get()
            self.transport = paramiko.Transport((host, port))
            self.transport.connect(username=username, password=password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            messagebox.showinfo("Success", "Connected to SSH server.")
            self.set_status("Connected", "green")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            

    def list_files(self):
        if not self.sftp:
            messagebox.showwarning("Warning", "Not connected.")
            return
        try:
            self.remote_listbox.delete(0, tk.END)
            for f in self.sftp.listdir():
                self.remote_listbox.insert(tk.END, f)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def upload_file(self):
        if not self.sftp:
            messagebox.showwarning("Warning", "Not connected.")
            return
        local_paths = filedialog.askopenfilenames()  # allow multiple file selection
        if local_paths:
            try:
                for local_path in local_paths:
                    filename = os.path.basename(local_path)
                    self.sftp.put(local_path, filename)
                messagebox.showinfo("Upload", f"Uploaded {len(local_paths)} file(s).")
                self.list_files()
            except Exception as e:
                messagebox.showerror("Upload Error", str(e))

    def download_file(self):
        if not self.sftp:
            messagebox.showwarning("Warning", "Not connected.")
            return
        selection = self.remote_listbox.curselection()
        if not selection:
            messagebox.showinfo("Download", "Select a file first.")
            return
        remote_file = self.remote_listbox.get(selection[0])
        local_path = filedialog.asksaveasfilename(initialfile=remote_file)
        if local_path:
            try:
                self.sftp.get(remote_file, local_path)
                messagebox.showinfo("Download", f"Downloaded to {local_path}")
            except Exception as e:
                messagebox.showerror("Download Error", str(e))

    def disconnect(self):
        try:
            if self.sftp:
                self.sftp.close()
            if self.transport:
                self.transport.close()
            messagebox.showinfo("Disconnected", "SSH session closed.")
            self.set_status("Disconnected", "red")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def set_status(self, text, color):
        self.status_label.config(text=text, fg=color)
        self.status_dot.itemconfig("dot", fill=color)
if __name__ == "__main__":
    root = tk.Tk()
    app = SSHApp(root)
    root.mainloop()
