from datetime import datetime

from simulator.parking_generator import simulate_slot_change


class WorkerMCU:
    """
    Simulasi Worker MCU (Edge Node).

    Setiap Worker MCU bertanggung jawab penuh terhadap zona parkir miliknya
    sendiri. Node ini beroperasi secara independen — tidak ada komunikasi
    langsung antar Worker MCU. Semua data diteruskan ke Master MCU melalui
    mekanisme distribusi paket.

    Attributes
    ----------
    name : str
        Identifier unik node ini (contoh: "MCU A - Area A").
    slots : dict
        Status setiap slot parkir: {slot_name: 0 or 1}.
    last_update : str
        Timestamp terakhir kali ada perubahan slot pada node ini.
    """

    def __init__(self, name: str, slots: list):
        self.name = name
        self.slots = {slot: 0 for slot in slots}
        self.last_update = "-"

    def simulate_sensor_change(self) -> list:
        """
        DISTRIBUTION PIPELINE WORKFLOW — STAGE 1:
        Distributed Sensor Reading

        Meminta modul simulator untuk mengevaluasi perubahan status slot
        secara acak, merepresentasikan sensor parkir (ultrasonik / IR)
        yang mendeteksi kendaraan masuk atau keluar.

        Status slot:
            0 = KOSONG (available)
            1 = TERISI (occupied)

        Returns
        -------
        list
            Daftar nama slot yang berubah status pada cycle ini.
        """
        changed_slots = simulate_slot_change(self.slots)

        if changed_slots:
            self.last_update = datetime.now().strftime("%H:%M:%S")

        return changed_slots

    def create_data_packet(self) -> dict:
        """
        DISTRIBUTION PIPELINE WORKFLOW — STAGE 2:
        Worker MCU Local Processing

        Membuat packet data terstruktur yang siap dikirim ke Master MCU.
        Packet berisi identitas node, timestamp update terakhir, dan
        snapshot lengkap status semua slot di zona ini.

        Returns
        -------
        dict
            Data packet dengan kunci: "node", "timestamp", "data".
        """
        return {
            "node": self.name,
            "timestamp": self.last_update,
            "data": self.slots.copy()
        }
