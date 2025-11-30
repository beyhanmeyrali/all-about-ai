# Kişisel Uzaktan Geliştirme Sunucunuz

## Özet (Deneyimli Geliştiriciler İçin)

**Nedir:** WSL2 + Tailscale VPN + tmux + VS Code Server = Yerel donanımınızda kişisel bulut geliştirme ortamınız

**Neden:** Kalıcı tmux oturumlarında birden fazla yapay zeka kodlama ajanı (Claude Code, Copilot CLI, Gemini CLI) çalıştırın. Güvenli VPN aracılığıyla her yerden (telefon, iPad, dizüstü bilgisayar) erişin. Port yönlendirme yok, bulut maliyeti yok, GPU hızlandırmalı yapay zeka iş yükleri.

**Yığın:**
```bash
WSL2 Ubuntu → SSH (uzak terminal) + Tailscale (sıfır yapılandırmalı VPN)
            → tmux (kalıcı oturumlar) + VS Code Server (web IDE)
            → Docker + vLLM/Ollama (yerel YZ modelleri) + Qdrant (vektör veritabanı)
            → NVIDIA GPU passthrough (YZ hızlandırma)
```

**Kullanım Senaryosu:** Evde farklı projeler üzerinde çalışan 5 yapay zeka ajanı başlatın, öğle yemeğinde telefondan ilerlemeyi kontrol edin, kanepede iPad'den kodlayın, hepsi şifreli VPN ağı üzerinden. Bağlantınız kopsa bile ajanlar 7/24 çalışmaya devam eder.

**Kurulum Süresi:** 5-10 dakika | **Maliyet:** 0$ (donanımınızda çalışır) | **Güvenlik:** Sadece VPN, açık port yok

**Hızlı Başlangıç:** `wsl --install Ubuntu` → Tailscale Kur → systemd'yi Etkinleştir → Bitti

---

## Oyun Değiştirici: 7/24 Çalışan, Her Yerden Yönetilen Yapay Zeka Kodlama Ajanları

> **Bu Kurulum Neden Önemli:** Kalıcı tmux oturumlarında çalışan yapay zeka kodlama ajanları (Claude Code, GitHub Copilot CLI, Gemini CLI) ile, **kodlama görevleri atayabilir ve siz uzaktayken çalışmalarını sağlayabilirsiniz**. Öğle yemeğinde telefonunuzdan ilerlemeyi kontrol edin, kanepede tabletinizden kodu inceleyin, herhangi bir cihazdan yeni görevler verin. Yapay zeka ajanları olmadan, kod yazmak için bilgisayarınızın başında olmanız gerekirdi. Bu kurulumla, yapay zeka ajanları sizin için kod yazarken siz sadece yönlendirir, inceler ve test edersiniz—**dünyanın her yerinden**.

> **Tüm Geliştiriciler İçin:** Web uygulamaları, arka uç hizmetleri, mobil uygulamalar, yapay zeka modelleri—bağlantı kopmalarına dayanıklı kalıcı oturumlarla aynı anda birden fazla proje üzerinde çalışın. Sıfır devam eden maliyetle kişisel bulut altyapınız.

**Oluşturan:** [Beyhan MEYRALI](https://www.linkedin.com/in/beyhanmeyrali/)


## İçindekiler

### Hızlı Başlangıç
- [Genel Bakış](#genel-bakış)
- [Hızlı Başlangıç (5 Dakika)](#hızlı-başlangıç-5-dakika) ⭐ **Buradan başlayın!**

### Kurulumu Anlamak
- [Ne İnşa Ediyoruz?](#ne-inşa-ediyoruz)
- [Mimari](#mimari)
- [Neden Bu Kurulum?](#neden-bu-kurulum)
- [Bileşenler Açıklaması](#bileşenler-açıklaması)
- [Öğrenme Yolu](#öğrenme-yolu)

### Kurulum
- [Sistem Bilgisi](#sistem-bilgisi)
- [⚠️ KRİTİK: WSL IP Değişiklikleri](#kritik-her-yeniden-başlatmada-wsl-ip-adresi-değişiklikleri)
- [İlk WSL Kurulumu](#ilk-wsl-kurulumu)
- [Root Olarak Çalışmak](#root-kullanıcısı-olarak-çalışmak-sudodan-kaçınmak)
- [Tam Kurulum Rehberi](#tam-kurulum-rehberi-adım-adım) ⭐ **Bunu takip edin!**
- [Yüklü Paketler](#yüklü-paketler)
- [WSL'e Uzaktan Erişim](#wsle-uzaktan-erişim)
- [Otomatik Servis Başlatma](#otomatik-servis-başlatma)
- [Kurulumunuzu Doğrulayın](#kurulumunuzu-doğrulayın) ✅ **Her şeyi test edin!**

### İleri Düzey Kurulum
- [Gelecek Kurulumlar](#gelecek-kurulumlar-yapılacaklar)
- [WSL Yapılandırma İpuçları](#wsl-yapılandırma-ipuçları)
- [Yedekleme ve Dışa Aktarma](#yedekleme-ve-dışa-aktarma)

### Referans
- [Sorun Giderme](#sorun-giderme)
- [Faydalı Komutlar](#faydalı-komutlar)
- [Ek Kaynaklar](#ek-kaynaklar)

---

## Genel Bakış

Bu rehber, Windows makinenizde WSL2 (Linux için Windows Alt Sistemi) kullanarak çalışan **profesyonel bir uzaktan geliştirme sunucusu** oluşturmanıza yardımcı olacaktır. Sonunda şunlara sahip olacaksınız:

✅ Windows üzerinde tam bir Linux geliştirme ortamı
✅ **Sıfır ağ karmaşıklığı** ile **her yerden** erişim (port yönlendirme yok, yönlendirici yapılandırması yok, statik IP gerekmez!)
✅ Tailscale VPN sayesinde **herhangi bir ağda** çalışır (kafe WiFi, otel, hücresel veri)
✅ Bağlantı kopmalarına dayanıklı kalıcı oturumlar—dizüstü bilgisayarınızı kapatın ve kaldığınız yerden devam edin
✅ Aynı anda çalışan birden fazla proje (ön uç, arka uç, mobil, ML boru hatları)
✅ Profesyonel geliştirme araçları (VS Code Server, tmux, SSH, Docker)
✅ **5 dakikalık kurulum** - Yükle, çalıştır, bağlan. Ağ uzmanlığı gerekmez.
✅ İsteğe bağlı: YZ/ML iş yükleri için GPU hızlandırma

**Bu kimin için?**
- **Web Geliştiricileri** - Aynı anda birden fazla React, Node.js veya Python projesi çalıştırın
- **Arka Uç Geliştiricileri** - Mikro hizmetleri, veritabanlarını ve API'leri tek bir yerden yönetin
- **Mobil Geliştiriciler** - Tam IDE erişimi ile uygulamaları uzaktan oluşturun ve test edin
- **Öğrenciler & Öğrenenler** - Herhangi bir cihazdan kodlama pratiği yapın, projeleri 7/24 çalışır durumda tutun
- **DevOps Mühendisleri** - Konteynerleri yönetin, dağıtımları test edin, CI/CD boru hatlarını çalıştırın
- **YZ/ML Geliştiricileri** - Modelleri eğitin, çıkarım sunucularını çalıştırın, veri boru hatlarını yönetin
- **Herkes** - Birden fazla cihazdan kodlamak veya çalışma oturumlarını canlı tutmak isteyen herkes

---

## Hızlı Başlangıç (5 Dakika)

**Hemen çalıştırmak mı istiyorsunuz?** İşte ekspres yol:

```bash
# 1. WSL2'yi Ubuntu ile yükleyin (Yönetici olarak PowerShell)
wsl --install Ubuntu

# 2. İstendiğinde root şifresini ve kullanıcı şifrenizi belirleyin

# 3. Ubuntu içinde, systemd'yi etkinleştirin
sudo nano /etc/wsl.conf
# Şu satırları ekleyin:
# [boot]
# systemd=true
# Kaydet (Ctrl+O, Enter, Ctrl+X)

# 4. WSL'i yeniden başlatın (PowerShell'den)
wsl --shutdown

# 5. Ubuntu'ya geri dönün, şifresiz sudo ayarlayın
sudo visudo
# Sona ekleyin: username ALL=(ALL) NOPASSWD:ALL
# (username kısmını kendi kullanıcı adınızla değiştirin)

# 6. Sistemi güncelleyin ve temel servisleri yükleyin
sudo apt update && sudo apt upgrade -y
sudo apt install -y openssh-server tmux

# 7. Tailscale yükleyin (uzaktan erişim için)
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --ssh

# 8. VS Code Server yükleyin
curl -fsSL https://code-server.dev/install.sh | sh

# 9. Servislerin açılışta başlamasını etkinleştirin
sudo systemctl enable ssh
sudo systemctl enable tailscaled

# 10. Her şeyin çalıştığını doğrulayın
sudo systemctl status ssh
tailscale status
tmux -V
code-server --version
```

**Bu kadar!** Artık şunlara sahipsiniz:
- ✅ Uzak terminal erişimi için SSH sunucusu
- ✅ Her yerden güvenli erişim için Tailscale
- ✅ Kalıcı oturumlar için tmux
- ✅ Tarayıcı tabanlı IDE için VS Code Server

**Sonraki adımlar:**
- [Tailscale kimlik doğrulamasını tamamlayın](#1-tailscale-vpnmesh-ağı) (gösterilen URL'yi ziyaret edin)
- [VS Code Server'ı yapılandırın](#4-vs-code-server-web-tabanlı-ide) (şifre belirleyin)
- [Port yönlendirmeyi ayarlayın](#wsle-uzaktan-erişim) (Tailscale kullanmıyorsanız)
- [Kurulumunuzu doğrulayın](#kurulumunuzu-doğrulayın) (tüm bileşenleri test edin)

Her bileşenin ne işe yaradığı ve neden gerekli olduğu hakkında ayrıntılı açıklamalar için aşağıyı okumaya devam edin.

---

## Ne İnşa Ediyoruz?

Windows PC'nizde çalışan ancak her yerden erişilebilen bir **uzaktan geliştirme sunucusu** oluşturuyoruz. Bunu kişisel bulut geliştirme ortamınız olarak düşünün, ancak kendi donanımınızda çalışıyor.

### Büyük Resim

```
┌─────────────────────────────────────────────────────────────────┐
│                        WINDOWS BİLGİSAYARINIZ                   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              WSL2 (Ubuntu Linux)                       │   │
│  │                                                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────────┐    │   │
│  │  │   SSH    │  │   tmux   │  │  VS Code Server │    │   │
│  │  │ (Uzaktan │  │ (Oturum  │  │  (Web Tarayıcı) │    │   │
│  │  │  Erişim) │  │ Yöneticisi)││                 │    │   │
│  │  └────┬─────┘  └────┬─────┘  └────────┬────────┘    │   │
│  │       │             │                  │              │   │
│  │  ┌────┴─────────────┴──────────────────┴─────────┐   │   │
│  │  │        Kodlarınız & YZ Modelleriniz           │   │   │
│  │  │  • Python Projeleri  • Docker Konteynerleri   │   │   │
│  │  │  • vLLM (YZ Modelleri) • Qdrant (Vektör VT)   │   │   │
│  │  └────────────────┬──────────────────────────────┘   │   │
│  │                   │                                   │   │
│  │              ┌────┴─────┐                            │   │
│  │              │   GPU    │  ← Donanım Hızlandırma     │   │
│  │              │  Erişimi │                            │   │
│  │              └──────────┘                            │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │              Tailscale (VPN Mesh)                    │     │
│  │           (Her yerden güvenli erişim)                │     │
│  └────────────────┬─────────────────────────────────────┘     │
└───────────────────┼─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │ Laptop │  │ Telefon│  │  iPad  │
    │  SSH   │  │Terminal│  │VS Code │
    │  tmux  │  │veya Web│  │  Web   │
    └────────┘  └────────┘  └────────┘
```

### Pratikte Bu Ne Anlama Geliyor

**Önce:** Masanızdasınız, Windows PC'nizde tüm YZ modelleriniz ve kodlarınızla çalışıyorsunuz.

**Sonra:** Kanepede iPad'inizle aynı çalışmaya tam bir VS Code ortamında devam ediyorsunuz veya bir kafede telefonunuzdan SSH aracılığıyla model eğitim ilerlemenizi kontrol ediyorsunuz.

### 🚀 Gerçek Güç: Aynı Anda Çalışan Birden Fazla Yapay Zeka Ajanı

İşte bu kurulumun sağladığı **oyun değiştiren iş akışı**:

```
Ev Sunucunuz (7/24 Çalışıyor)
│
├── tmux oturumu 1: "frontend"
│   └── Claude Code React uygulaması üzerinde çalışıyor
│
├── tmux oturumu 2: "backend"
│   └── GitHub Copilot CLI Python API'sini kodluyor
│
├── tmux oturumu 3: "mobile"
│   └── Gemini CLI Flutter uygulaması geliştiriyor
│
├── tmux oturumu 4: "ml-pipeline"
│   └── Qwen CLI veri boru hatları oluşturuyor
│
└── tmux oturumu 5: "training"
    └── vLLM özel bir modeli eğitiyor
```

**Dünyanın her yerinden siz:**
```bash
# Bir kafede telefonunuzdan
ssh user@home-via-tailscale

# Çalışan tüm projeleri kontrol et
tmux ls
  0: frontend (Claude Code aktif)
  1: backend (GitHub Copilot aktif)
  2: mobile (Gemini CLI aktif)
  3: ml-pipeline (Qwen CLI aktif)
  4: training (model eğitimi %67 tamamlandı)

# Herhangi bir oturuma bağlan
tmux attach -t frontend  # Claude'un ne yaptığını gör
tmux attach -t backend   # Copilot'un ilerlemesini kontrol et

# Yeni bir projede yeni bir YZ ajanı başlat
tmux new -s website
claude "bana bir portfolyo web sitesi yap"
# Ayır (Ctrl+B, D) - Claude çalışmaya devam eder!

# iPad'inizde tarayıcıda VS Code Server'ı açın
# Erişim: http://tailscale-ip:8080
# Tüm eklentilerle tam VS Code, tüm projeleri düzenleme
```

**Bu Neden Devrim Niteliğinde:**

1. **Tek Sunucuda Birden Fazla YZ Ajanı**
   - Aynı anda 5+ farklı YZ kodlama aracı çalıştırın
   - Her biri kendi tmux oturumunda
   - Her biri farklı projeler üzerinde çalışıyor
   - Hepsine her yerden erişilebilir

2. **Port Yönlendirme Gerekmez**
   - **Tailscale** güvenli bir VPN ağı oluşturur
   - Sunucunuz ev güvenlik duvarınızın arkasında kalır
   - Her yerden erişim: kafe, tatil, telefon
   - Yönlendirici yapılandırması gerekmez

3. **Kalıcı Oturumlar (tmux)**
   - Dizüstü bilgisayarınızı kapatın → YZ ajanları çalışmaya devam eder
   - İnternet bağlantısını kaybedin → Projeler devam eder
   - Cihaz değiştirin → Kaldığınız yerden aynen devam edin
   - YZ ajanları karmaşık görevlerde saatlerce/günlerce çalışabilir

4. **Web Tabanlı IDE (VS Code Server)**
   - Tarayıcınızda tam VS Code
   - İstemci cihazlarda kurulum yok
   - iPad, Chromebook, tarayıcısı olan herhangi bir cihazda çalışır
   - Tüm eklentiler: Claude Code, Copilot, hata ayıklayıcılar

---

## Mimari

Mimarisi basitten karmaşığa üç katmana ayıralım.

### Seviye 1: Temel Kurulum (Başlangıç)

```
Windows (Ana Bilgisayar)
    └── WSL2 (Ubuntu Linux)
            ├── Kod Dosyalarınız
            └── Geliştirme Araçları
```

En basit seviyede, WSL2 sadece Windows içinde çalışan Linux'tur. Windows üzerinde gerçek bir Ubuntu terminaline sahip olursunuz.

### Seviye 2: Uzaktan Erişim (Orta Seviye)

```
Windows PC
    └── WSL2 Ubuntu
            ├── SSH Sunucusu (Port 22) ──────┐
            │   "Uzaktan bağlantıları kabul et" │
            │                                │
            ├── VS Code Server (Port 8080) ─┤
            │   "Web tabanlı IDE"            │
            │                                │
            └── Tailscale ──────────────────┤
                "Güvenli erişim için VPN"    │
                                             │
        ┌────────────────────────────────────┘
        │ İnternet / Yerel Ağ
        │
        ▼
   Diğer Cihazlar
   (Telefon, Tablet, Başka PC)
```

Artık geliştirme ortamınıza diğer cihazlardan şunları kullanarak bağlanabilirsiniz:
- **SSH** - Terminal erişimi (tmux, CLI araçları için)
- **VS Code Server** - Tarayıcınızda tam IDE
- **Tailscale** - Güvenli VPN bağlantısı

### Seviye 3: Üretim YZ Geliştirme (İleri Seviye)

```
┌──────────────── GELİŞTİRME SUNUCUNUZ ─────────────────┐
│                                                           │
│  Erişim Katmanı (Nasıl bağlanırsınız)                    │
│  ├── Tailscale (Güvenli VPN)                             │
│  ├── SSH (Port 2222) ← Terminal erişimi                  │
│  └── VS Code Server (Port 8080) ← Web IDE                │
│                                                           │
│  Oturum Yönetimi                                          │
│  └── tmux (Bağlantı kopsa bile süren kalıcı oturumlar)   │
│                                                           │
│  Uygulama Katmanı                                         │
│  ├── Python/Node.js (Kodunuz)                            │
│  ├── vLLM (Llama, Mistral gibi YZ modellerini çalıştır)  │
│  ├── Ollama (Kolay YZ model yönetimi)                    │
│  └── Docker (Konteynerleştirilmiş servisler)             │
│                                                           │
│  Veri Katmanı                                             │
│  ├── Qdrant (YZ embeddingleri için vektör veritabanı)    │
│  ├── Proje dosyalarınız                                  │
│  └── Model ağırlıkları                                   │
│                                                           │
│  Donanım Katmanı                                          │
│  └── NVIDIA GPU (YZ için donanım hızlandırma)            │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

Bu, uzaktan erişimli profesyonel YZ geliştirme için tam yığındır.

---

## Neden Bu Kurulum?

Her kararın arkasındaki "neden"i açıklayalım:

### Neden normal bir VM yerine WSL2?

| Özellik | WSL2 | Geleneksel VM |
|---------|------|---------------|
| **Performans** | Neredeyse yerel hız | Daha yavaş (tam emülasyon) |
| **Kaynak Kullanımı** | Hafif | Ağır (tam işletim sistemi yükü) |
| **Başlangıç Süresi** | Anında | 30-60 saniye |
| **Dosya Erişimi** | Kolay (Windows ↔ Linux) | Karmaşık (ağ paylaşımları) |
| **GPU Erişimi** | Yerleşik destek | Karmaşık kurulum |

**Sonuç**: WSL2, sanal makine yükü olmadan size tam bir Linux ortamı sunar.

### Neden port yönlendirme yerine Tailscale?

**Kritik Fark: Ev Sunucunuz Evde Kalır**

**Port Yönlendirme** (Geleneksel yaklaşım):
- ⚠️ PC'nizi internete açar (güvenlik riski!)
- ⚠️ Yönlendirici yapılandırması gerektirir (bazı ağlarda mümkün değildir)
- ⚠️ Ağ değiştirdiğinizde bozulur (dizüstü bilgisayarı kafeye götüremezsiniz)
- ⚠️ Sabit IP adresi gerekir (para maliyeti)
- ⚠️ Güvenlik duvarı yapılandırma kabusu

**Tailscale** (Modern yaklaşım):
- ✅ **Sıfır yapılandırmalı güvenli VPN** - Yükle ve kullan
- ✅ **Herhangi bir güvenlik duvarı/NAT arkasında çalışır** - Kafe, otel, uçak WiFi
- ✅ **Varsayılan olarak şifreli** - WireGuard protokolü
- ✅ **Açık port yok** - Saldırganlara görünür hiçbir şey yok
- ✅ **Her yerden çalışır** - Ev IP'niz değişse bile
- ✅ **Mesh ağı** - Tüm cihazlarınız birbiriyle konuşabilir

### Neden tmux?

**Birden Fazla YZ Ajanının Anahtarı: Kalıcı Oturumlar**

**tmux olmadan**:
```
SSH Bağlantısı → Claude Code Başlat → Bağlantı kopar → Claude durur ❌
Bağlantınız kesildiğinde tüm YZ ajanlarınız ölür ❌
```

**tmux ile**:
```
SSH → tmux oturumu 1 → Claude Code Başlat → Bağlantı kopar → Claude devam eder ✓
SSH → tmux oturumu 2 → GitHub Copilot Başlat → Bağlantı kopar → Copilot devam eder ✓
...
Tekrar SSH → tmux ls → TÜM ajanların hala çalıştığını gör ✓
```

### Neden VS Code Server?

**Web Tabanlı IDE = Kelimenin Tam Anlamıyla Her Yerden Kodlama**

tmux + SSH, CLI tabanlı YZ ajanları için mükemmel olsa da, VS Code Server size web tarayıcınızda **tam grafiksel bir IDE** sunar.

**Ne Elde Edersiniz:**
- **Tam VS Code** - Sınırlı bir sürüm değil, GERÇEK VS Code
- **Tüm Eklentiler Çalışır** - Claude Code, GitHub Copilot, hata ayıklayıcılar, temalar
- **Tarayıcı Tabanlı** - İstemci cihazda kurulum gerekmez
- **Dokunmatik Dostu** - Klavyeli iPad'de harika çalışır
- **Herhangi Bir Cihaz** - Chromebook, tablet, telefon (hızlı düzenlemeler için)

---

## Bileşenler Açıklaması

### 🟢 Seviye 1: Temel Bileşenler

#### 1. WSL2 (Linux için Windows Alt Sistemi)
**Nedir**: Sanal makine olmadan Windows üzerinde gerçek Linux çalıştırmanın bir yolu.
**Analoji**: Windows PC'nizin içinde ikinci bir bilgisayar varmış gibi düşünün, ama aslında Linux.

#### 2. SSH (Güvenli Kabuk)
**Nedir**: Komut satırını kullanarak bir bilgisayarı uzaktan kontrol etmenin bir yolu.
**Analoji**: Uzak Masaüstü gibi, ancak GUI yerine terminal/komut satırı için.

#### 3. tmux (Terminal Çoklayıcı)
**Nedir**: Bağlantınız kesildikten sonra bile terminal oturumlarınızı çalışır durumda tutan bir araç.
**Analoji**: Tarayıcıyı kapattıktan sonra Chrome sekmelerini açık tutmak gibi düşünün. Chrome'u tekrar açtığınızda sekmeleriniz hala oradadır.

### 🟡 Seviye 2: Geliştirme Araçları

#### 4. VS Code Server (code-server)
**Nedir**: Web tarayıcınızda çalışan tam Visual Studio Code.

#### 5. Tailscale (Sıfır Yapılandırmalı VPN)
**Nedir**: Tüm cihazlarınızı güvenli bir şekilde bağlayan bir mesh VPN.

#### 6. systemd (Servis Yöneticisi)
**Nedir**: Linux'ta arka plan servislerini yöneten sistem.
**Analoji**: Windows Hizmetleri gibi, ancak Linux için.

### 🔴 Seviye 3: YZ/ML Bileşenleri

#### 7. Docker & Docker Compose
**Nedir**: Uygulamaları tüm bağımlılıklarıyla birlikte paketlemenin bir yolu.

#### 8. NVIDIA Container Toolkit
**Nedir**: Docker konteynerlerinin NVIDIA GPU'nuzu kullanmasını sağlar.

#### 9. vLLM (LLM Çıkarım Motoru)
**Nedir**: Büyük dil modellerini (Llama, Mistral gibi) çalıştırmak için optimize edilmiş yazılım.

#### 10. Ollama (Kolay LLM Yönetimi)
**Nedir**: YZ modellerini yerel olarak çalıştırmak için kullanıcı dostu bir araç.

#### 11. Qdrant (Vektör Veritabanı)
**Nedir**: YZ embeddingleri ve benzerlik araması için optimize edilmiş bir veritabanı.

---

## Sistem Bilgisi

- **Oluşturulma Tarihi**: 24 Kasım 2025
- **WSL Sürümü**: 2
- **Dağıtım**: Ubuntu 24.04 LTS
- **Root Şifresi**: ubuntu

## Donanım Özellikleri

- **CPU**: AMD Ryzen AI 9 365 w/ Radeon 880M
- **GPU**:
  - NVIDIA GeForce RTX 5060 Laptop GPU (ayrılmış)
  - AMD Radeon 880M Graphics (entegre)

---

## ⚠️ KRİTİK: Her Yeniden Başlatmada WSL IP Adresi Değişiklikleri

**Bu, kullanıcıların karşılaştığı 1 numaralı sorundur - dikkatlice okuyun!**

### Sorun

Windows'u her yeniden başlattığınızda veya WSL'i kapattığınızda, Ubuntu örneğinize Windows tarafından **yeni bir dahili IP adresi** atanır (örneğin, `172.24.x.x` → `172.29.x.x`).

**Ne bozulur:**
- ❌ Port yönlendirme kuralları çalışmayı durdurur
- ❌ Diğer cihazlardan gelen SSH bağlantıları başarısız olur
- ❌ VS Code Server erişilemez hale gelir
- ❌ Kaydedilen IP adresleri geçersiz olur

### Çözümler (Birini Seçin)

#### Seçenek A: Tailscale Kullanın (Önerilen)

**En iyi çözüm** - Makineniz asla değişmeyen kalıcı bir sanal IP alır.

#### Seçenek B: Otomatik Güncellenen Port Yönlendirme Komut Dosyası

Açılışta çalışan bir Windows Görev Zamanlayıcı görevi oluşturun.

#### Seçenek C: Yeniden Başlatma Sonrası Manuel Kontrol

Tailscale veya otomasyon kullanmıyorsanız, her yeniden başlatmadan sonra IP'nizi manuel olarak kontrol edin.

---

## Tam Kurulum Rehberi (Adım Adım)

Bu bölüm, tüm kurulum adımlarını doğru sırayla birleştirir. Sorunsuz bir kurulum deneyimi için bunu takip edin.

### Ön Koşullar Kontrol Listesi

Başlamadan önce şunlara sahip olduğunuzdan emin olun:
- ✅ Yönetici erişimine sahip Windows 10/11
- ✅ ~10 GB boş disk alanı
- ✅ İnternet bağlantısı
- ✅ 30-60 dakika zaman

### Aşama 0: İlk WSL Kurulumu (10 dakika)

**Adım 1: WSL2'yi Ubuntu ile Yükleyin**
```powershell
# Yönetici olarak PowerShell'de
wsl --install Ubuntu
```

**Adım 2: Şifreleri Belirleyin**
- İstendiğinde kullanıcı hesabınızı oluşturun
- Güçlü bir şifre belirleyin
- Bu şifreyi unutmayın!

**Adım 3: systemd'yi Etkinleştirin**
```bash
# Ubuntu terminalinde
sudo nano /etc/wsl.conf

# Şu satırları ekleyin:
[boot]
systemd=true

# Kaydet: Ctrl+O, Enter, Ctrl+X
```

**Adım 4: WSL'i Yeniden Başlatın**
```powershell
# PowerShell'de
wsl --shutdown
```

**Adım 5: Şifresiz sudo ayarlayın (ŞİDDETLE ÖNERİLİR)**
```bash
# Tekrar Ubuntu'da
sudo visudo

# Sona ekleyin ('username' kısmını kendinizinkiyle değiştirin):
username ALL=(ALL) NOPASSWD:ALL

# Kaydet: Ctrl+O, Enter, Ctrl+X
```

### Aşama 1: Temel Servisler (20 dakika)

**Adım 1: Sistemi güncelleyin**
```bash
sudo apt update && sudo apt upgrade -y
```

**Adım 2: SSH Sunucusunu Yükleyin**
```bash
sudo apt install -y openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
```

**Adım 3: tmux Yükleyin**
```bash
sudo apt install -y tmux
```

**Adım 4: Tailscale Yükleyin**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo systemctl enable tailscaled
sudo tailscale up --ssh
```

**Önemli:** Tarayıcıda Tailscale kimlik doğrulamasını tamamlayın (terminaldeki URL'ye bakın)!

**Adım 5: Tailscale IP'nizi alın**
```bash
tailscale ip -4
# Bu IP'yi kaydedin - bu sizin kalıcı adresiniz!
```

### Aşama 2: Geliştirme Araçları (15 dakika)

**Adım 1: VS Code Server Yükleyin**
```bash
curl -fsSL https://code-server.dev/install.sh | sh
```

**Adım 2: Yapılandırma dizini oluşturun**
```bash
mkdir -p ~/.config/code-server
```

**Adım 3: Yapılandırma dosyası oluşturun**
```bash
nano ~/.config/code-server/config.yaml

# Ekle:
bind-addr: 0.0.0.0:8080
auth: password
password: guvenli-sifreniz-buraya
cert: false

# Kaydet: Ctrl+O, Enter, Ctrl+X
```

**Adım 4: systemd servisi oluşturun**
```bash
sudo nano /etc/systemd/system/code-server.service

# Ekle ('username' ve şifreyi değiştirin):
[Unit]
Description=code-server
After=network.target

[Service]
Type=simple
User=username
Environment=PASSWORD=guvenli-sifreniz-buraya
ExecStart=/usr/bin/code-server --bind-addr 0.0.0.0:8080 --auth password
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Kaydet: Ctrl+O, Enter, Ctrl+X
```

**Adım 5: code-server'ı etkinleştirin ve başlatın**
```bash
sudo systemctl daemon-reload
sudo systemctl enable code-server
sudo systemctl start code-server
```

### Aşama 3: İsteğe Bağlı - YZ/ML Yığını (30-60 dakika)

**Yalnızca Docker, GPU desteği veya YZ araçlarına ihtiyacınız varsa bunu yapın.**

[Gelecek Kurulumlar](#gelecek-kurulumlar-yapılacaklar) bölümündeki ayrıntılı talimatlara bakın.

---

## Kurulumunuzu Doğrulayın

Kurulumu tamamladıktan sonra, her şeyin doğru çalıştığından emin olmak için bu testleri çalıştırın.

### ✅ Test 1: SSH Sunucusu
```bash
sudo systemctl status ssh
# Beklenen: "Active: active (running)"
```

### ✅ Test 2: Tailscale VPN
```bash
tailscale status
# Beklenen çıktı: 100.x.x.x ...
```

### ✅ Test 3: tmux
```bash
tmux -V
# Beklenen: tmux 3.x veya daha yeni
```

### ✅ Test 4: VS Code Server
```bash
sudo systemctl status code-server
# Tarayıcıda açın: http://localhost:8080
```

---

## Faydalı Komutlar

### WSL Yönetimi
```powershell
wsl --list --all
wsl --shutdown
```

### Ubuntu Paket Yönetimi
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y <paket>
```

---

## Ek Kaynaklar

- **WSL Dokümantasyonu**: https://learn.microsoft.com/en-us/windows/wsl/
- **Ubuntu Dokümantasyonu**: https://help.ubuntu.com/
- **Docker Dokümantasyonu**: https://docs.docker.com/
- **NVIDIA Container Toolkit**: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/
- **vLLM Dokümantasyonu**: https://docs.vllm.ai/
- **Ollama Dokümantasyonu**: https://github.com/ollama/ollama
- **Qdrant Dokümantasyonu**: https://qdrant.tech/documentation/

---

**Claude Code ile oluşturuldu**
**Son Güncelleme**: 24 Kasım 2025
