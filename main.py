import argparse
import datetime
import hashlib
import os
import sys
import logging
import threading
from tkinter import Tk, Label, Entry, Button, Checkbutton, BooleanVar, filedialog, messagebox, Text, Scrollbar, VERTICAL, END, Listbox, MULTIPLE
from tkinter import ttk  # Modern widgets

# Global options
args = None

class MD5ChecksumApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MD5 Checksum Calculator")

        self.basedir_entries = []
        self.subdirs_listboxes = []
        self.file_count_labels = []
        self.progress_labels = []

        self.create_widgets()

    def create_widgets(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(25, weight=1)

        self.add_base_directory()

        self.add_button = Button(self.root, text="Add Another Base Directory", command=self.add_base_directory)
        self.add_button.grid(row=1, column=3, padx=10, pady=5)

        self.debug_var = BooleanVar()
        Checkbutton(self.root, text="Debug", variable=self.debug_var).grid(row=2, column=3, sticky='w', padx=10, pady=5)

        self.recalculate_var = BooleanVar()
        Checkbutton(self.root, text="Recalculate", variable=self.recalculate_var).grid(row=3, column=3, sticky='w', padx=10, pady=5)

        Button(self.root, text="Start", command=self.start_process).grid(row=4, column=3, pady=10, padx=10)

        self.log_text = Text(self.root, wrap='word', height=20, width=50)
        self.log_text.grid(row=5, column=3, rowspan=10, padx=10, pady=10, sticky='nsew')

        scrollbar = Scrollbar(self.root, command=self.log_text.yview, orient=VERTICAL)
        scrollbar.grid(row=5, column=4, rowspan=10, sticky='ns')
        self.log_text['yscrollcommand'] = scrollbar.set

    def calc_hash_md5(self, file_path):
        md5 = hashlib.md5()
        logging.debug(f"Calculating hash for file {file_path}")
        start = datetime.datetime.now()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b''):
                    md5.update(chunk)
        except Exception as e:
            logging.warning(f"Failed to calculate hash for {file_path} with error {str(e)}")
            return None, None
        end = datetime.datetime.now()
        processing_time = (end - start).total_seconds()
        logging.debug(f"Calculating hash took {processing_time} seconds")
        return md5.hexdigest(), processing_time

    def process_file(self, file_path, recalculate):
        if file_path.endswith(".md5"):
            return None

        full_path_md5_file = f"{file_path}.md5"
        if os.path.exists(full_path_md5_file) and not recalculate:
            return None

        md5_hash, processing_time = self.calc_hash_md5(file_path)
        if md5_hash is None:
            return None

        with open(full_path_md5_file, 'w', encoding='utf-8') as f:
            f.write(f"{md5_hash} {os.path.basename(file_path)}\n")

        return file_path, processing_time

    def walk_tree(self, basedir, recalculate=False, progress_label=None, log_text_widget=None, total_files=None, progress_count=None):
        files_to_process = []

        for root, _, files in os.walk(basedir, topdown=False):
            for file_ in files:
                full_path = os.path.join(root, file_)
                files_to_process.append(full_path)

        results = []
        for idx, file_ in enumerate(files_to_process):
            result = self.process_file(file_, recalculate)
            if result:
                results.append(result)
            if total_files and progress_count is not None:
                progress_count[0] += 1
                progress_percentage = min((progress_count[0] / total_files[0]) * 100, 100)
                progress_label.config(text=f"Progress: {progress_percentage:.2f}%")
            if log_text_widget:
                log_text_widget.update_idletasks()

        return results

    def start_process(self):
        base_dirs = [e.get() for e in self.basedir_entries if e.get()]
        subdirs = [[l.get(i) for i in l.curselection()] if l.curselection() else None for l in self.subdirs_listboxes]
        debug = self.debug_var.get()
        recalculate = self.recalculate_var.get()

        def run():
            log_filename = "md5_log.txt"
            logging.basicConfig(
                handlers=[
                    logging.FileHandler(log_filename, 'w', 'utf-8'),
                    TextHandler(self.log_text),
                    logging.StreamHandler(sys.stdout)
                ],
                level=logging.DEBUG if debug else logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )

            all_results = []
            total_files_list = []
            progress_counts = []

            for basedir, subdir_list in zip(base_dirs, subdirs):
                total_files = 0
                for root, _, files in os.walk(basedir):
                    total_files += len(files)
                if subdir_list:
                    for subdir in subdir_list:
                        subdir_path = os.path.join(basedir, subdir)
                        for root, _, files in os.walk(subdir_path):
                            total_files += len(files)
                total_files_list.append(total_files)
                progress_counts.append(0)

            for i, basedir in enumerate(base_dirs):
                file_count = 0
                for root, _, files in os.walk(basedir):
                    file_count += len(files)
                subdir_list = subdirs[i]
                if subdir_list:
                    for subdir in subdir_list:
                        subdir_path = os.path.join(basedir, subdir)
                        for root, _, files in os.walk(subdir_path):
                            file_count += len(files)
                self.file_count_labels[i].config(text=f"Files: {file_count}")

            for i, (basedir, subdir_list) in enumerate(zip(base_dirs, subdirs)):
                logging.info(f"Calculating hashes for all files under {basedir}")
                all_results.extend(self.walk_tree(basedir, recalculate, self.progress_labels[i], self.log_text, [total_files_list[i]], [progress_counts[i]]))
                if not subdir_list:
                    subdir_list = next(os.walk(basedir))[1]
                for subdir in subdir_list:
                    subdir_path = os.path.join(basedir, subdir)
                    logging.info(f"Calculating hashes for all files under {subdir_path}")
                    subdir_results = self.walk_tree(subdir_path, recalculate, self.progress_labels[i], self.log_text, [total_files_list[i]], [progress_counts[i]])
                    all_results.extend(subdir_results)

            with open(log_filename, 'a', encoding='utf-8') as f:
                f.write("\nProcessing Summary:\n")
                for file_path, processing_time in all_results:
                    f.write(f"{file_path}: {processing_time} seconds\n")

            messagebox.showinfo("Complete", "MD5 calculation is complete.")
            for progress_label in self.progress_labels:
                progress_label.config(text="Progress: 100.00%")

        threading.Thread(target=run).start()

    def browse_directory(self, entry, subdirs_listbox, add_button):
        dirname = filedialog.askdirectory()
        if dirname:
            entry.delete(0, "end")
            entry.insert(0, dirname)
            subdirs_listbox.delete(0, END)
            subdirs = next(os.walk(dirname))[1]
            if subdirs:
                for subdir in subdirs:
                    subdirs_listbox.insert(END, subdir)
                subdirs_listbox.grid()
                add_button.grid()
            else:
                subdirs_listbox.grid_remove()

    def add_base_directory(self):
        row = len(self.basedir_entries) * 5
        label = Label(self.root, text=f"Base Directory {len(self.basedir_entries) + 1}:")
        label.grid(row=row, column=0, sticky='w')
        basedir_entry = Entry(self.root, width=50)
        basedir_entry.grid(row=row, column=1, padx=10, pady=5, sticky='ew')
        self.basedir_entries.append(basedir_entry)

        subdirs_listbox = Listbox(self.root, selectmode=MULTIPLE, height=5)
        self.subdirs_listboxes.append(subdirs_listbox)
        browse_button = Button(self.root, text="Browse", command=lambda e=basedir_entry, l=subdirs_listbox: self.browse_directory(e, l, self.add_button))
        browse_button.grid(row=row, column=2, padx=10, pady=5)

        subdirs_label = Label(self.root, text=f"Select Subdirectories for Base Directory {len(self.basedir_entries)}:")
        subdirs_label.grid(row=row + 1, column=0, sticky='w')
        subdirs_listbox.grid(row=row + 2, column=1, padx=10, pady=5, columnspan=2, sticky='ew')
        subdirs_listbox.grid_remove()

        file_count_label = Label(self.root, text="Files: 0")
        file_count_label.grid(row=row + 3, column=0, columnspan=3, sticky='w')
        self.file_count_labels.append(file_count_label)

        progress_label = Label(self.root, text="Progress: 0.00%")
        progress_label.grid(row=row + 4, column=0, columnspan=3, sticky='w')
        self.progress_labels.append(progress_label)

        if len(self.basedir_entries) >= 5:
            self.add_button.grid_remove()

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, self.append, msg)

    def append(self, msg):
        self.text_widget.insert(END, msg + '\n')
        self.text_widget.see(END)
        self.flush()

def main():
    root = Tk()
    app = MD5ChecksumApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
