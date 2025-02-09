import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import askstring
import fitz
from PIL import Image, ImageTk

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("CourseHelpr with Chatbot")
        self.geometry("1920x1080")

        self.courses = []  # To hold the course objects

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        # Button to open chatbot
        self.chatbot_button = ttk.Button(button_frame, text="Open Chatbot", command=self.open_chatbot)
        self.chatbot_button.pack(side="left", padx=5)

        # Open PDF button
        self.Importbutton = ttk.Button(button_frame, text="Import Presentation", command=self.import_presentation)
        self.Importbutton.pack(side="left", padx=5)

        self.add_course_button = ttk.Button(button_frame, text="Add Course", command=self.add_course)
        self.add_course_button.pack(side="left", padx=5)

        self.add_sub_section_button = ttk.Button(button_frame, text="Add Sub-Section", command=self.add_sub_section)
        self.add_sub_section_button.pack(side="left", padx=5)

        self.delete_course_button = ttk.Button(button_frame, text="Delete Course", command=self.delete_course)
        self.delete_course_button.pack(side="left", padx=5)

        # Delete lecture button
        self.delete_lecture_button = ttk.Button(button_frame, text="Delete Lecture", command=self.delete_lecture)
        self.delete_lecture_button.pack(side="left", padx=5)

        # Create the notebook for course tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.load_courses()

    def open_chatbot(self):
        # Open a new window for the chatbot interaction
        chatbot_window = tk.Toplevel(self)
        chatbot_window.title("Chatbot")
        chatbot_window.geometry("500x500")

        self.chat_output = tk.Text(chatbot_window, wrap="word", state="disabled", height=20, width=60)
        self.chat_output.pack(pady=10)

        self.chat_input = tk.Entry(chatbot_window, width=50)
        self.chat_input.pack(pady=10)

        send_button = ttk.Button(chatbot_window, text="Send", command=lambda: self.chatbot_response(chatbot_window))
        send_button.pack(pady=5)

    def load_courses(self):
        classes_dir = os.path.join(os.getcwd(), "classes")
        if os.path.exists(classes_dir):
            for course_name in os.listdir(classes_dir):
                course_path = os.path.join(classes_dir, course_name)
                if os.path.isdir(course_path):
                    course = Course(course_name)
                    self.courses.append(course)
                    self.create_course_tabs()

    def load_presentations(self, course):
        course_dir = os.path.join(os.getcwd(), "classes", course.name)
        if os.path.exists(course_dir):
            for file_name in os.listdir(course_dir):
                if file_name.endswith(".pdf"):
                    file_path = os.path.join(course_dir, file_name)
                    tab = ttk.Frame(course.notebook)
                    course.notebook.add(tab, text=file_name)
                    self.display_pdf(file_path, tab)

    def delete_course(self):
        selected_tab_id = self.notebook.select()
        if not selected_tab_id:
            messagebox.showwarning("No Course Selected", "Please select a course tab to delete.")
            return

        course_name = self.notebook.tab(selected_tab_id, "text")
        if messagebox.askyesno("Delete Course", f"Are you sure you want to delete the course '{course_name}'?"):
            # Remove the course directory
            course_dir = os.path.join(os.getcwd(), "classes", course_name)
            if os.path.exists(course_dir):
                for root, dirs, files in os.walk(course_dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(course_dir)

            # Remove the course tab
            self.notebook.forget(selected_tab_id)

            # Remove the course from the list
            self.courses = [c for c in self.courses if c.name != course_name]
    def delete_lecture(self):
        selected_tab_id = self.notebook.select()
        if not selected_tab_id:
            messagebox.showwarning("No Course Selected", "Please select a course tab to delete a lecture.")
            return

        course_name = self.notebook.tab(selected_tab_id, "text")
        course = next((c for c in self.courses if c.name == course_name), None)
        if course:
            selected_sub_tab_id = course.notebook.select()
            if not selected_sub_tab_id:
                messagebox.showwarning("No Lecture Selected", "Please select a lecture tab to delete.")
                return

            lecture_name = course.notebook.tab(selected_sub_tab_id, "text")
            if messagebox.askyesno("Delete Lecture", f"Are you sure you want to delete the lecture '{lecture_name}'?"):
                # Remove the lecture file
                lecture_path = os.path.join(os.getcwd(), "classes", course_name, lecture_name)
                if os.path.exists(lecture_path):
                    os.remove(lecture_path)

                # Remove the lecture tab
                course.notebook.forget(selected_sub_tab_id)

    def add_course(self):
        course_name = askstring("Course Name", "Enter the course name:")
        if course_name:
            course = Course(course_name)
            self.courses.append(course)
            self.create_course_tabs()

    def add_sub_section(self):
        selected_tab_id = self.notebook.select()
        if not selected_tab_id:
            messagebox.showwarning("No Course Selected", "Please select a course tab to add a sub-section.")
            return

        sub_section_name = askstring("Sub-Section Name", "Enter the sub-section name:")
        if sub_section_name:
            selected_tab = self.notebook.nametowidget(selected_tab_id)
            course_name = self.notebook.tab(selected_tab, "text")
            course = next((c for c in self.courses if c.name == course_name), None)
            if course:
                sub_tab = ttk.Frame(course.notebook)
                course.notebook.add(sub_tab, text=sub_section_name)

    def import_presentation(self):
        selected_tab_id = self.notebook.select()
        if not selected_tab_id:
            messagebox.showwarning("No Course Selected", "Please select a course tab to import the presentation.")
            return

        file_path = askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            selected_tab = self.notebook.nametowidget(selected_tab_id)
            course_name = self.notebook.tab(selected_tab, "text")

            # Prompt the user for a new name for the file
            new_file_name = askstring("Rename File", "Enter the new name for the file (without extension):")
            if not new_file_name:
                messagebox.showwarning("Invalid Name", "File name cannot be empty.")
                return

            new_file_name += ".pdf"

            classes_dir = os.path.join(os.getcwd(), "classes")
            if not os.path.exists(classes_dir):
                os.makedirs(classes_dir)

            course_dir = os.path.join(classes_dir, course_name)
            if not os.path.exists(course_dir):
                os.makedirs(course_dir)

            new_file_path = os.path.join(course_dir, new_file_name)
            with open(file_path, 'rb') as src_file:
                with open(new_file_path, 'wb') as dest_file:
                    dest_file.write(src_file.read())

            course = next((c for c in self.courses if c.name == course_name), None)
            if course:
                sub_tab = ttk.Frame(course.notebook)
                course.notebook.add(sub_tab, text=new_file_name)
                self.display_pdf(new_file_path, sub_tab)

    def display_pdf(self, file_path, tab):
        pdf_document = fitz.open(file_path)

        for widget in tab.winfo_children():
            widget.destroy()

        canvas_frame = ttk.Frame(tab)
        canvas_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)

        page_images = []

        y_offset = 0
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_tk = ImageTk.PhotoImage(img)

            label = tk.Label(canvas, image=img_tk)
            label.image = img_tk
            page_images.append(label)

            canvas.create_window((0, y_offset), window=label, anchor="nw")
            y_offset += pix.height

        tab.canvas = canvas
        canvas.bind("<MouseWheel>", lambda event: self.on_mousewheel(event, canvas))

    def create_course_tabs(self):
        for course in self.courses:
            if not hasattr(course, 'tab'):
                tab = ttk.Frame(self.notebook)
                self.notebook.add(tab, text=course.name)
                course.tab = tab
                course.notebook = ttk.Notebook(tab)
                course.notebook.pack(fill="both", expand=True)
                self.load_presentations(course)

    def on_tab_changed(self, event):
        selected_tab = event.widget.nametowidget(event.widget.select())
        for child in selected_tab.winfo_children():
            if isinstance(child, ttk.Notebook):
                child.bind("<MouseWheel>", lambda event: self.on_mousewheel(event, child))

    def on_mousewheel(self, event, widget):
        if event.delta > 0:
            widget.yview_scroll(-1, "units")
        elif event.delta < 0:
            widget.yview_scroll(1, "units")

class Course:
    def __init__(self, name):
        self.name = name
        self.notebook = None

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()