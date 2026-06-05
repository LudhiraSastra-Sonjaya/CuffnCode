import tkinter as tk
from tkinter import ttk
from datetime import datetime
from collections import deque
import random

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class WorkerMCU:
    """
    Simulasi Worker MCU.
    Setiap Worker MCU bertanggung jawab terhadap beberapa slot parkir.
    """

    def __init__(self, name, slots):
        self.name = name
        self.slots = {slot: 0 for slot in slots}
        self.last_update = "-"

    def simulate_sensor_change(self):
        """
        DISTRIBUTION PIPELINE WORKFLOW STAGE 1:
        Distributed Sensor Reading

        Status slot berubah otomatis secara acak.
        0 = kosong
        1 = terisi
        """
        changed_slots = []

        for slot in self.slots:
            change_probability = random.random()

            # 25% kemungkinan slot berubah status
            if change_probability < 0.25:
                self.slots[slot] = 1 if self.slots[slot] == 0 else 0
                changed_slots.append(slot)

        if changed_slots:
            self.last_update = datetime.now().strftime("%H:%M:%S")

        return changed_slots

    def create_data_packet(self):
        """
        DISTRIBUTION PIPELINE WORKFLOW STAGE 2:
        Worker MCU Local Processing

        Worker membuat packet data untuk dikirim ke Master MCU.
        """
        return {
            "node": self.name,
            "timestamp": self.last_update,
            "data": self.slots.copy()
        }


class MasterMCU:
    """
    Simulasi Master MCU.
    Master menerima data dari semua Worker MCU,
    melakukan agregasi, lalu menghitung status parkir.
    """

    def __init__(self):
        self.received_packets = {}

    def receive_packet(self, packet):
        """
        DISTRIBUTION PIPELINE WORKFLOW STAGE 3:
        Data Packet Distribution
        """
        self.received_packets[packet["node"]] = packet

    def aggregate_and_calculate(self):
        """
        DISTRIBUTION PIPELINE WORKFLOW STAGE 4 & 5:
        Master MCU Data Aggregation + Parking Status Calculation
        """
        total_slots = 0
        occupied_slots = 0
        area_summary = {}

        for node_name, packet in self.received_packets.items():
            area_total = len(packet["data"])
            area_occupied = sum(packet["data"].values())
            area_available = area_total - area_occupied

            area_summary[node_name] = {
                "total": area_total,
                "occupied": area_occupied,
                "available": area_available
            }

            total_slots += area_total
            occupied_slots += area_occupied

        available_slots = total_slots - occupied_slots

        return total_slots, occupied_slots, available_slots, self.received_packets, area_summary


class SmartParkingDistributionWorkflowGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Parking Multi-MCU Distribution Pipeline Workflow")
        self.root.geometry("1280x800")
        self.root.resizable(False, False)
        self.root.configure(bg="#ffffff")

        # Delay workflow
        # Bisa diubah kalau ingin lebih cepat/lambat
        self.stage_delay = 500
        self.cycle_delay = 1000

        # Virtual Worker MCU
        self.worker_a = WorkerMCU("MCU A - Area A", ["A1", "A2", "A3"])
        self.worker_b = WorkerMCU("MCU B - Area B", ["B1", "B2", "B3"])
        self.worker_c = WorkerMCU("MCU C - Area C", ["C1", "C2", "C3"])

        self.workers = [self.worker_a, self.worker_b, self.worker_c]
        self.master = MasterMCU()

        self.running = False
        self.cycle_count = 0

        # Data sementara per-cycle
        self.current_worker_changes = {}
        self.current_packets = []
        self.current_result = None

        # GUI references
        self.slot_buttons = {}
        self.node_labels = {}
        self.workflow_labels = {}

        # Graph history
        self.time_history = deque(maxlen=40)
        self.occupied_history = deque(maxlen=40)
        self.available_history = deque(maxlen=40)

        # Heartbeat / ECG graph history
        self.ecg_history = deque(maxlen=80)
        self.ecg_counter = 0

        self.setup_style()
        self.create_widgets()
        self.initialize_master_packets()
        self.update_dashboard()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Title.TLabel",
            font=("Arial", 22, "bold"),
            foreground="#111827",
            background="#ffffff"
        )

        style.configure(
            "Subtitle.TLabel",
            font=("Arial", 11),
            foreground="#4b5563",
            background="#ffffff"
        )

        style.configure(
            "Summary.TLabel",
            font=("Arial", 13, "bold"),
            background="#ffffff",
            foreground="#111827"
        )

        style.configure(
            "CardTitle.TLabel",
            font=("Arial", 12, "bold"),
            background="#f9fafb",
            foreground="#111827"
        )

        style.configure(
            "Info.TLabel",
            font=("Arial", 9),
            background="#f9fafb",
            foreground="#374151"
        )

    def create_widgets(self):
        self.create_header()

        content_frame = tk.Frame(self.root, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_frame = tk.Frame(content_frame, bg="#ffffff")
        left_frame.pack(side="left", fill="both", expand=False)

        right_frame = tk.Frame(content_frame, bg="#ffffff")
        right_frame.pack(side="right", fill="both", expand=True, padx=(20, 0))

        self.create_parking_area(left_frame)
        self.create_summary(left_frame)
        self.create_distribution_workflow_panel(left_frame)
        self.create_control_buttons(left_frame)
        self.create_log(left_frame)

        self.create_graph(right_frame)

    def create_header(self):
        header_frame = tk.Frame(self.root, bg="#ffffff")
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        title = ttk.Label(
            header_frame,
            text="Smart Parking Multi-MCU Distribution Pipeline Workflow",
            style="Title.TLabel"
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            header_frame,
            text="Simulasi otomatis sistem parkir pintar berbasis multi-MCU, distributed system, parallel processing, distribution workflow, dan heartbeat graph.",
            style="Subtitle.TLabel"
        )
        subtitle.pack(anchor="w", pady=(5, 0))

    def create_parking_area(self, parent):
        area_frame = tk.Frame(parent, bg="#ffffff")
        area_frame.pack(fill="x", pady=(0, 12))

        self.create_worker_card(area_frame, self.worker_a, 0)
        self.create_worker_card(area_frame, self.worker_b, 1)
        self.create_worker_card(area_frame, self.worker_c, 2)

    def create_worker_card(self, parent, worker, column):
        card = tk.Frame(
            parent,
            bg="#f9fafb",
            highlightbackground="#d1d5db",
            highlightthickness=1,
            width=175,
            height=245
        )
        card.grid(row=0, column=column, padx=6, sticky="n")
        card.grid_propagate(False)

        title = ttk.Label(
            card,
            text=worker.name,
            style="CardTitle.TLabel"
        )
        title.pack(anchor="w", padx=10, pady=(10, 4))

        info_label = ttk.Label(
            card,
            text="Last Update: -",
            style="Info.TLabel"
        )
        info_label.pack(anchor="w", padx=10, pady=(0, 6))

        self.node_labels[worker.name] = info_label

        for slot in worker.slots:
            btn = tk.Button(
                card,
                text=f"{slot}\nKOSONG",
                font=("Arial", 11, "bold"),
                width=10,
                height=2,
                bg="#22c55e",
                fg="white",
                relief="flat",
                state="disabled",
                disabledforeground="white"
            )
            btn.pack(padx=10, pady=4)

            self.slot_buttons[slot] = btn

    def create_summary(self, parent):
        summary_frame = tk.Frame(
            parent,
            bg="#ffffff",
            highlightbackground="#d1d5db",
            highlightthickness=1
        )
        summary_frame.pack(fill="x", pady=(0, 12))

        summary_title = ttk.Label(
            summary_frame,
            text="Master MCU Dashboard",
            style="Summary.TLabel"
        )
        summary_title.pack(anchor="w", padx=15, pady=(10, 4))

        self.cycle_label = ttk.Label(
            summary_frame,
            text="Cycle: 0",
            style="Summary.TLabel"
        )
        self.cycle_label.pack(anchor="w", padx=15, pady=2)

        self.total_label = ttk.Label(
            summary_frame,
            text="Total Slot: 0",
            style="Summary.TLabel"
        )
        self.total_label.pack(anchor="w", padx=15, pady=2)

        self.occupied_label = ttk.Label(
            summary_frame,
            text="Slot Terisi: 0",
            style="Summary.TLabel"
        )
        self.occupied_label.pack(anchor="w", padx=15, pady=2)

        self.available_label = ttk.Label(
            summary_frame,
            text="Slot Kosong: 0",
            style="Summary.TLabel"
        )
        self.available_label.pack(anchor="w", padx=15, pady=(2, 10))

    def create_distribution_workflow_panel(self, parent):
        workflow_frame = tk.Frame(
            parent,
            bg="#ffffff",
            highlightbackground="#d1d5db",
            highlightthickness=1
        )
        workflow_frame.pack(fill="x", pady=(0, 12))

        title = tk.Label(
            workflow_frame,
            text="Distribution Pipeline Workflow",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#111827"
        )
        title.pack(anchor="w", padx=15, pady=(10, 6))

        stages = [
            "1. Distributed Sensor Reading",
            "2. Worker MCU Local Processing",
            "3. Data Packet Distribution",
            "4. Master MCU Data Aggregation",
            "5. Parking Status Calculation",
            "6. Dashboard and Graph Update"
        ]

        for stage in stages:
            label = tk.Label(
                workflow_frame,
                text=f"○ {stage}",
                font=("Arial", 10, "bold"),
                bg="#ffffff",
                fg="#6b7280",
                anchor="w"
            )
            label.pack(fill="x", padx=15, pady=2)
            self.workflow_labels[stage] = label

        self.workflow_info = tk.Label(
            workflow_frame,
            text="Status: Idle",
            font=("Arial", 9),
            bg="#ffffff",
            fg="#374151"
        )
        self.workflow_info.pack(anchor="w", padx=15, pady=(6, 10))

    def create_control_buttons(self, parent):
        button_frame = tk.Frame(parent, bg="#ffffff")
        button_frame.pack(fill="x", pady=(0, 12))

        self.start_button = tk.Button(
            button_frame,
            text="Start Simulation",
            font=("Arial", 10, "bold"),
            bg="#2563eb",
            fg="white",
            padx=10,
            pady=7,
            relief="flat",
            command=self.start_simulation
        )
        self.start_button.pack(side="left", padx=(0, 8))

        self.stop_button = tk.Button(
            button_frame,
            text="Stop",
            font=("Arial", 10, "bold"),
            bg="#f97316",
            fg="white",
            padx=10,
            pady=7,
            relief="flat",
            command=self.stop_simulation
        )
        self.stop_button.pack(side="left", padx=(0, 8))

        reset_button = tk.Button(
            button_frame,
            text="Reset",
            font=("Arial", 10, "bold"),
            bg="#dc2626",
            fg="white",
            padx=10,
            pady=7,
            relief="flat",
            command=self.reset_simulation
        )
        reset_button.pack(side="left")

    def create_log(self, parent):
        log_frame = tk.Frame(parent, bg="#ffffff")
        log_frame.pack(fill="both", expand=True)

        log_title = tk.Label(
            log_frame,
            text="Communication Log",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#111827"
        )
        log_title.pack(anchor="w", pady=(0, 5))

        self.log_text = tk.Text(
            log_frame,
            height=10,
            width=68,
            font=("Consolas", 9),
            bg="#111827",
            fg="#e5e7eb",
            insertbackground="#ffffff"
        )
        self.log_text.pack(fill="both", expand=True)

    def create_graph(self, parent):
        graph_title = tk.Label(
            parent,
            text="Real-Time Parking Activity Monitor",
            font=("Arial", 15, "bold"),
            bg="#ffffff",
            fg="#111827"
        )
        graph_title.pack(anchor="w", pady=(0, 10))

        self.figure = Figure(figsize=(6.7, 6.4), dpi=100)

        self.ax_line = self.figure.add_subplot(211)
        self.ax_bar = self.figure.add_subplot(212)

        self.figure.tight_layout(pad=3)

        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def initialize_master_packets(self):
        """
        Mengirim packet awal dari semua worker ke master,
        supaya dashboard langsung punya data awal.
        """
        for worker in self.workers:
            packet = worker.create_data_packet()
            self.master.receive_packet(packet)

    def set_workflow_stage(self, active_stage, status_text):
        """
        Mengubah tampilan Distribution Pipeline Workflow
        agar terlihat stage mana yang sedang berjalan.
        """
        for stage, label in self.workflow_labels.items():
            if stage == active_stage:
                label.config(text=f"● {stage}", fg="#2563eb")
            else:
                label.config(text=f"○ {stage}", fg="#6b7280")

        self.workflow_info.config(text=f"Status: {status_text}")
        self.root.update_idletasks()

    def start_simulation(self):
        if not self.running:
            self.running = True
            self.add_log("Distribution pipeline workflow started")
            self.run_distribution_workflow_cycle()

    def stop_simulation(self):
        self.running = False
        self.add_log("Distribution pipeline workflow stopped")
        self.workflow_info.config(text="Status: Stopped")

    def run_distribution_workflow_cycle(self):
        """
        DISTRIBUTION PIPELINE WORKFLOW WITH STAGE DELAY

        Workflow:
        1. Distributed Sensor Reading
        2. Worker MCU Local Processing
        3. Data Packet Distribution
        4. Master MCU Data Aggregation
        5. Parking Status Calculation
        6. Dashboard and Graph Update
        """

        if not self.running:
            return

        self.cycle_count += 1
        self.current_worker_changes = {}
        self.current_packets = []
        self.current_result = None

        self.stage_distributed_sensor_reading()

    def stage_distributed_sensor_reading(self):
        if not self.running:
            return

        self.set_workflow_stage(
            "1. Distributed Sensor Reading",
            "Each virtual sensor reads parking slot conditions"
        )

        self.current_worker_changes = {}

        for worker in self.workers:
            changed_slots = worker.simulate_sensor_change()
            self.current_worker_changes[worker.name] = changed_slots

        self.root.after(self.stage_delay, self.stage_worker_mcu_processing)

    def stage_worker_mcu_processing(self):
        if not self.running:
            return

        self.set_workflow_stage(
            "2. Worker MCU Local Processing",
            "Each Worker MCU processes its own parking area locally"
        )

        self.current_packets = []

        for worker in self.workers:
            packet = worker.create_data_packet()
            self.current_packets.append(packet)

            changed_slots = self.current_worker_changes[worker.name]

            if changed_slots:
                changed_text = ", ".join(changed_slots)
                self.add_log(f"{worker.name} processed local slot change: {changed_text}")
            else:
                self.add_log(f"{worker.name} processed local sensor data: no change")

        self.root.after(self.stage_delay, self.stage_data_packet_distribution)

    def stage_data_packet_distribution(self):
        if not self.running:
            return

        self.set_workflow_stage(
            "3. Data Packet Distribution",
            "Worker MCUs distribute packets to the Master MCU"
        )

        for packet in self.current_packets:
            self.master.receive_packet(packet)
            self.add_log(
                f"{packet['node']} distributed packet to Master MCU at {packet['timestamp']}"
            )

        self.root.after(self.stage_delay, self.stage_master_mcu_aggregation)

    def stage_master_mcu_aggregation(self):
        if not self.running:
            return

        self.set_workflow_stage(
            "4. Master MCU Data Aggregation",
            "Master MCU receives and aggregates distributed packets"
        )

        self.current_result = self.master.aggregate_and_calculate()

        self.root.after(self.stage_delay, self.stage_parking_status_calculation)

    def stage_parking_status_calculation(self):
        if not self.running:
            return

        self.set_workflow_stage(
            "5. Parking Status Calculation",
            "Master MCU calculates occupied and available parking slots"
        )

        total, occupied, available, all_data, area_summary = self.current_result

        self.update_dashboard_view(total, occupied, available)

        self.root.after(self.stage_delay, self.stage_dashboard_and_graph_update)

    def stage_dashboard_and_graph_update(self):
        if not self.running:
            return

        self.set_workflow_stage(
            "6. Dashboard and Graph Update",
            "GUI dashboard and heartbeat graph are updated"
        )

        total, occupied, available, all_data, area_summary = self.current_result

        self.update_graph(area_summary, occupied, available)

        self.workflow_info.config(
            text=f"Status: Distribution workflow cycle {self.cycle_count} completed"
        )

        self.root.after(self.cycle_delay, self.run_distribution_workflow_cycle)

    def update_dashboard(self):
        total, occupied, available, all_data, area_summary = self.master.aggregate_and_calculate()
        self.update_dashboard_view(total, occupied, available)
        self.update_graph(area_summary, occupied, available)

    def update_dashboard_view(self, total, occupied, available):
        self.cycle_label.config(text=f"Cycle: {self.cycle_count}")
        self.total_label.config(text=f"Total Slot: {total}")
        self.occupied_label.config(text=f"Slot Terisi: {occupied}")
        self.available_label.config(text=f"Slot Kosong: {available}")

        for worker in self.workers:
            self.node_labels[worker.name].config(
                text=f"Last Update: {worker.last_update}"
            )

            for slot, status in worker.slots.items():
                button = self.slot_buttons[slot]

                if status == 1:
                    button.config(
                        text=f"{slot}\nTERISI",
                        bg="#dc2626"
                    )
                else:
                    button.config(
                        text=f"{slot}\nKOSONG",
                        bg="#22c55e"
                    )

    def generate_heartbeat_signal(self, occupied, available):
        """
        Membuat sinyal seperti detak jantung.
        Dalam simulasi ini, spike merepresentasikan aktivitas parkir.
        Semakin banyak slot terisi, amplitudo sinyal sedikit meningkat.
        """

        heartbeat_pattern = [
            0.0, 0.05, 0.0, -0.08,
            0.2, 1.2, -0.55,
            0.35, 0.12, 0.0,
            0.0, 0.0, 0.0, 0.0
        ]

        amplitude = 1 + (occupied * 0.12)
        baseline = available * 0.03

        value = heartbeat_pattern[self.ecg_counter % len(heartbeat_pattern)]
        value = (value * amplitude) + baseline

        # Noise kecil supaya terlihat hidup
        value += random.uniform(-0.03, 0.03)

        self.ecg_counter += 1
        self.ecg_history.append(value)

    def update_graph(self, area_summary, occupied, available):
        now = datetime.now().strftime("%H:%M:%S")

        self.time_history.append(now)
        self.occupied_history.append(occupied)
        self.available_history.append(available)

        # Update heartbeat signal
        self.generate_heartbeat_signal(occupied, available)

        self.draw_graph(area_summary)

    def draw_graph(self, area_summary):
        self.ax_line.clear()
        self.ax_bar.clear()

        # =====================================================
        # GRAPH 1: ECG / Heartbeat Style Graph
        # =====================================================
        ecg_values = list(self.ecg_history)

        if not ecg_values:
            ecg_values = [0]

        x_values = list(range(len(ecg_values)))

        self.ax_line.plot(
            x_values,
            ecg_values,
            linewidth=2,
            label="Parking Activity Signal"
        )

        self.ax_line.set_title("Real-Time Parking Activity Signal")
        self.ax_line.set_xlabel("Time")
        self.ax_line.set_ylabel("Signal")
        self.ax_line.set_ylim(-1.0, 2.0)
        self.ax_line.legend(loc="upper right")
        self.ax_line.grid(True, alpha=0.3)

        if self.occupied_history:
            current_occupied = self.occupied_history[-1]
            current_available = self.available_history[-1]

            self.ax_line.text(
                0.02,
                0.88,
                f"OCCUPIED: {current_occupied} | AVAILABLE: {current_available}",
                transform=self.ax_line.transAxes,
                fontsize=9,
                fontweight="bold"
            )

        # =====================================================
        # GRAPH 2: Slot Terisi per Worker MCU
        # =====================================================
        area_names = []
        occupied_values = []

        for area, data in area_summary.items():
            short_name = area.replace("MCU ", "").replace(" - ", "\n")
            area_names.append(short_name)
            occupied_values.append(data["occupied"])

        if not area_names:
            area_names = ["A\nArea A", "B\nArea B", "C\nArea C"]
            occupied_values = [0, 0, 0]

        self.ax_bar.bar(area_names, occupied_values)
        self.ax_bar.set_title("Slot Terisi per Worker MCU")
        self.ax_bar.set_xlabel("Worker MCU")
        self.ax_bar.set_ylabel("Jumlah Terisi")
        self.ax_bar.set_ylim(0, 3)
        self.ax_bar.grid(True, axis="y", alpha=0.3)

        self.figure.tight_layout(pad=3)
        self.canvas.draw()

    def add_log(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{now}] {message}\n"

        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)

    def reset_simulation(self):
        self.running = False
        self.cycle_count = 0

        self.current_worker_changes = {}
        self.current_packets = []
        self.current_result = None

        for worker in self.workers:
            for slot in worker.slots:
                worker.slots[slot] = 0

            worker.last_update = "-"

        self.master.received_packets.clear()
        self.initialize_master_packets()

        self.time_history.clear()
        self.occupied_history.clear()
        self.available_history.clear()
        self.ecg_history.clear()
        self.ecg_counter = 0

        self.log_text.delete("1.0", tk.END)
        self.add_log("Distribution pipeline workflow reset: all parking slots are empty")

        for stage, label in self.workflow_labels.items():
            label.config(text=f"○ {stage}", fg="#6b7280")

        self.workflow_info.config(text="Status: Idle")

        self.update_dashboard()


def main():
    root = tk.Tk()
    SmartParkingDistributionWorkflowGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()