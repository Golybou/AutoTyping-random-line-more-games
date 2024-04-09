import random
import time
import os
import sys
from PIL import Image, ImageTk
from tkinter import Tk, Label, Button, Entry, filedialog, StringVar, font, messagebox, Toplevel, Canvas, ttk
import keyboard
import winreg
import webbrowser
import threading
import unicodedata


class AutoTyperGUI:
    def __init__(self, root):
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=16)

        self.root = root
        root.title("trashtolk more game by Golyb0u")
        root.geometry('700x600')
        root.configure(bg="#535353")

        self.file_label = Label(root, text="The file with the lines is not selected", bg="#535353", fg="white")
        self.file_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.select_button = Button(root, text="Select a file with lines", bg="#535353", fg="white", command=self.select_file)
        self.select_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.activate_button = Button(root, bg="#535353", fg="white", text="Activate the script", command=self.activate_script, state="normal")
        self.activate_button.grid(row=2, column=0, columnspan=2, pady=10)
        self.prefix_entry = Entry(root, bg="#535353", fg="white", font=("Helvetica", 10))
        self.prefix_entry.grid(row=3, column=0, columnspan=2, pady=10)
        self.prefix_entry.insert(0, "Set a nickname for the attack")

        self.activate_chat_button = None

        self.phrases = []
        self.current_index = 0
        self.hotkey = None
        self.last_invoked = 0

    def activate_script(self):
        if self.hotkey is not None:
            keyboard.remove_hotkey(self.hotkey)

        self.hotkey = self.hotkey_button.get_hotkey()
        self.chat_hotkey = self.activate_chat_button.get_hotkey()

        try:
            keyboard.add_hotkey(self.hotkey, self.type_phrase)
            keyboard.add_hotkey(self.chat_hotkey, self.activate_chat)
        except keyboard.keyboard.KeyAlreadyTakenException:
            messagebox.showerror("Error", "One of the hotkeys is already taken. Please select different ones.")
            return

        self.select_button.grid_forget()
        self.activate_button.grid_forget()
        self.hotkey_button.grid_forget()
        if hasattr(self, 'activate_chat_button'):
            self.activate_chat_button.grid_forget()

        self.file_label.pack_forget()
        self.select_button.pack_forget()
        self.activate_button.pack_forget()

        if hasattr(self, 'hotkey_button'):
            self.hotkey_button.pack_forget()
        if hasattr(self, 'activate_chat_button'):
            self.activate_chat_button.pack_forget()

    def select_file(self):
        filepath = filedialog.askopenfilename()
        if not os.path.exists(filepath):
            print("The selected file does not exist.")
            return
        filename = os.path.basename(filepath)
        self.file_label['text'] = "The file is selected: " + filename

        with open(filepath, 'r', encoding='utf-8') as file:
            self.phrases = []
            for phrase in file.readlines():
                phrase = phrase.strip()
                if phrase:
                    phrase = unicodedata.normalize('NFKC', phrase)
                    self.phrases.append(phrase)

        random.shuffle(self.phrases)

        self.hotkey_button = HotkeyButton(self.root,  self.activate_button, "Set the script activation key", bg="#535353", fg="white")
        self.hotkey_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.activate_chat_button = HotkeyButton(self.root, self.activate_button, self.hotkey_button, "Set the chat activation key", bg="#535353", fg="white")
        self.activate_chat_button.grid(row=4, column=0, columnspan=2, pady=10)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = int((screen_width / 2) - (300 / 2))
        y = int((screen_height / 2) - (100 / 2))

        self.hotkey_button.prompt_window.geometry(f"300x100+{x}+{y}")

        self.hotkey_button.grid(row=3, column=0, columnspan=2, pady=10)
        self.hotkey_button.other_button = self.activate_chat_button

    def activate_chat(self):
        print("Chat is activated")

    def type_phrase(self):
        current_time = time.time()
        if current_time - self.last_invoked < 1:
            return
        self.last_invoked = current_time

        if self.current_index >= len(self.phrases):
            self.current_index = 0
            random.shuffle(self.phrases)

        random_phrase = self.phrases[self.current_index]
        self.current_index += 1

        prefix = self.prefix_entry.get().strip()
        if prefix:
            random_phrase = prefix + " " + random_phrase

        keyboard.press_and_release(self.activate_chat_button.get_hotkey())
        time.sleep(0.1)

        typing_delay = 0.1 / len(random_phrase)

        for char in random_phrase:
            keyboard.write(char)
            time.sleep(typing_delay)

        time.sleep(0.5)
        keyboard.press_and_release('enter')


class HotkeyButton(Button):
    def __init__(self, root, activate_button, other_button=None, button_text="Set the script activation key", bg=None, fg=None):
        super().__init__(root, text=button_text, command=self.configure_hotkey, bg=bg, fg=fg)
        self.activate_button = activate_button
        self.other_button = other_button
        self.hotkey = None

        self.prompt_window = Toplevel(root)
        self.prompt_window.title("Setting the key")
        self.prompt_window.geometry('300x100')
        self.prompt_window.configure(bg='#535353') 
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        x = int((screen_width / 2) - (300 / 2))
        y = int((screen_height / 2) - (100 / 2))

        self.prompt_window.geometry(f"300x100+{x}+{y}")

        self.prompt_window.withdraw()

        self.prompt_label = Label(self.prompt_window, text="type key:", bg="#535353", fg="white")
        self.prompt_label.pack(pady=10)
        self.prompt_entry = Entry(self.prompt_window, bg="#535353", fg="white")
        self.prompt_entry.pack()

    def configure_hotkey(self):
        self.prompt_window.deiconify()
        self.prompt_entry.focus_set()
        self.prompt_entry.bind("<Key>", self.set_hotkey)

    def set_hotkey(self, event):
        self.hotkey = event.keysym.upper()
        self["text"] = f"key selected: {self.hotkey}"
        self.unbind("<Key>")
        self.focus_set()

        if self.other_button and self.other_button.get_hotkey():
            self.activate_button.configure(state="normal")

        self.prompt_window.withdraw()

        self.prompt_entry.unbind("<Key>")
        self.prompt_entry.delete(0, 'end')

    def get_hotkey(self):
        return self.hotkey


def main():
    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = int((screen_width / 2) - (800 / 2))
    y = int((screen_height / 2) - (600 / 2))

    root.geometry(f"800x600+{x}+{y}")
    root.configure(bg='#535353')

    my_gui = AutoTyperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
