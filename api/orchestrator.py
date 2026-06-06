import operator
from collections.abc import Sequence
from typing import Annotated

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, ConfigDict, Field


# 1. Definisi State (Memori Global)
# State ini akan dibawa dan diperbarui oleh setiap agen yang bekerja
class UniverseState(BaseModel):
    model_config = ConfigDict(frozen=True)
    messages: Annotated[Sequence[BaseMessage], operator.add] = Field(
        default_factory=list
    )
    next_agent: str = ""


# 2. Inisialisasi Model Lokal (DeepSeek dari Ollama)
# Pastikan nama model sesuai dengan yang Anda daftarkan di Modelfile
llm = ChatOllama(model="uis-agent", temperature=0)


# 3. Node: Supervisor (Sang Manajer)
def supervisor_node(state: UniverseState):
    messages = state.messages

    # Prompt sistem yang memaksa model hanya membalas dengan nama domain
    system_prompt = (
        "Kamu adalah Supervisor AI di ML Agents Universe. "
        "Tugasmu HANYA membaca input pengguna dan merutekannya ke agen yang tepat.\n"
        "Pilihan agen: 'finance', 'nlp', 'science', 'mathematics', 'economy', 'education', 'entertainment', 'healthcare', 'legal', 'cybersecurity', 'creative', 'devops', 'data_engineering', 'osint', 'game_ai', 'productivity'.\n"
        "Balas HANYA dengan nama agen dalam huruf kecil tanpa tanda baca atau kalimat tambahan."
    )

    # Gabungkan prompt sistem dengan input terakhir dari pengguna
    routing_prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": messages[-1].content},
    ]

    # Minta model memutuskan
    response = llm.invoke(routing_prompt)
    content = response.content
    if isinstance(content, list):
        content = content[0] if isinstance(content[0], str) else str(content[0])
    routed_agent = str(content).strip().lower()

    # Fallback jika model menjawab di luar pilihan
    valid_agents = [
        "finance",
        "nlp",
        "science",
        "mathematics",
        "economy",
        "education",
        "entertainment",
        "healthcare",
        "legal",
        "cybersecurity",
        "creative",
        "devops",
        "data_engineering",
        "osint",
        "game_ai",
        "productivity",
    ]
    if routed_agent not in valid_agents:
        routed_agent = "nlp"  # Default ke NLP jika bingung

    print(f"[Supervisor] Merutekan tugas ke: -> {routed_agent.upper()}")
    return {"next_agent": routed_agent}


# 4. Node: Agen Pekerja (Mockup sementara)
def finance_agent(state: UniverseState):
    print("[Finance Agent] Menganalisis data pasar...")
    # Di sini nanti kita masukkan tool CCXT / Trading
    response = AIMessage(content="[Finance] Analisis trading selesai dieksekusi.")
    return {"messages": [response]}


def nlp_agent(state: UniverseState):
    print("[NLP Agent] Memproses bahasa natural...")
    # Implementasi Pemrosesan Bahasa Natural (NLP)
    # Di sini Anda akan menambahkan library seperti SpaCy atau Transformers
    # Untuk sementara, kita hanya akan mengembalikan pesan sederhana
    response = AIMessage(content="[NLP] Teks atau percakapan berhasil diproses.")
    return {"messages": [response]}


def science_agent(state: UniverseState):
    print("[Science Agent] Melakukan eksperimen...")
    # Implementasi Eksperimen Ilmiah (Misalnya simulasi fisika atau kimia)
    # Di sini Anda akan menambahkan library seperti SciPy atau PyBullet
    response = AIMessage(content="[Science] Hasil eksperimen tersedia.")
    return {"messages": [response]}


def mathematics_agent(state: UniverseState):
    print("[Mathematics Agent] Memecahkan masalah...")
    # Implementasi Pemecahan Masalah Matematika
    response = AIMessage(content="[Mathematics] Solusi berhasil ditemukan.")
    return {"messages": [response]}


def economy_agent(state: UniverseState):
    print("[Economy Agent] Menganalisis pasar...")
    # Implementasi Analisis Ekonomi
    # Di sini Anda akan menambahkan library seperti Pandas atau Statsmodels
    response = AIMessage(content="[Economy] Analisis pasar selesai.")
    return {"messages": [response]}


def education_agent(state: UniverseState):
    print("[Education Agent] Membantu belajar...")
    # Implementasi Pendidikan
    # Di sini Anda akan menambahkan library seperti TensorFlow atau Keras
    response = AIMessage(content="[Education] Materi pelajaran tersedia.")
    return {"messages": [response]}


def entertainment_agent(state: UniverseState):
    print("[Entertainment Agent] Merekomendasikan konten...")
    # Implementasi Hiburan
    # Di sini Anda akan menambahkan library seperti OpenCV atau Pygame
    response = AIMessage(content="[Entertainment] Rekomendasi konten tersedia.")
    return {"messages": [response]}


def healthcare_agent(state: UniverseState):
    print("[Healthcare Agent] Menganalisis data medis...")
    response = AIMessage(content="[Healthcare] Analisis medis selesai.")
    return {"messages": [response]}


def legal_agent(state: UniverseState):
    print("[Legal Agent] Menganalisis dokumen hukum...")
    response = AIMessage(content="[Legal] Analisis hukum selesai.")
    return {"messages": [response]}


def cybersecurity_agent(state: UniverseState):
    print("[Cybersecurity Agent] Memeriksa kerentanan keamanan...")
    response = AIMessage(content="[Cybersecurity] Pengecekan keamanan selesai.")
    return {"messages": [response]}


def creative_agent(state: UniverseState):
    print("[Creative Agent] Membantu desain kreatif...")
    response = AIMessage(content="[Creative] Tugas desain kreatif selesai.")
    return {"messages": [response]}


def devops_agent(state: UniverseState):
    print("[DevOps Agent] Menganalisis infrastruktur...")
    response = AIMessage(content="[DevOps] Tugas infrastruktur selesai.")
    return {"messages": [response]}


def data_engineering_agent(state: UniverseState):
    print("[Data Eng Agent] Memproses pipeline data...")
    response = AIMessage(content="[Data Eng] ETL pipeline selesai.")
    return {"messages": [response]}


def osint_agent(state: UniverseState):
    print("[OSINT Agent] Mengumpulkan data dari sumber terbuka...")
    response = AIMessage(content="[OSINT] Pengumpulan informasi publik selesai.")
    return {"messages": [response]}


def game_ai_agent(state: UniverseState):
    print("[Game AI Agent] Menganalisis sistem game...")
    response = AIMessage(content="[Game AI] Tugas desain game AI selesai.")
    return {"messages": [response]}


def productivity_agent(state: UniverseState):
    print("[Productivity Agent] Mengatur produktivitas harian...")
    response = AIMessage(
        content="[Productivity] Pengaturan tugas produktivitas selesai."
    )
    return {"messages": [response]}


# 5. Membangun Graph (Peta Alur Kerja)
workflow = StateGraph(UniverseState)

# Daftarkan semua node
workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("finance", finance_agent)
workflow.add_node("nlp", nlp_agent)
workflow.add_node("science", science_agent)
workflow.add_node("mathematics", mathematics_agent)
workflow.add_node("economy", economy_agent)
workflow.add_node("education", education_agent)
workflow.add_node("entertainment", entertainment_agent)
workflow.add_node("healthcare", healthcare_agent)
workflow.add_node("legal", legal_agent)
workflow.add_node("cybersecurity", cybersecurity_agent)
workflow.add_node("creative", creative_agent)
workflow.add_node("devops", devops_agent)
workflow.add_node("data_engineering", data_engineering_agent)
workflow.add_node("osint", osint_agent)
workflow.add_node("game_ai", game_ai_agent)
workflow.add_node("productivity", productivity_agent)

# Tentukan titik awal
workflow.add_edge(START, "Supervisor")

# Logika Percabangan (Routing)
workflow.add_conditional_edges(
    "Supervisor",
    lambda state: state.next_agent,  # Lihat hasil keputusan Supervisor
    {
        "finance": "finance",
        "nlp": "nlp",
        "science": "science",
        "mathematics": "mathematics",
        "economy": "economy",
        "education": "education",
        "entertainment": "entertainment",
        "healthcare": "healthcare",
        "legal": "legal",
        "cybersecurity": "cybersecurity",
        "creative": "creative",
        "devops": "devops",
        "data_engineering": "data_engineering",
        "osint": "osint",
        "game_ai": "game_ai",
        "productivity": "productivity",
    },
)

# Setelah agen pekerja selesai, kembalikan ke END (atau bisa kembali ke Supervisor)
workflow.add_edge("finance", END)
workflow.add_edge("nlp", END)
workflow.add_edge("science", END)
workflow.add_edge("mathematics", END)
workflow.add_edge("economy", END)
workflow.add_edge("education", END)
workflow.add_edge("entertainment", END)
workflow.add_edge("healthcare", END)
workflow.add_edge("legal", END)
workflow.add_edge("cybersecurity", END)
workflow.add_edge("creative", END)
workflow.add_edge("devops", END)
workflow.add_edge("data_engineering", END)
workflow.add_edge("osint", END)
workflow.add_edge("game_ai", END)
workflow.add_edge("productivity", END)

# Compile Graph menjadi aplikasi yang bisa dijalankan
app = workflow.compile()

# ==========================================
# 6. BLOK PENGUJIAN LOKAL
# ==========================================
if __name__ == "__main__":
    print("=== UIS-OTAK AI ROUTER AKTIF ===")
    while True:
        user_input = input("\nMasukkan perintah Anda (ketik 'exit' untuk keluar): ")
        if user_input.lower() == "exit":
            break

        # Masukkan input pengguna ke dalam state
        initial_state = UniverseState(messages=[HumanMessage(content=user_input)])

        # Jalankan LangGraph
        result = app.invoke(initial_state)

        # Tampilkan hasil akhir
        print(f"\nJawaban Akhir: {result['messages'][-1].content}")
