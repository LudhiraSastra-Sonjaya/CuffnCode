class MasterMCU:
    """
    Simulasi Master MCU (Central Aggregation Node).

    Master MCU adalah satu-satunya titik pengumpul data dari seluruh
    Worker MCU dalam topologi ini. Master tidak melakukan pembacaan sensor
    secara langsung — ia hanya menerima paket dari Worker, mengagregasi
    data, dan menghitung statistik parkir secara global.

    Attributes
    ----------
    received_packets : dict
        Buffer paket yang diterima dari setiap Worker MCU.
        Format: {node_name: packet_dict}
    """

    def __init__(self):
        self.received_packets = {}

    def receive_packet(self, packet: dict) -> None:
        """
        DISTRIBUTION PIPELINE WORKFLOW — STAGE 3:
        Data Packet Distribution

        Menerima dan menyimpan paket data dari satu Worker MCU.
        Setiap paket baru menimpa (overwrite) paket sebelumnya dari
        node yang sama, sehingga buffer selalu berisi data terbaru.

        Parameters
        ----------
        packet : dict
            Data packet dari Worker MCU. Harus memiliki kunci "node".
        """
        self.received_packets[packet["node"]] = packet

    def aggregate_and_calculate(self) -> tuple:
        """
        DISTRIBUTION PIPELINE WORKFLOW — STAGE 4 & 5:
        Master MCU Data Aggregation + Parking Status Calculation

        Mengiterasi semua paket yang diterima, menghitung jumlah slot
        terisi dan kosong per area, lalu mengembalikan ringkasan global.

        Returns
        -------
        tuple
            (total_slots, occupied_slots, available_slots,
             all_packets, area_summary)
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
