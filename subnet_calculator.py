"""A standalone IPv4 subnet calculator with a classic desktop layout."""

import ipaddress
import tkinter as tk
from tkinter import ttk


BACKGROUND = "#bdbbbd"
CLASSES = {
    "A": (8, "1 - 126", "10.0.0.0", "0"),
    "B": (16, "128 - 191", "172.16.0.0", "10"),
    "C": (24, "192 - 223", "192.168.0.0", "110"),
}


def subnet(address, prefix):
    try:
        ip = ipaddress.IPv4Address(address.strip())
    except ValueError:
        return None

    # Accept host addresses and let ipaddress find the containing subnet.
    network = ipaddress.IPv4Network((ip, prefix), strict=False)
    first = network.network_address
    last = network.broadcast_address
    # Only conventional subnets reserve both ends of the address block.
    if prefix < 31:
        first += 1
        last -= 1

    return {
        "Hex IP Address": ".".join(format(value, "02X") for value in ip.packed),
        "Wildcard Mask": str(network.hostmask),
        "Host Address Range": str(first) if first == last else f"{first} - {last}",
        "Subnet ID": str(network.network_address),
        "Broadcast Address": str(network.broadcast_address),
    }


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Subnet Calculator")
        self.geometry("540x603")
        self.resizable(False, False)
        self.configure(bg=BACKGROUND)
        self.selected_class = tk.StringVar(value="A")
        self.address = tk.StringVar(value="10.0.0.0")
        self.prefix = 16
        self.outputs = {}
        self.selects = {}

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Retro.TCombobox", font=("Arial", 15), arrowsize=17)
        style.map("Retro.TCombobox", fieldbackground=[("readonly", "#fffefe")],
                  foreground=[("readonly", "#161616")])
        self.option_add("*TCombobox*Listbox.font", ("Arial", 12))

        header = tk.Canvas(self, bg="#050505", highlightthickness=1,
                           highlightbackground="#a7a5a7")
        header.place(x=0, y=0, width=540, height=35)
        header.create_oval(5, 8, 25, 26, outline="#aaa", width=2)
        header.create_text(34, 18, anchor="w", text="Subnet Calculator",
                           fill="white", font=("Arial", 17, "bold"))

        self.caption("Network Class", 16, 48)
        for name, x in zip(CLASSES, (15, 68, 121)):
            tk.Label(self, text=name, bg=BACKGROUND, font=("Arial", 13),
                     padx=0, pady=0).place(x=x, y=77)
            tk.Radiobutton(self, variable=self.selected_class, value=name,
                           command=self.change_class, bg=BACKGROUND,
                           activebackground=BACKGROUND, selectcolor="white",
                           padx=0, pady=0).place(x=x + 22, y=74)

        self.caption("IP Address", 16, 116)
        self.ip_entry = tk.Entry(self, textvariable=self.address, relief="sunken",
                                 bd=2, font=("Arial", 15), bg="#fffefe", fg="#161616")
        self.ip_entry.place(x=16, y=140, width=221, height=33)

        self.add_select("Subnet Mask", 16, 186, 210)
        self.add_select("Subnet Bits", 16, 252, 277)
        self.add_select("Maximum Subnets", 16, 319, 343)
        self.add_output("First Octet Range", 285, 47, 71)
        self.add_output("Hex IP Address", 285, 115, 141)
        self.add_output("Wildcard Mask", 285, 181, 207)
        self.add_select("Mask Bits", 285, 252, 274)
        self.add_select("Hosts per Subnet", 285, 318, 340)
        self.selects["Hosts per Subnet"].configure(style="Hosts.TCombobox")
        style.configure("Hosts.TCombobox", bordercolor="#64a4cd")
        self.add_output("Host Address Range", 17, 385, 410, width=489)
        self.add_output("Subnet ID", 17, 454, 478)
        self.add_output("Broadcast Address", 285, 452, 477)

        self.caption("Subnet Bitmap", 16, 524)
        self.bitmap = tk.Text(self, height=1, relief="sunken", bd=2,
                              bg="#f2f0f2", font=("Consolas", 14, "bold"),
                              wrap="none", padx=0, pady=4, takefocus=False)
        self.bitmap.place(x=16, y=547, width=489, height=34)
        self.bitmap.tag_configure("center", justify="center")
        self.bitmap.tag_configure("network", foreground="#a32d37")
        self.bitmap.tag_configure("subnet", foreground="#89681b")
        self.bitmap.tag_configure("host", foreground="white", background="#086bb6")
        self.address.trace_add("write", self.address_changed)
        self.refresh()

    def caption(self, title, x, y):
        tk.Label(self, text=title, bg=BACKGROUND, fg="#161616",
                 font=("Arial", 13), padx=0, pady=0).place(x=x + 2, y=y)

    def add_output(self, title, x, y, box_y, width=221):
        self.caption(title, x, y)
        variable = tk.StringVar()
        tk.Entry(self, textvariable=variable, state="readonly", relief="sunken",
                 bd=2, justify="center", font=("Arial", 15),
                 readonlybackground=BACKGROUND, fg="#161616").place(
                     x=x, y=box_y, width=width, height=33)
        self.outputs[title] = variable

    def add_select(self, title, x, y, box_y):
        self.caption(title, x, y)
        widget = ttk.Combobox(self, state="readonly", style="Retro.TCombobox",
                              font=("Arial", 15))
        widget.place(x=x, y=box_y, width=221, height=31)
        widget.bind("<<ComboboxSelected>>", self.prefix_changed)
        self.selects[title] = widget

    def change_class(self):
        self.address.set(CLASSES[self.selected_class.get()][2])

    def address_changed(self, *_):
        if subnet(self.address.get(), self.prefix):
            first = int(self.address.get().strip().split(".")[0])
            if 1 <= first <= 126:
                self.selected_class.set("A")
            elif 128 <= first <= 191:
                self.selected_class.set("B")
            elif 192 <= first <= 223:
                self.selected_class.set("C")
        self.prefix = max(self.prefix, CLASSES[self.selected_class.get()][0])
        self.refresh()

    def prefix_changed(self, event):
        base = CLASSES[self.selected_class.get()][0]
        self.prefix = base + event.widget.current()
        self.refresh()

    def refresh(self):
        base, octets, _, signature = CLASSES[self.selected_class.get()]
        # Each dropdown has one choice per prefix, in the same order.
        prefixes = range(base, 33)
        values = {
            "Subnet Mask": [str(ipaddress.IPv4Network((0, bits)).netmask) for bits in prefixes],
            "Subnet Bits": [bits - base for bits in prefixes],
            "Maximum Subnets": [2 ** (bits - base) for bits in prefixes],
            "Mask Bits": list(prefixes),
            "Hosts per Subnet": [2 ** (32 - bits) - (2 if bits < 31 else 0) for bits in prefixes],
        }
        for title, widget in self.selects.items():
            widget.configure(values=values[title])
            widget.current(self.prefix - base)

        result = subnet(self.address.get(), self.prefix)
        self.ip_entry.configure(fg="#161616" if result else "#a32d37")
        if result is None:
            result = {"Host Address Range": "Enter a valid IPv4 address"}
        result["First Octet Range"] = octets
        for title, variable in self.outputs.items():
            variable.set(result.get(title, "—"))

        # Fill the class, borrowed subnet, and remaining host bits in order.
        bits = signature.ljust(base, "n").ljust(self.prefix, "s").ljust(32, "h")
        self.bitmap.configure(state="normal")
        self.bitmap.delete("1.0", "end")
        for index, bit in enumerate(bits):
            if index and index % 8 == 0:
                self.bitmap.insert("end", ".", ("center",))
            group = "network" if index < base else "subnet" if index < self.prefix else "host"
            self.bitmap.insert("end", bit, ("center", group))
        self.bitmap.configure(state="disabled")


if __name__ == "__main__":
    Calculator().mainloop()
