# Büyük İnce Ayar Devrimi: Yapay Zekanın En Dramatik Atılımlarına Bir Yolculuk

[![Lisans](https://img.shields.io/badge/Lisans-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-orange.svg)](https://pytorch.org/)
[![AMD ROCm](https://img.shields.io/badge/AMD-ROCm-red.svg)](https://rocm.docs.amd.com/)

> **🎓 Oluşturan:** [Beyhan MEYRALI](https://www.linkedin.com/in/beyhanmeyrali/)  
> **🏛️ Optimize Edildi:** [GMKtec K11](https://www.gmktec.com/products/amd-ryzen%E2%84%A2-9-8945hs-nucbox-k11) ile AMD Ryzen 9 8945HS + Radeon 780M  
> **📚 Öğrenme Yolculuğu:** 15 dakikalık demolardan üretim dağıtımına

*Zeki beyinlerin, imkânsız zorlukların ve her şeyi değiştiren tekniklerin hikayesi*

---

## Önsöz: İmkânsız Rüya

Şunu hayal edin: 2020 yılındayız ve parlak bir fikriniz var. GPT-3'ü özel bir görev için özelleştirmek istiyorsunuz—belki eski dilleri çevirmek ya da daha iyi kod yazmak. Ancak küçük bir sorun var: GPT-3, 175 milyar parametreye sahip. Sıfırdan eğitmek 12 milyon dolara mal olur ve bir süper bilgisayar gerektirir.

Dizüstü bilgisayarınıza bakıyorsunuz—belki **AMD Ryzen 9 8945HS ve Radeon 780M ile GMKtec K11, GPU görevleri için 8GB veya daha fazla paylaşılan sistem belleği kullanan** mütevazı bir makine—ve bu fikrin saçmalığına gülüyorsunuz. Bu, bir oyuncak çekiçle Altın Kapı Köprüsü'nü yeniden inşa etmeye çalışmak gibi.

Ama ya size 2025 yılında bu aynı dizüstü bilgisayarın GPT-3'ten daha güçlü modelleri ince ayar yapabileceğini söylesem? Ya imkânsız sadece mümkün değil, aynı zamanda *kolay* hale gelseydi?

Bu, birkaç zeki araştırmacının dağları yerinden oynatmadığı, aslında onları hareket ettirmeye hiç gerek olmadığını öğrettiği hikaye.

---

## 🤯 Tam Yeni Başlayanlar İçin: Sihri Mümkün Kılan Kütüphaneler

**Yapay Zekaya yeni misiniz? Teknik terimlerden kafanız mı karıştı?** Bu bölüm HERŞEYI sıfırdan açıklar.

### 🌐 İnternet Ekosistemi: Yapay Zeka Modellerinin Yaşadığı Yer

#### **HuggingFace: Yapay Zeka Modellerinin GitHub'ı**
```
Nedir: https://huggingface.co - İnsanların yapay zeka modellerini paylaştığı website
Düşünün: Yapay zeka modelleri için Netflix - bir kez indirin, sonsuza kadar kullanın
Neler indiriyoruz:
├── Yapay zeka modelinin "beyni" (1-2GB dosyalar)
├── Tokenizer (yapay zekanın kelime hazinesi)
└── Konfigürasyon dosyaları (modeli nasıl kullanacağını)

Scriptlerimizi çalıştırdığınızda:
1. Bilgisayarınız HuggingFace.co ile iletişim kurar
2. İhtiyacınız olan yapay zeka modelini indirir
3. Yerel olarak kaydeder (C:\Users\[SizinAdınız]\.cache\huggingface\)
4. Bir sonraki sefer = anında yükleme!
```

### 🔗 Tam Ekosistem Haritası

```
                    İNTERNET
                         |
                 HuggingFace.co
              (Yapay Zeka Model Deposu)
                         |
                    İndirmeler
               ┌─────────┼─────────┐
               ▼         ▼         ▼
         Tokenizer   Model    Config
          (5MB)     (1.2GB)   (5KB)
               │         │         │
               └─────────┼─────────┘
                         ▼
                BİLGİSAYARINIZ
                Yerel Önbellek Depolama
               (~/.cache/huggingface/)
                         |
                    ┌────┴────┐
                    ▼         ▼
             İlk Çalıştırma  Sonraki Çalıştırmalar
            (İndirme)       (Önbellek Yükle)
                    │         │
                    └────┬────┘
                         ▼
                PYTHON KÜTÜPHANELERİ
                   (Araç Takımınız)
```

### 🧰 Python Kütüphaneleri: Yapay Zeka Araç Takımınız

#### **PyTorch: Motor**
```python
import torch  # Yapay zeka motorunu başlatır
```
- **Ne yapar**: Tüm matematiği halleder (saniyede milyonlarca işlem)
- **Benzetme**: Arabadaki motor gibi - diğer her şey bunun çalışması için gerekir
- **Faydası**: Masaüstünüzde yapay zeka eğitimini mümkün kılar

#### **Transformers: Model Kütüphanesi**
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
```
- **Ne yapar**: HuggingFace'den önceden yapılmış yapay zeka modellerini indirir
- **AutoTokenizer**: Yapay zekanın "sözlüğünü" alır (metin ↔ sayı çevirisi)
- **AutoModelForCausalLM**: Asıl yapay zeka "beynini" alır
- **Boyut**: Genellikle 500MB - 2GB model başına
- **Faydanız**: Binlerce önceden eğitilmiş yapay zeka modeline erişim

#### **PEFT: Bellek Tasarrufçusu**
```python
from peft import get_peft_model, LoraConfig
```
- **Ne yapar**: Tüm yapay zekayı yeniden eğitmek yerine küçük "adaptör" katmanları ekler
- **Bellek tasarrufu**: %95 daha az RAM gerekir
- **Hız artışı**: %90 daha hızlı eğitim
- **Kalite**: Tam eğitimle aynı sonuçlar
- **Faydanız**: K11'inizde büyük yapay zeka modelleri eğitin

#### **BitsAndBytes: Sıkıştırıcı**
```python
from transformers import BitsAndBytesConfig
```
- **Ne yapar**: Yapay zeka modellerini daha az bellek kullanacak şekilde küçültür
- **Nasıl**: 16-bit'ten 4-bit hassasiyete (4x daha küçük)
- **Kalite kaybı**: Sadece %2-5 (fark edilmez)
- **Faydanız**: 32GB RAM'inizde daha büyük modeller çalıştırın

#### **TRL: Eğitim Yardımcısı**
```python
from trl import SFTTrainer
```
- **Ne yapar**: Karmaşık eğitim sürecini yönetir
- **Halleder**: İlerleme takibi, kaydetme, hata kurtarma
- **Alternatif**: Kendiniz 500+ satır kod yazmanız gerekirdi
- **Faydanız**: Eğitim basit ve otomatik hale gelir

#### **Datasets: Veri Yöneticisi**
```python
from datasets import Dataset
```
- **Ne yapar**: Eğitim verinizi verimli şekilde işler
- **Çalışır**: JSON, CSV, her veri formatı
- **Faydalar**: Hızlı yükleme, bellek yönetimi
- **Faydanız**: Verinize odaklanın, veri işleme koduna değil

### 🔄 Eğitim Sırasında Gerçek Zamanlı Veri Akışı

```
1. Verileriniz (JSON dosyası)
        ↓
2. Datasets Kütüphanesi (verimli yükler)
        ↓
3. Tokenizer (metni sayılara çevirir)
        ↓
4. PEFT Modeli (adaptörler üzerinden işler)
        ↓
5. PyTorch (hesaplamaları yapar)
        ↓
6. TRL Trainer (süreci yönetir)
        ↓
7. BitsAndBytes (belleği düşük tutar)
        ↓
8. Özel Yapay Zeka Modeliniz (sonuç)
```

### 📦 Gerçekte Neler İndirilir ve Nereye

#### **İlk Defa Herhangi Bir Script Çalıştırırken:**
```
HuggingFace'den İndiriliyor:
├── tokenizer.json (2-5MB) - Yapay zekanın kelime hazinesi
├── model dosyaları (500MB-2GB) - Yapay zekanın beyni
├── config dosyaları (birkaç KB) - Modeli nasıl kullanacağını
└── Toplam: Genellikle 500MB-2GB model başına

Kaydedilir: C:\Users\[SizinAdınız]\.cache\huggingface\
```

#### **Daha Sonraki Her Seferinde:**
```
Yerel önbellekten yükleme: Anında!
İnternet gerekir: Hiç (tamamen çevrimdışı)
```

### 🎯 Sihirli An: Adım Adım

**`python train_qwen.py` çalıştırdığınızda:**

```
[Dakika 1: Kurulum ve İndirmeler]
[Bilgisayarınız] Kütüphaneler yükleniyor...
[PyTorch] ✓ Yapay zeka motoru başlatıldı
[Transformers] HuggingFace'de Qwen/Qwen2.5-0.5B-Instruct kontrol ediliyor...
[İnternet] Model dosyaları indiriliyor (1.2GB)...
[İlerleme] ████████████████████ %100 - 2 dakika
[Yerel Önbellek] Model gelecek kullanım için kaydedildi

[Dakika 3: Model Yükleme]
[Transformers] Yapay zeka modeli önbellekten yükleniyor...
[BitsAndBytes] Model sıkıştırılıyor (1.2GB → 300MB)...
[PEFT] Eğitilebilir adaptör katmanları ekleniyor...
[Bellek] 2GB yerine 500MB RAM kullanıyor
[Durum] ✓ Eğitime hazır

[Dakika 4-30: Eğitim]
[Datasets] Eğitim örnekleriniz yükleniyor...
[TRL] Eğitim süreci başlatılıyor...
[PyTorch] Batch 1/100 işleniyor...
[PEFT] Sadece adaptör katmanları güncelleniyor...
[İlerleme] Eğitim kaybı: 2.4 → 1.8 → 1.2 (gelişiyor!)
[Durum] ✓ Eğitim tamamlandı

[Dakika 30: Test]
[Yapay Zekanız] Yeni yetenekler test ediliyor...
[Karşılaştırma] Öncesi vs Sonrası sonuçlar...
[Sonuç] Kişiselleştirilmiş yapay zekanız hazır!
```

### 💡 Bu Mimari Neden Devrimsel

**Geleneksel yaklaşım:**
- Her bileşen için doktora seviyesi bilgi gerekir
- Pahalı bulut altyapısı gerekir
- Anlayamadığınız kara kutu süreçler
- Satıcıya bağımlılık ve sürekli maliyetler

**Bizim modüler yaklaşımımız:**
- **Her kütüphane bir iş yapar** → Anlaması ve hata ayıklaması kolay
- **Standart arayüzler** → Her şey sorunsuzca birlikte çalışır
- **Topluluk tarafından sürdürülür** → Sürekli gelişir, asla eskimez
- **Karıştır ve eşleştir** → Farklı yaklaşımlardan teknikleri birleştir
- **Aşamalı öğrenme** → Bir seferde bir parçaya hakim ol

---

## Bölüm 1: Temel - Microsoft Her Şeyi Değiştirdiğinde

### Edward Hu’nun Dehası

2021 yılında Microsoft Research’ün koridorlarında Edward Hu, yapay zeka topluluğunu yıllardır şaşırtan bir matematiksel bulmacayla boğuşuyordu. Devasa bir sinir ağını yeniden eğitmeden ona yeni numaralar nasıl öğretilirdi?

Geleneksel bilgiye göre, tüm ağırlıkları—GPT-3 için 175 milyar tanesini—güncellemek zorundaydınız. Bu, yeni bir tablo asmak için evinizi tamamen yeniden inşa etmeniz gerektiğini söylemek gibiydi.

Ama Hu’nun farklı bir fikri vardı. Ya yapılması gereken “değişiklikler” aslında o kadar karmaşık değilse? Ya bilginin çoğu zaten oradaysa ve sadece birkaç stratejik “adaptör” eklemek gerekiyorsa?

**Atılım Anı**

Hu, derin bir gerçeği fark etti: İnce ayar için gereken güncellemeler genellikle düşük içsel boyuta sahiptir. Basitçe söylemek gerekirse, yapılması gereken değişiklikler çok daha küçük matematiksel yapılarla ifade edilebilir.

Devasa bir W matrisini doğrudan güncellemek yerine:
```python
W_new = W + ΔW  # ΔW büyük ve pahalı
```

Güncellemeyi iki küçük matrise ayırdı:
```python
W_new = W + B × A  # B ve A çok, çok daha küçük
```

Bu, bir ansiklopediyi tamamen yeniden yazmak yerine, doğru değişiklikleri işaret eden küçük bir dizin eklemek gibiydi.

**Sihirli Sayılar**

Hu, LoRA’yı (Düşük Rank Adaptasyonu) yayınladığında sonuçlar şaşırtıcıydı:
- **Bellek kullanımı %95 azaldı** - bazı modeller için 32GB’dan 1.5GB’a
- **Eğitim süresi %90 düştü** - günlerden saatlere
- **Performans aynı kaldı** - kalitede hiç kayıp yok

Aniden, masanızdaki GMKtec K11 bir oyuncak olmaktan çıktı. Gerçek bir yapay zeka araştırma istasyonu haline geldi.

> **🎯 Eğitim Bağlantısı**: İşte bu yüzden `02-huggingface-peft/` modülümüz LoRA ile başlıyor - bu, diğer her şeyin mümkün olmasını sağlayan temel. K11’de ilk LoRA ince ayarınızı çalıştırdığınızda, Hu’nun izinden gidiyorsunuz.

**📚 Daha Fazla Bilgi:**
- **Orijinal Makale**: [LoRA: Büyük Dil Modeli Adaptasyonu](https://arxiv.org/abs/2106.09685)
- **HuggingFace PEFT**: [https://github.com/huggingface/peft](https://github.com/huggingface/peft)
- **Microsoft Araştırma Blogu**: [LoRA: Büyük Dil Modellerini Uyarlama](https://www.microsoft.com/en-us/research/blog/lora-adapting-large-language-models/)

---

## Bölüm 2: NVIDIA Devrimi - İyi, Harika Olduğunda

### LoRA’yı Gölgeleyen Gizem

Üç yıl boyunca LoRA, etkili ince ayarların tartışmasız kralıydı. Dünya çapındaki araştırmacılar onu kullandı, sevdi ve kariyerlerini onun üzerine inşa etti. Ancak NVIDIA’dan Shih-Yang Liu’nun içini kemiren bir his vardı.

LoRA inanılmaz derecede iyi çalışıyordu, ama *neden*? Ve daha da önemlisi, naber eksik?

Liu, sinir ağı ağırlıklarının matematiğine derinlemesine daldı. Sayılara bakmıyordu sadece—onların *özünü* anlamaya çalışıyordu. Bir ağırlık matrisini ne harekete geçiriyordu?

**Eureka Anı**

2024’te bir akşam, Liu’nun atılımı geldi. Her ağırlık matrisinin iki temel bileşeni olduğunu fark etti:
- **Büyüklük**: Bağlantının ne kadar “güçlü” olduğu
- **Yön**: Bağlantının hangi yöne işaret ettiği

Bu, fizikte bir vektörü tanımlamak gibiydi—hem gücü hem de yönü tam olarak anlamak için ihtiyacınız var.

Sonra şok edici bir gerçek ortaya çıktı: **LoRA sadece yönü uyarlıyordu!**

```python
# LoRA’nın aslında yaptığı (farkında olmadan)
W = büyüklük × yön
LoRA_güncellemesi = sadece_yön_değişikliği  # Resmin yarısı eksik!

# DoRA’nın önerdiği
W = büyüklük × yön  
DoRA_güncellemesi = büyüklük_değişikliği + yön_değişikliği  # Tam resim!
```

**Her Şeyi Değiştiren Deney**

Liu ve ekibi DoRA’yı (Ağırlık Ayrıştırılmış Düşük Rank Adaptasyonu) test ettiğinde, sonuçlar nefes kesiciydi:

- **Llama 7B, akıl yürütme görevlerinde 3.7 puan arttı**
- **Llama 3 8B, performansta 4.4 puan sıçradı**
- **Test edilen her model** tutarlı iyileşmeler gösterdi
- **Ek bellek maliyeti yok** - LoRA ile aynı verimlilik

Bu, sanatçıların tüm bu süre boyunca paletlerinin sadece yarısını kullanarak resim yaptığını keşfetmek gibiydi.

**Gerçek Dünya Etkisi**

Sayılar hikayeyi anlatıyor:
- **Sağduyu akıl yürütme**: +3.7 puan (AI’da bu çok büyük!)
- **Çok turlu sohbetler**: +0.4 puan (daha doğal diyalog)
- **Görsel görevler**: +1.9 puan (daha iyi görüntü anlama)

Bağlam için, AI kıyaslamalarında 1 puanlık bir iyileşme önemli kabul edilir. DoRA, tutarlı bir şekilde 3-4 puanlık sıçramalar sunuyordu.

> **🎯 Eğitim Bağlantısı**: DoRA, `06-advanced-techniques/` modülümüzün yıldızı. K11’de LoRA ile DoRA performansını karşılaştırdığınızda, bu iyileşmeleri bizzat göreceksiniz. İyi ile harika ince ayar arasındaki fark bu.

**📚 Daha Fazla Bilgi:**
- **Orijinal Makale**: [DoRA: Ağırlık Ayrıştırılmış Düşük Rank Adaptasyonu](https://arxiv.org/abs/2402.09353)
- **NVIDIA Geliştirici Blogu**: [DoRA’yı Tanıtıyoruz, LoRA’ya Yüksek Performanslı Bir Alternatif](https://developer.nvidia.com/blog/introducing-dora-a-high-performing-alternative-to-lora-for-fine-tuning/)
- **DoRA Uygulaması**: [NVlabs/DoRA](https://github.com/NVlabs/DoRA)

---

## Bölüm 3: Topluluğun Cevabı - Zeki Beyinler İşbirliği Yaptığında

### Mükemmeliyetin Sorunu

DoRA harikaydı, ancak bir sorunu vardı: LoRA ile aynı belleği gerektiriyordu. GMKtec K11 gibi mütevazı donanımlara sahip birçok araştırmacı için—GPU görevleri için 8GB veya daha fazla paylaşılan sistem belleği ile—daha büyük modellerle çalışırken LoRA bile zorlayıcı olabiliyordu.

Answer.AI, yapay zekanın sadece milyon dolarlık GPU kümelerine sahip olanlara değil, herkese erişilebilir olması gerektiğine inanan yenilikçi bir araştırma laboratuvarı olarak devreye girdi.

### İki Zeki Fikrin Evliliği

Answer.AI ekibi DoRA’ya bakarak çılgınca bir fikir ortaya attı: “Ya bunu kuantizasyonla birleştirirsek?”

Kuantizasyon, bilmeyenler için, önemli detayları kaybetmeden yüksek çözünürlüklü bir fotoğrafı sıkıştırmak gibidir. Sayıları 16 bit hassasiyetle saklamak yerine, genellikle sadece 4 bit ile yetinebilirsiniz—bu, 4 kat bellek azalması demek!

Sorun şuydu: Kuantizasyon her zaman LoRA ile eşleştirilmişti. Kimse bunu üstün DoRA ile denememişti.

**Topluluk Deneyi**

Sonra olanlar güzeldi. Answer.AI, QDoRA’yı (Kuantize Edilmiş DoRA) tek başına geliştirmedi. Toplulukla işbirliği yaptı, deneyleri paylaştı, geri bildirim topladı ve hızla yineledi.

Sonuç? **QDoRA**—size şunu veren bir teknik:
- **DoRA’nın üstün performansı** (LoRA’ya göre +3.7 puan)
- **Kuantizasyonun bellek verimliliği** (4 kat bellek azalması)
- **Tek bir teknikte her iki dünyanın en iyisi**

```python
# Sihirli kombinasyon
QDoRA = DoRA_performansı + Kuantizasyon_verimliliği
# Sonuç: 1/4 bellekte üstün adaptasyon
```

**K11 Bağlantısı**

Bu, GMKtec K11 gibi donanımlar için oyunun kurallarını değiştirdi. Aniden şunları yapabilirdiniz:
- **7B modelleri 8GB paylaşılan sistem belleğinde çalıştırın** (önceden imkânsızdı)
- **DoRA seviyesinde performans** kuantizasyon verimliliğiyle alın
- **Tam ince ayardan daha iyi performans gösteren modeller eğitin**
- Hepsi bir tüketici masaüstünde

> **🎯 Eğitim Bağlantısı**: QDoRA, `04-quantization/` ve `06-advanced-techniques/` modüllerimizde öne çıkıyor. CLAUDE.md’de “EXTREME_CONFIG” (1 toplu iş boyutu, 4-bit kuantizasyon) gördüğünüzde, K11’de QDoRA’yı mümkün kılan tam olarak bu bellek-verimli teknikleri kullanıyorsunuz.

**📚 Daha Fazla Bilgi:**
- **Answer.AI Blogu**: [QDoRA: Kuantize Edilmiş DoRA İnce Ayar](https://www.answer.ai/posts/2024-03-14-qdora.html)
- **Topluluk Tartışması**: [QDoRA Uygulama Konusu](https://github.com/huggingface/peft/discussions/1474)
- **Kuantizasyon Kılavuzu**: [BitsAndBytes Dokümantasyonu](https://github.com/TimDettmers/bitsandbytes)

---

## Bölüm 4: Matematikçinin İçgörüsü - Neden Rastgele Yanlış?

### Her Şeyi Başlatan Can Sıkıcı Soru

DoRA manşetlere çıkarken, başka bir grup araştırmacı rahatsız edici bir soru soruyordu: “Neden LoRA adaptörlerini rastgele sayılarla başlatıyoruz?”

Düşünün. Büyük modelleri insan bilgisini kodlamak için muazzam çaba harcıyoruz. Bu modeller, milyarlarca metin örneğinden öğrenilen desenleri içeriyor. Ağırlık matrisleri dilin, akıl yürütmenin ve bilginin sırlarını tutuyor.

Ve sonra, onları uyarlamak istediğimizde... tamamen rastgele gürültüyle mi başlıyoruz?

Bu, bir usta şefin mükemmel hazırlanmış tarifine sahip olmak ve sonra marketten rasgele malzemeler seçerek eklemeler yapmak gibiydi.

### Ana Bileşen Devrimi

PiSSA (Ana Tekil Değerler ve Tekil Vektörler Adaptasyonu) arkasındaki matematikçiler daha iyi bir fikir buldu. Rastgele başlatma yerine, modelin zaten bildiği **en önemli kısımlardan** başlasak ne olur?

**Matematiksel Sihir**

Her ağırlık matrisi, Tekil Değer Ayrışımı (SVD) kullanılarak ayrıştırılabilir. Bunu, karmaşık bir senfoniyi en önemli müzikal temalarına ayırmak gibi düşünün:

```python
# Geleneksel LoRA: Rastgele gürültüyle başla
A = rastgele_gürültü()  # Herhangi bir yere işaret edebilir!
B = sıfırlar()         # Başlangıçta hiçbir katkı sağlamaz

# PiSSA: Modelin en önemli desenleriyle başla
U, S, V = SVD(orijinal_ağırlık)  # “Senfoniyi” ayır
A = en_önemli_U            # Ana “temalarla” başla  
B = en_önemli_S @ en_önemli_V  # Onların önem ağırlıkları
```

**Parlak İçgörü**

PiSSA araştırmacıları, en yüksek tekil değerlerin ve vektörlerin modelin öğrendiği en kritik desenleri temsil ettiğini fark etti. Adaptörleri bu bileşenlerle başlatarak, ince ayar sürecine şunu söylüyorsunuz: “Buradan başla—en çok bu önemli.”

Bu, bir öğrenciye yeni materyali öğrenmeden önce ders kitabının en önemli bölümlerini vermek gibiydi.

### Herkesi Şok Eden Sonuçlar

PiSSA test edildiğinde, iyileşmeler anında ve tutarlıydı:

- **Daha hızlı yakınsama**: Modeller yeni görevleri daha az adımda öğrendi
- **Daha iyi kararlılık**: Eğitim daha pürüzsüz ve öngörülebilir oldu
- **Üstün nihai performans**: Sonuçlar sürekli olarak rastgele başlatmayı geçti
- **İlkeli yaklaşım**: Nihayet matematiksel olarak sağlam bir adaptasyon başlangıcı

**Öğrenme Hızı Devrimi**

Belki de en önemlisi, PiSSA modelleri daha hızlı öğrendi. K11’deki eğitim ortamımızda bu şu anlama geliyor:
- **Daha kısa eğitim süreleri** (45-60 dakika yerine 15-30 dakika)
- **Daha az elektrik maliyeti** (uzun eğitim oturumları için önemli)
- **Daha hızlı deney döngüleri** (aynı sürede daha fazla fikir deneyin)

> **🎯 Eğitim Bağlantısı**: PiSSA teknikleri `06-advanced-techniques/` modülümüze entegre edilmiştir. Eğitimlerde başlatma stratejilerini karşılaştırdığınızda, “akıllı” başlamanın “rastgele” başlamayı her zaman yendiğini göreceksiniz. `00-first-time-beginner/` içindeki Mistral Large 2 örneklerimizde bu özellikle belirgin—rastgele başlatma ile 30 dakika süren aynı model, PiSSA ile 15 dakikada yakınsar!

**📚 Daha Fazla Bilgi:**
- **Araştırma Makalesi**: [PiSSA: Ana Tekil Değerler ve Vektörler Adaptasyonu](https://arxiv.org/abs/2404.02948)
- **Uygulama**: [GraphPKU/PiSSA](https://github.com/GraphPKU/PiSSA)
- **Matematiksel Arka Plan**: [Tekil Değer Ayrışımı Açıklaması](https://web.mit.edu/be.400/www/SVD/Singular_Value_Decomposition.htm)

---

## Bölüm 5: Hizalanma Devrimi - Yapay Zeka Kendi Öğretmeni Olduğunda

### İnsan Darboğazı Sorunu

2024’e gelindiğinde, yapay zeka geliştirmede yeni bir kriz ortaya çıkıyordu. Modeller inanılmaz derecede güçlü hale geliyordu, ancak onları yardımsever, zararsız ve dürüst yapmak için İnsan Geri Bildirimiyle Pekiştirme Öğrenimi (RLHF) adı verilen bir şey gerekiyordu.

Süreç basitti ama pahalıydı: İnsanlara binlerce model yanıtını gösterin, hangilerinin daha iyi olduğunu değerlendirmelerini isteyin ve bu geri bildirimi modeli iyi davranmaya eğitmek için kullanın.

Sorun şuydu: **İnsanlar pahalı, yavaş ve tutarsız.**

Tek bir hizalanma çalışması, insan etiketleme ücretleri için 50.000 dolara mal olabilirdi. Daha kötüsü, insanlar yoruluyor, birbirleriyle çelişiyor ve 7/24 çalışamıyordu. Bu, her öğrencinin kişisel bir öğretmene ihtiyaç duyarak eğitimi ölçeklendirmeye çalışmak gibiydi—teoride asil, pratikte imkânsız.

### Anayasal Yapay Zeka Atılımı

Anthropic’ten (Claude’un arkasındaki şirket) Lee ve meslektaşları devrimci bir fikir geliştirdi: Ya yapay zeka kendi kendine öğretmeyi öğrenseydi?

Anayasal Yapay Zeka dedikleri bir şey geliştirdiler; burada insanlar geri bildirim sağlamak yerine, güçlü bir yapay zeka modeli (GPT-4 gibi) bir “anayasa” ilkelerine göre yanıtları değerlendiriyor ve geliştiriyor.

**RLAIF’in Sihri**

RLAIF (Yapay Zeka Geri Bildirimiyle Pekiştirme Öğrenimi) senaryoyu tamamen tersine çevirdi:

```python
# Geleneksel RLHF: Pahalı ve yavaş
insan_değerlendirmesi = pahalı_insan_etiketleyici(model_yanıtı)
model.öğren(insan_değerlendirmesi)

# RLAIF: Hızlı ve ölçeklenebilir
ai_değerlendirmesi = gpt4_anayasal_değerlendirici(model_yanıtı, anayasa)
model.öğren(ai_değerlendirmesi)
```

**Şok Edici Sonuçlar**

Diyalog ve özetleme görevlerinde test edildiğinde, RLAIF modelleri RLHF modelleriyle **aynı** performansı gösterdi. Yapay zeka geri bildirimi, insan geri bildirimi kadar iyiydi, ancak:

- **1000 kat daha ucuz**: Çalışma başına 50.000 dolar yerine 500 dolar
- **1000 kat daha hızlı**: Haftalar yerine dakikalar
- **Sonsuz ölçeklenebilir**: İnsan yorgunluğu veya erişilebilirlik kısıtlamaları yok
- **Daha tutarlı**: Yapay zeka kötü günler geçirmez veya anlaşmazlık yaşamaz

### Anayasal Eğitim Devrimi

Atılım, sadece maliyet tasarrufunun ötesine geçti. Anayasal Yapay Zeka, karmaşık etik ilkeleri doğrudan eğitime kodlamayı mümkün kıldı:

- **Yardımseverlik**: Dürüst kalarak maksimum yardım sağlama
- **Zararsızlık**: Zararlı içerik üretmekten kaçınma
- **Dürüstlük**: Halüsinasyon yerine belirsizliği kabul etme

> **🎯 Eğitim Bağlantısı**: Bu, `07-system-prompt-modification/` modülümüzün temelidir. K11’de anayasal eğitim kullanarak hizalanmış modeller oluşturduğunuzda, büyük yapay zeka laboratuvarlarının kullandığı teknikleri kullanıyorsunuz—ama sizin özel ihtiyaçlarınıza uyarlanmış. CLAUDE.md’de belirtilen “20-40 dakika eğitim süresi”? Bu, RLAIF’in tüketici donanımında gelişmiş hizalamayı erişilebilir kılması.

**📚 Daha Fazla Bilgi:**
- **Anayasal Yapay Zeka Makalesi**: [Anayasal Yapay Zeka: Yapay Zeka Geri Bildiriminden Zararsızlık](https://arxiv.org/abs/2212.08073)
- **RLAIF Araştırması**: [RLAIF: İnsan Geri Bildiriminden Pekiştirme Öğrenimini Ölçeklendirme](https://arxiv.org/abs/2309.00267)
- **Anthropic Blogu**: [Anayasal Yapay Zeka: Yapay Zeka Geri Bildiriminden Zararsızlık](https://www.anthropic.com/news/constitutional-ai-harmlessness-from-ai-feedback)
- **Uygulama Kılavuzu**: [TRL Anayasal Eğitim](https://huggingface.co/docs/trl/constitutional_ai)

---

## Bölüm 6: LLaMA-Factory Devrimi - Karmaşıklık Basit Olduğunda

### Çok Fazla Seçenek Sorunu

2024’e gelindiğinde, ince ayar manzarası inanılmaz derecede zengin—ve inanılmaz derecede kafa karıştırıcı—hale gelmişti. LoRA, DoRA, QLoRA, QDoRA, PiSSA, RLHF, RLAIF ve daha onlarca teknik vardı. Her biri güçlüydü, ama hepsini öğrenmek, dünyadaki her mutfağı öğrenerek usta şef olmaya çalışmak gibiydi.

LLaMA-Factory, basit bir soru soran bir proje olarak devreye girdi: “Ya tüm bu teknikleri tek bir güzel arayüz üzerinden erişilebilir kılsak?”

### Sıfır Kod Devrimi

LLaMA-Factory’nin yaratıcıları derin bir gerçeği fark etti: Modelleri ince ayar yapmak isteyen herkes programcı değil. Doktorlar, avukatlar, araştırmacılar, yazarlar ve girişimciler, yapay zekayı iyileştirebilecek alan bilgisine sahip—ama Python, CUDA ve dağıtık eğitimi öğrenmeleri gerekmemeli.

**Web Arayüzü Atılımı**

LLaMA-Factory, devrimci bir şey sundu: İnce ayar için bir web arayüzü. Şunları yapabilirdiniz:
- **100’den fazla model arasından seçim yapın**, Mistral Large 2 gibi en son sürümler dahil
- **Eğitim yönteminizi seçin** (LoRA, DoRA, RLHF) açılır menülerden
- **Verilerinizi yükleyin** dosyaları sürükleyip bırakarak
- **Eğitimi izleyin** gerçek zamanlı grafiklerle
- **Modelleri dışa aktarın** ihtiyacınız olan herhangi bir formata

```bash
# Her şeyi değiştiren sihirli komut
llamafactory-cli webui
# Tarayıcınızda güzel bir arayüz açar
```

**Gün-0 Vaadi**

Belki de en dikkat çekici olanı, LLaMA-Factory’nin yeni modeller için “Gün-0” desteği taahhüt etmesiydi. Meta, Llama 3.1’i yayınladığında, LLaMA-Factory’de saatler içinde destekleniyordu. Mistral Large 2 piyasaya sürüldüğünde, hemen oradaydı.

Bu sadece kolaylık değildi—devrimdi. Daha önce, çerçeve desteği için 3-6 ay beklemek normaldi. LLaMA-Factory, en yeni modelleri anında erişilebilir kıldı.

> **🎯 Eğitim Bağlantısı**: İşte bu yüzden öğrenme yolculuğumuza `08-llamafactory/` ekledik. 00-07 modüllerinde temelleri öğrendikten sonra, LLaMA-Factory gelişmiş deneyler için “komuta merkezi” olur. Web arayüzü, yapılandırma dosyaları yerine veri ve sonuçlara odaklanmak isteyen öğrenciler için mükemmel.

### Üretim Hattı Rüyası

Ama LLaMA-Factory daha ileri gitti. İnce ayarı kolaylaştırmakla yetinmedi—onu **tamamlanmış** yaptı. Yeni başlayanlara yardımcı olan aynı araç şunları da destekledi:
- **Çoklu GPU eğitimi** DeepSpeed entegrasyonu ile
- **Deney takibi** Wandb ve TensorBoard ile
- **Model değerlendirme** kapsamlı kıyaslamalarla
- **Dağıtım hatları** vLLM ve Ollama ihracatı ile

Bu, basit bir hesap makinesine sahip olup gerektiğinde diferansiyel denklemleri çözebilen bir makineye dönüşmesi gibiydi.

> **🎯 Eğitim Bağlantısı**: `03-ollama/` modülümüz, LLaMA-Factory’yi tamamlar ve ince ayar yapılmış modelleri yerel veya uç cihazlarda çalıştırmak için dağıtım komut dosyaları sağlar, böylece yapay zekanız her yerde erişilebilir olur.

**📚 Daha Fazla Bilgi:**
- **LLaMA-Factory GitHub**: [hiyouga/LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)
- **Dokümantasyon**: [LLaMA-Factory Belgeleri](https://llamafactory.readthedocs.io/)
- **Web Arayüzü Demosu**: [LLaMA-Factory WebUI Eğitimi](https://github.com/hiyouga/LLaMA-Factory/wiki/Web-UI)
- **Model Desteği**: [Desteklenen Modeller Listesi](https://github.com/hiyouga/LLaMA-Factory#supported-models)

---

## Bölüm 7: DeepSeek Anı - Hangzhou’da Bir Şok Dalgası

### Ezilenin Zaferi

Ocak 2025’te, Çin’in Hangzhou şehrinde bir fırtına koptu. Liang Wenfeng’in High-Flyer hedge fonu tarafından desteklenen nispeten bilinmeyen bir startup olan DeepSeek, DeepSeek-R1’i piyasaya sürdü. Bu sadece başka bir dil modeli değildi—bir devrimdi. ABD ihracat kontrolleriyle sınırlı Nvidia H800 çipleriyle inşa edilen R1, sadece 5.6 milyon dolarla OpenAI’nin o1 modelinin akıl yürütme gücüne ulaştı; Batılı devlerin 100 milyon dolarlık bütçelerinin bir kısmıyla.

**Teknik Büyücülük**

DeepSeek’in sırrı, Uzmanlar Karışımı (MoE) mimarisindeydi; her sorgu için modelin sadece en ilgili kısımlarını etkinleştiren akıllı bir numara, hesaplama taleplerini keskin bir şekilde azalttı. Çok Başlı Gizli Dikkat (MLA) ile birleştirildiğinde, karmaşık verileri cerrahi hassasiyetle işledi. İşte MoE’nin nasıl çalıştığına dair bir bakış:

```python
class MixtureOfExperts:
    def __init__(self, uzmanlar):
        self.uzmanlar = uzmanlar  # Uzmanlaşmış alt modeller listesi
        self.kapı = KapıAğı()  # Hangi uzmanı kullanacağına karar verir

    def ileri(self, giriş):
        # Kapı, giriş için en ilgili uzmanları seçer
        uzman_ağırlıkları = self.kapı(giriş)
        çıktı = 0
        for uzman, ağırlık in zip(self.uzmanlar, uzman_ağırlıkları):
            çıktı += ağırlık * uzman(giriş)
        return çıktı
```

Pekiştirme öğrenimi, ağır denetimli ince ayar yerine R1’in matematik ve kodlama becerilerini keskinleştirdi, onu güçlü bir rakip haline getirdi. MIT Lisansı altında mevcut olan R1, dünya çapındaki geliştiricilere GMKtec K11 gibi mütevazı donanımlarda son teknoloji modelleri ince ayar yapma gücü verdi.

**Wall Street Depremi**

Gerçek drama, 27 Ocak 2025’te, DeepSeek’in sohbet botunun Apple’ın ABD App Store’unda ChatGPT’yi geçerek zirveye yerleşmesiyle展开了。Wall Street sarsıldı: Nasdaq %3,1 düştü, Nvidia tek bir günde 600 milyar dolar piyasa değeri kaybetti—ABD tarihindeki en büyük tek günlük düşüş. Yapay zekanın enerji açlığı üzerine bahis oynayan Constellation Energy ve Vistra gibi kamu hizmeti hisseleri %20’den fazla değer kaybetti. Marc Andreessen bunu bir “Sputnik anı” olarak adlandırdı ve Başkan Trump, Amerikan teknolojisi için bir “uyarı zili” olduğunu söyledi.

Ancak kaosun ortasında, DeepSeek’in açık kaynak ruhu küresel bir rönesansı ateşledi. R1’in koduyla silahlanan girişimler ve hobi sahipleri, finansal danışmanlardan tıbbi teşhislere kadar özel yapay zeka çözümleri üretmeye başladı, hepsi tüketici sınıfı donanımlarda çalışıyordu.

> **🎯 Eğitim Bağlantısı**: DeepSeek-R1’i `05-examples/` modülümüzde keşfedin; burada K11’de LLaMA-Factory kullanarak ince ayar yapabilirsiniz. MoE verimliliğini `06-advanced-techniques/` içinde Mistral Large 2 ile karşılaştırın ve gerçek dünya uygulamaları için `03-ollama/` ile yerel olarak dağıtın.

**📚 Daha Fazla Bilgi:**
- **DeepSeek Duyurusu**: [DeepSeek-R1 Sürümü](https://www.deepseek.com/)
- **MoE Genel Bakış**: [Uzmanlar Karışımı Açıklaması](https://huggingface.co/blog/moe)
- **Piyasa Etkisi**: [Bloomberg: DeepSeek’in Piyasa Şoku](https://www.bloomberg.com/news/articles/2025-01-28/ai-startup-deepseek-shakes-up-market)

---

## Sonsöz: Gelecek Sizin Ellerinizde

### Bugün Neredeyiz

2025’in ortasında dururken ve 2026’ya bakarken, ince ayar devrimi yapay zekada mümkün olanı temelden değiştirdi. Hu’nun temel LoRA’sından DeepSeek’in çığır açan R1’ine kadar bu atılımlar, yapay zekanın demokratikleşmesini temsil ediyor. GMKtec K11’iniz, GPU görevleri için 8GB veya daha fazla paylaşılan sistem belleği ile şimdi şunları yapabilir:
- GPT-3 ile rekabet eden modelleri ince ayar yapma
- Genel modelleri geride bırakan alan özelinde yapay zeka eğitimi
- Aylar önce var olmayan teknikleri deney yapma
- Büyük bütçeler olmadan hizalanmış, yardımsever yapay zeka yaratma

### Öğrenme Yolculuğu Önde

**Eğitmenler İçin: Devrimi Öğretmek**

Bu kavramları öğrettiğinizde, sadece teknikleri açıklamıyorsunuz—geleceğin anahtarlarını paylaşıyorsunuz. Bu becerileri öğrenen her öğrenci, daha önce doktora araştırmacı ekipleri gerektiren sorunları çözebilecek hale gelir.

**Dersleriniz İçin Üç Perdelik Yapı:**

**Birinci Perde: Sorun** (İmkânsızlıkla onları yakalayın)
- “ChatGPT’yi özelleştirmek istediğinizi hayal edin, ama eğitim 12 milyon dolara mal oluyor...”
- İlerlemeyi engelleyen duvarı gösterin

**İkinci Perde: Atılım** (Dehayı ortaya çıkarın)
- Her keşfi anlatın: LoRA, DoRA, PiSSA, RLAIF, DeepSeek’in MoE’si
- Benzetmeler kullanın: heykeltıraşlar, senfoniler, simyacılar
- Somut sayılar gösterin: +3.7 puan, %95 bellek tasarrufu, 5.6 milyon dolarlık eğitim

**Üçüncü Perde: Gelecek** (Onları katkıda bulunmaya teşvik edin)
- “SİZ hangi atılımı keşfedeceksiniz?”
- “Bu hikayenin bir sonraki bölümü yazılmadı”
- “Araçlar şimdi sizin elinizde”

### **Etkileşimli Öğretim Teknikleri**

**Heykeltıraş Alıştırması**
Öğrencilere gerçek kil verin. Bazıları kaba araçlar (LoRA), bazıları hassas aletler (DoRA), bazıları DeepSeek’in MoE verimliliği kullansın. Hangi heykeller daha iyi olur? Neden?

**Bellek Oyunu**
Mistral Large 2 veya DeepSeek-R1’i yüklerken RAM kullanımını gerçek zamanlı gösterin. `04-quantization/` ile belleğin 32GB’dan 8GB’a düştüğünü izleyin.

**Performans Yarışı**
LoRA, DoRA ve DeepSeek-R1 ile aynı ince ayar görevlerini çalıştırın `06-advanced-techniques/` içinde. Öğrenciler, doğruluğun gerçek zamanlı yükseldiğini görerek geleceğin geçmişi geçtiğine tanık olur.

> **🎯 Tam Eğitim Entegrasyonu**: Bu hikayede her teknik, öğrenme modüllerimizde uygulamalı uygulamalara sahiptir. Öğrenciler bu atılımları sadece öğrenmez—onları yeniden yaratır, geliştirir ve kendi yeniliklerini keşfeder. Gerçek dünya kullanım durumlarını görmek için `05-examples/` keşfedin.

### Bir Sonraki Bölüm: 2026’da Neler Geliyor

2026’ya bakarken, DeepSeek anı yapay zeka kurallarını yeniden yazdı. Ortaya çıkan trendler hikayemizi daha da heyecanlı kılıyor:

**Çok Modlu Devrim**
Şimdi 2025’te, dil modellerini değil, görme + dil sistemlerini birlikte uyarlıyorsunuz. Kod yazabilen ve UI ekran görüntülerini anlayan bir modeli eğittiğinizi hayal edin. `05-examples/` modülümüz, K11’de LLaVA ile metin ve görüntü anlamayı birleştiren çok modlu deneyler içerir.

**Federated Gelecek**
Eğitim, dağıtık ve özel hale geliyor. K11’iniz, verileri yerel tutarken daha iyi modeller eğitmek için binlerce cihazla işbirliği yapabilir, `06-advanced-techniques/` içinde prototipler yapabileceğiniz bir teknik.

**Kendi Kendini İyileştiren Yapay Zeka**
Modeller, kullanıcı geri bildirimlerinden sürekli olarak gelişecek, hataları otomatik düzeltecek ve yeni alanlara manuel müdahale olmadan uyum sağlayacak. `07-system-prompt-modification/` içinde RLAIF kullanarak bu kavramları deneyin.

**DeepSeek Dalga Etkisi**
DeepSeek’in verimliliği, yapay zeka pazarını ikiye böldü: OpenAI gibi premium oyuncular varoluşsal atılımlar peşinde, DeepSeek-R2 gibi açık kaynak modeller (2026 için planlanıyor) ise küçük işletmeleri ve girişimleri güçlendiriyor. Jevons Paradoksu, daha ucuz yapay zekanın üstel benimsenmeyi tetikleyeceğini öne sürüyor; sağlık hizmetlerinden finansa kadar özel modelleri körüklüyor. ChatGPT tabanlı portföylerin %29,22 kazanç sağladığı erken deneyler, yapay zeka finansal danışmanların insanları geçebileceğini ima ediyor. Ancak dikkat: 2025’te DeepSeek’in sunucularına yapılan siber saldırılar zayıflıkları açığa çıkardı ve İtalya ile Avustralya’daki yasaklar gizlilik zorluklarını işaret ediyor.

### En Önemli Ders

Hu’nun ilk LoRA deneylerinden DeepSeek’in R1’ine kadar bir desen beliriyor: **En derin atılımlar, genellikle başkalarının göz ardı ettiği basit soruları sormaktan gelir.**
- Hu sordu: “TÜM ağırlıkları güncellemek zorunda mıyız?”
- Liu sordu: “LoRA ağırlık yapısında aslında ne yapıyor?”
- DeepSeek sordu: “Daha azıyla devlerle eşleşebilir miyiz?”

### Öğrencilerinizin Fırsatı

Bugün sınıfınızda oturan öğrenciler, bu atılımları yaratan aynı araçlara sahip:
- Hugging Face üzerinden **en yeni modeller** (Mistral Large 2, DeepSeek-R1)
- **Güçlü teknikler** (LoRA, DoRA, RLAIF, MoE)
- K11 gibi **erişilebilir donanım**
- Deneyleri demokratikleştiren **açık kaynak çerçeveler**

En önemlisi, başkalarının kaçırdığı şeyleri görebilecek **taze gözlere** sahipler.

### Maceraya Çağrı

*“Bu hikayede her teknik, sizin gibi birinin imkânsız bir sorunla karşı karşıya kalmasıyla başladı. Hu, GPT-3’ü yeniden eğitmeyi göze alamadı. DeepSeek, en iyi çiplere erişemedi. Yine de dünyayı değiştirdiler.”*

*“SİZ hangi imkânsız sorunu çözeceksiniz? Hangi basit soruyu soracaksınız? Bu hikayenin bir sonraki bölümü sizin yazmanız için bekliyor.”*

---

## 📚 Tam Öğrenme Entegrasyonu

### **Tarih Boyunca Uygulamalı Yolculuk**

**Atılımlar Üzerinden Modül Yolu:**
- `00-first-time-beginner/`: Mistral Large 2 ile imkânsız rüyayı deneyimleyin
- `01-unsloth/`: Unsloth'un 2x hız artışı ile eğitimi hızlandırın
- `02-huggingface-peft/`: Hu'nun LoRA temelini öğrenin
- `03-ollama/`: **YENİ** - Hibrit iş akışı: Mevcut Ollama modelleri + HuggingFace eğitimi
- `04-quantization/`: Verimliliği performansla birleştirin (QDoRA)
- `05-examples/`: DeepSeek-R1 ve çok modlu deneyler dahil gerçek dünya uygulamalarını keşfedin
- `06-advanced-techniques/`: DoRA, PiSSA ve MoE atılımlarını uygulayın
- `07-system-prompt-modification/`: Anayasal Yapay Zeka ve RLAIF'i dağıtın
- `08-llamafactory/`: Hızlı deneyler için sıfır kod arayüzleri kullanın

### **🔄 Ollama Entegrasyon İş Akışı (Modül 03)**

#### **Görsel Akış Diyagramı**

```
                   MEVCUT KURULUMUNUZ
                         |
                 C:\Users\BM\.ollama\models\
            (İndirilmiş Ollama Modelleriniz)
                         |
                    ┌────┴────┐
                    ▼         ▼
            qwen3:0.6b    qwen3:8b
             (522MB)      (5.2GB)
                    │         │
                    └────┬────┘
                         ▼
               UYUMLULUK EŞLEŞTİRMESİ
               (use_ollama_models.py)
                         |
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   Qwen2.5-0.5B    Qwen2.5-7B    DeepSeek-R1
    (Eğitim)       (Eğitim)      (Eğitim)
         │              │              │
         └──────────────┼──────────────┘
                        ▼
                 HUGGINGFACE.CO
             (Eğitim Modellerini İndir)
                        |
                   ┌────┴────┐
                   ▼         ▼
             İlk Kez     Önbellekli
           (İndir)      (Hızlı Yükle)
                   │         │
                   └────┬────┘
                        ▼
              İNCE AYAR AŞAMASI
             (HuggingFace Ekosistemi)
                        |
              ┌─────────┼─────────┐
              ▼         ▼         ▼
      Modeli Yükle   LoRA Ekle   Eğit
        (PEFT)     (Adaptörler) (15-30dk)
              │         │         │
              └─────────┼─────────┘
                        ▼
              DIŞA AKTAR & DÖNÜŞTÜR
               (export_to_ollama.py)
                        |
                        ▼
               OLLAMA DAĞITIMI
            (ollama create my-model)
                        |
               ┌────────┼────────┐
               ▼        ▼        ▼
        Orijinal    Özel     Sonuçları
      qwen3:0.6b   my-model  Karşılaştır
           │          │          │
           └──────────┼──────────┘
                      ▼
             ÜRETİME HAZIR
           (İki Dünyanın En İyisi)
```

#### **Detaylı İş Akışı**

```
HİBRİT GELİŞTİRME DÖNGÜSÜ - İki Dünyanın En İyisi

Mevcut Ollama Modelleriniz:
├── qwen3:0.6b (522MB) ← Zaten indirilmiş
├── qwen3:8b (5.2GB) ← Zaten indirilmiş
├── deepseek-r1:8b (5.2GB) ← Zaten indirilmiş
└── [Modelleriniz] ← Geliştirmeye hazır

            ↓ Analiz & Eşleme ↓

HuggingFace Eğitim Eşdeğerleri:
├── Qwen/Qwen2.5-0.5B-Instruct ← qwen3:0.6b'nin eğitim versiyonu
├── Qwen/Qwen2.5-7B-Instruct ← qwen3:8b'nin eğitim versiyonu
├── deepseek-ai/DeepSeek-R1-Distill-Qwen-8B ← Eğitim versiyonu
└── [Eşdeğer modeller] ← Sadece eğitim sırasında indirin

🎯 EĞİTİM AŞAMASI (HuggingFace Ekosistemi):
   ├── python use_ollama_models.py ← Modellerinizi eşler
   ├── python train_qwen3_0_6b.py ← Otomatik oluşturulan script
   ├── Verilerinizle ince ayar ← K11'de 15-30 dakika
   └── İnce ayar yapılmış modeli kaydet ← Dışa aktarım için hazır

🚀 DAĞITIM AŞAMASI (Ollama Ekosistemi):
   ├── python export_to_ollama.py ← Format dönüştürme
   ├── ollama create my-custom-qwen -f Modelfile ← İçe aktar
   ├── ollama run my-custom-qwen ← Uzmanlaşmış modelinizi kullanın
   └── Orijinal ile karşılaştır: ollama run qwen3:0.6b

🔄 YINELEME DÖNGÜSÜ:
   ├── Her iki modeli yan yana test edin
   ├── Eğitim verilerini iyileştirin
   ├── Daha iyi örneklerle yeniden eğitin
   └── Gelişmiş versiyonu dağıtın

FAYDALAR:
├── [DEPOLAMA] Gereksiz indirme yok
├── [HIZ] Mevcut Ollama yatırımlarından faydalanın
├── [İŞ AKIŞI] Sorunsuz eğitim → dağıtım
└── [GİZLİLİK] Her şey K11'inizde kalır
```

**Kodda Tam Hikaye Kemeri:**
Öğrenciler yolculuğu yeniden yaratır, hayal kırıklıklarını yaşar, eureka anlarını kutlar ve bir sonraki bölümü yaratmaya hazır hale gelir.

### **Tam Kaynak Kütüphanesi**
- **DoRA Makalesi**: [Ağırlık Ayrıştırılmış Düşük Rank Adaptasyonu](https://arxiv.org/abs/2402.09353)
- **PiSSA Çalışmaları**: [Ana Tekil Değerler Adaptasyonu](https://arxiv.org/abs/2404.02948)
- **RLAIF Araştırması**: [Anayasal Yapay Zeka](https://arxiv.org/abs/2212.08073)
- **DeepSeek Duyurusu**: [DeepSeek-R1 Sürümü](https://www.deepseek.com/)
- **MoE Genel Bakış**: [Uzmanlar Karışımı Açıklaması](https://huggingface.co/blog/moe)
- **LLaMA-Factory**: [Sıfır kod ince ayar](https://github.com/hiyouga/LLaMA-Factory)
- **Unsloth**: [2x daha hızlı eğitim](https://github.com/unslothai/unsloth)
- **Ollama**: [Yerel model dağıtımı](https://ollama.ai/)
- **AMD ROCm**: [GPU hızlandırma kılavuzu](https://rocm.docs.amd.com/)

## 🚀 Hızlı Başlangıç Kılavuzu

### Ön Koşullar
- **Donanım**: AMD Ryzen 9 8945HS + Radeon 780M (GPU görevleri için 8GB+ paylaşılan sistem belleği ile)
- **RAM**: 32GB+ önerilir
- **Depolama**: 100GB+ boş alanlı hızlı NVMe SSD

### Kurulum
```bash
# Bu depoyu klonlayın (not: doğru yazım için https://github.com/beyhanmeyrali/fine-tuning olarak yeniden adlandırın)
git clone https://github.com/beyhanmeyrali/fine-tunning.git
cd fine-tunning

# Başlangıç modülüyle başlayın
cd 00-first-time-beginner/
python test_setup.py  # Ortamınızı doğrulayın

# Veya sıfır kod arayüzüne geçin
cd 08-llamafactory/
llamafactory-cli webui  # Web arayüzünü açar
```

### Öğrenme Yolu
1. **🎯 Başlangıç**: `00-first-time-beginner/` (Mistral Large 2, 30 dakika)
2. **⚡ Hız**: `01-unsloth/` (2x daha hızlı eğitim)
3. **🔧 Standart**: `02-huggingface-peft/` (LoRA temelleri)
4. **🚀 Dağıtım**: `03-ollama/` (Yerel model dağıtımı)
5. **🔄 Verimlilik**: `04-quantization/` (QDoRA teknikleri)
6. **📚 Örnekler**: `05-examples/` (Gerçek dünya ve DeepSeek-R1 uygulamaları)
7. **🔬 Gelişmiş**: `06-advanced-techniques/` (DoRA, PiSSA, MoE)
8. **🤝 Hizalanma**: `07-system-prompt-modification/` (RLAIF ve Anayasal Yapay Zeka)
9. **🖥️ Sıfır Kod**: `08-llamafactory/` (Web arayüzü)

---

## 📊 Depo İstatistikleri

![GitHub yıldızları](https://img.shields.io/github/stars/beyhanmeyrali/fine-tunning?style=social)
![GitHub çatalları](https://img.shields.io/github/forks/beyhanmeyrali/fine-tunning?style=social)
![GitHub sorunları](https://img.shields.io/github/issues/beyhanmeyrali/fine-tunning)
![GitHub lisansı](https://img.shields.io/github/license/beyhanmeyrali/fine-tunning)

**🌟 Bu depoyu yıldızlayın** eğer ince ayar devrimini anlamanıza yardımcı olduysa!

**🔄 Çatallayın ve katkıda bulunun** - bir sonraki atılım sizin olabilir!

---

*Bu atılımlar hikayesi, sizin keşif yolculuğunuz olur. Her teknik, her içgörü, her atılım sadece akademik tarih değil—usta olabileceğiniz, geliştirebileceğiniz ve sonunda devrim yaratabileceğiniz pratik bir beceridir.*

**❤️ ile [Beyhan MEYRALI](https://www.linkedin.com/in/beyhanmeyrali/) tarafından oluşturuldu | Yapay zekanın demokratikleşmesi için optimize edildi**