# Entegre Ajanlar - RAG ile CrewAI

RAG (Retrieval-Augmented Generation) sistemini CrewAI ajanlarıyla entegre etme.

## 🎯 Genel Bakış

Bu modül, Qdrant vektör veritabanı ile CrewAI ajanlarını birleştirerek bilgi tabanı destekli akıllı ajanlar oluşturmayı gösterir.

## 📁 Dosyalar

```
04-integrated-agents/
├── README.md              # Bu dosya
├── 01_rag_agent.py       # RAG entegreli CrewAI ajanı
└── success_output.txt    # Test çıktısı örneği
```

## 🚀 Çalıştırma

### Ön Koşullar

1. **Qdrant çalışıyor olmalı:**
```bash
cd ..
docker compose up -d
```

2. **Bilgi tabanı dolu olmalı:**
```bash
cd ../03-embeddings-rag
python 03_ingestion.py
```

3. **Bağımlılıklar yüklü olmalı:**
```bash
pip install crewai qdrant-client requests
```

### RAG Ajanını Çalıştır

```bash
python 01_rag_agent.py
```

## 🏗️ Mimari

```
Kullanıcı Sorusu
    ↓
[CrewAI Ajanı]
    ↓
[KnowledgeBaseTool]
    ↓
[Qdrant Vektör VT] ← Semantik Arama
    ↓
[Qwen3:8b LLM] ← Bağlam ile Cevap Oluştur
    ↓
Kullanıcıya Cevap
```

## 🔧 Özellikler

- ✅ Qdrant vektör veritabanı entegrasyonu
- ✅ Semantik arama ile bilgi getirme
- ✅ CrewAI ajan framework'ü
- ✅ Ollama LLM (qwen3:8b)
- ✅ Bilgi tabanı destekli cevaplar

## 📚 Detaylı Dokümantasyon

Tam dokümantasyon için İngilizce README'ye bakın.

---

**Hazır mısınız?** `python 01_rag_agent.py` komutunu çalıştırın! 🤖
