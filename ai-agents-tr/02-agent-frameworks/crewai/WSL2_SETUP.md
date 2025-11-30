# Windows'ta WSL2 ile CrewAI Kurulumu

## Neden WSL2?

CrewAI, hafıza özellikleri için ChromaDB kullanır ve bu da yerel Windows'ta yüklenmesi zor olan C++ derleme araçlarını gerektirir. WSL2, Windows üzerinde tam bir Linux ortamı sağlayarak kurulumu sorunsuz hale getirir ve tüm CrewAI özelliklerine erişmenizi sağlar.

## Ön Koşullar

- Windows 10 sürüm 2004+ veya Windows 11
- Yönetici erişimi
- ~2 GB boş disk alanı

## Hızlı Kurulum

### 1. WSL2'yi Yükleyin

PowerShell'i Yönetici olarak açın:

```powershell
wsl --install
```

Bu, varsayılan olarak Ubuntu'yu yükler. İstendiğinde **bilgisayarınızı yeniden başlatın**.

### 2. İlk Ubuntu Kurulumu

Yeniden başlattıktan sonra Ubuntu otomatik olarak açılacaktır:
- Bir kullanıcı adı oluşturun (küçük harf, boşluk yok)
- Bir şifre oluşturun (yazarken görmeyeceksiniz)

### 3. Ubuntu'yu Güncelleyin

```bash
sudo apt update && sudo apt upgrade -y
```

### 4. Python ve Bağımlılıkları Yükleyin

```bash
# Python 3.11'i yükleyin
sudo apt install python3.11 python3.11-venv python3-pip -y

# Derleme araçlarını yükleyin (ChromaDB için)
sudo apt install build-essential -y
```

### 5. WSL2 içinde Ollama'yı Yükleyin

```bash
# Ollama'yı yükleyin
curl -fsSL https://ollama.com/install.sh | sh

# Ollama'yı arka planda başlatın
ollama serve > /dev/null 2>&1 &

# Modeli çekin
ollama pull qwen3:8b
```

### 6. Projenize Gidin

WSL2, Windows dosyalarına `/mnt/` üzerinden erişebilir:

```bash
# Projenize gidin (gerekirse sürücü harfini ayarlayın)
cd /mnt/d/workspace/all-about-ai/ai-agents/02-agent-frameworks/crewai
```

### 7. Sanal Ortam Oluşturun

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 8. CrewAI'ı Yükleyin

```bash
pip install crewai crewai-tools langchain-ollama
```

### 9. Örnekleri Çalıştırın

```bash
python 01_simple_crew.py
```

🎉 **İşiniz bitti!** Hafıza dahil tüm CrewAI özellikleri mükemmel şekilde çalışacaktır.

---

## Alternatif: WSL2'den Windows Ollama'yı Kullanın

Windows'ta zaten çalışan Ollama'nız varsa, buna WSL2'den erişebilirsiniz:

### Windows IP'nizi Bulun

WSL2'de:
```bash
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
```

Bu, Windows IP'nizi gösterir (genellikle `172.x.x.x`)

### Betikleri Güncelleyin

Betiklerdeki `base_url`'i değiştirin:

```python
llm = ChatOllama(
    model="qwen3:8b",
    base_url="http://172.x.x.x:11434",  # Windows IP'niz
    temperature=0.7
)
```

Veya ortam değişkeni ayarlayın:
```bash
export OLLAMA_HOST=http://$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):11434
```

---

## İpuçları & Püf Noktaları

### VS Code'dan WSL2'ye Erişim

1. VS Code'da "WSL" eklentisini yükleyin
2. Komut Paletini açın (Ctrl+Shift+P)
3. "WSL: Connect to WSL" yazın
4. Proje klasörünüzü açın

### Ollama'yı Otomatik Başlatma

`~/.bashrc` dosyasına ekleyin:

```bash
# Ollama çalışmıyorsa başlat
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve > /dev/null 2>&1 &
fi
```

Sonra: `source ~/.bashrc`

### Daha İyi Performans: WSL2 İçine Klonlayın

Daha hızlı dosya erişimi için repoyu WSL2 içine klonlayın:

```bash
cd ~
git clone https://github.com/beyhanmeyrali/all-about-ai.git
cd all-about-ai/ai-agents/02-agent-frameworks/crewai
```

### Dosya İzin Sorunları

İzin hataları alırsanız:

```bash
sudo chown -R $USER:$USER /mnt/d/workspace/all-about-ai
```

---

## Sorun Giderme

### "wsl --install" bulunamadı

**Çözüm:** Windows Update ile Windows'u en son sürüme güncelleyin

### Ollama bağlantısı reddedildi

**Çözüm:** Ollama'nın çalıştığından emin olun:
```bash
ollama serve > /dev/null 2>&1 &
```

### ChromaDB kurulumu başarısız

**Çözüm:** Derleme araçlarını yükleyin:
```bash
sudo apt install build-essential python3-dev -y
```

### /mnt/ üzerinden yavaş dosya erişimi

**Çözüm:** Windows dosyalarına erişmek yerine depoyu WSL2 içine klonlayın

### WSL2 çok fazla bellek kullanıyor

**Çözüm:** Windows kullanıcı klasöründe `.wslconfig` oluşturun:
```
[wsl2]
memory=4GB
processors=2
```

---

## Doğrulama

Kurulumunuzu test edin:

```bash
# Python'ı kontrol et
python3 --version

# CrewAI'ı kontrol et
python3 -c "import crewai; print('CrewAI:', crewai.__version__)"

# Ollama'yı kontrol et
curl http://localhost:11434/api/tags

# Bir test betiği çalıştır
python 00_crew_basics.py
```

Hepsi hatasız çalışmalıdır! 🚀
