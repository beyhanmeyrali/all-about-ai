#!/bin/bash
# =============================================================================
# Curl Örnekleri: HTTP Katmanını Anlamak
# =============================================================================
#
# Bu betik, tüm LLM etkileşimlerinin arkasındaki ham HTTP isteklerini gösterir.
# Bunu anlamak şunlara yardımcı olur:
# - LLM'leri HERHANGİ BİR sisteme entegre etmek (sadece Python değil)
# - Ağ seviyesindeki sorunları ayıklamak
# - LangChain gibi frameworklerin arka planda ne yaptığını anlamak
#
# Yazar: Beyhan MEYRALI
# =============================================================================

# Çıktı için renkler
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # Renk Yok

OLLAMA_URL="http://localhost:11434"
MODEL="qwen2.5:3b"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Curl Örnekleri: Ham HTTP LLM Etkileşimleri               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# Örnek 1: Temel Sohbet
# =============================================================================

echo -e "${GREEN}Örnek 1: Temel Sohbet${NC}"
echo -e "${YELLOW}Ne olur: Basit bir soru gönder, yanıt al${NC}"
echo ""
echo "Komut:"
echo "--------"
cat << 'EOF'
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "user", "content": "What is 2+2?"}
  ],
  "stream": false
}'
EOF
echo ""
echo -e "${YELLOW}Çalıştırılıyor...${NC}"
curl -X POST $OLLAMA_URL/api/chat -d "{
  \"model\": \"$MODEL\",
  \"messages\": [
    {\"role\": \"user\", \"content\": \"What is 2+2?\"}
  ],
  \"stream\": false
}" 2>/dev/null | python3 -m json.tool
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =============================================================================
# Örnek 2: Sistem Promptu ile
# =============================================================================

echo -e "${GREEN}Örnek 2: Sistem Promptu ile${NC}"
echo -e "${YELLOW}Ne olur: Sistem mesajı ile LLM davranışını kontrol et${NC}"
echo ""
echo "Komut:"
echo "--------"
cat << 'EOF'
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "system", "content": "You are a pirate. Always talk like a pirate!"},
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "stream": false
}'
EOF
echo ""
echo -e "${YELLOW}Çalıştırılıyor...${NC}"
curl -X POST $OLLAMA_URL/api/chat -d "{
  \"model\": \"$MODEL\",
  \"messages\": [
    {\"role\": \"system\", \"content\": \"You are a pirate. Always talk like a pirate!\"},
    {\"role\": \"user\", \"content\": \"What is the capital of France?\"}
  ],
  \"stream\": false
}" 2>/dev/null | python3 -m json.tool
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =============================================================================
# Örnek 3: Geçmişli Konuşma
# =============================================================================

echo -e "${GREEN}Örnek 3: Geçmişli Konuşma${NC}"
echo -e "${YELLOW}Ne olur: LLM tam konuşmayı alarak 'hatırlar'${NC}"
echo ""
echo "Komut:"
echo "--------"
cat << 'EOF'
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "user", "content": "My favorite color is blue"},
    {"role": "assistant", "content": "That'\''s nice! Blue is a great color."},
    {"role": "user", "content": "What is my favorite color?"}
  ],
  "stream": false
}'
EOF
echo ""
echo -e "${YELLOW}Çalıştırılıyor...${NC}"
curl -X POST $OLLAMA_URL/api/chat -d "{
  \"model\": \"$MODEL\",
  \"messages\": [
    {\"role\": \"user\", \"content\": \"My favorite color is blue\"},
    {\"role\": \"assistant\", \"content\": \"That's nice! Blue is a great color.\"},
    {\"role\": \"user\", \"content\": \"What is my favorite color?\"}
  ],
  \"stream\": false
}" 2>/dev/null | python3 -m json.tool
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =============================================================================
# Örnek 4: Akış Yanıtı
# =============================================================================

echo -e "${GREEN}Örnek 4: Akış Yanıtı${NC}"
echo -e "${YELLOW}Ne olur: Tokenlar tek tek gelir (gerçek zamanlı)${NC}"
echo ""
echo "Komut:"
echo "--------"
cat << 'EOF'
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "user", "content": "Count from 1 to 5"}
  ],
  "stream": true
}'
EOF
echo ""
echo -e "${YELLOW}Çalıştırılıyor (tokenların gerçek zamanlı gelişini izleyin)...${NC}"
curl -X POST $OLLAMA_URL/api/chat -d "{
  \"model\": \"$MODEL\",
  \"messages\": [
    {\"role\": \"user\", \"content\": \"Count from 1 to 5\"}
  ],
  \"stream\": true
}" 2>/dev/null
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =============================================================================
# Örnek 5: Mevcut Modelleri Listele
# =============================================================================

echo -e "${GREEN}Örnek 5: Mevcut Modelleri Listele${NC}"
echo -e "${YELLOW}Ne olur: Hangi modellerin yüklü olduğunu gör${NC}"
echo ""
echo "Komut:"
echo "--------"
echo "curl http://localhost:11434/api/tags"
echo ""
echo -e "${YELLOW}Çalıştırılıyor...${NC}"
curl $OLLAMA_URL/api/tags 2>/dev/null | python3 -m json.tool
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =============================================================================
# Örnek 6: Model Bilgisini Kontrol Et
# =============================================================================

echo -e "${GREEN}Örnek 6: Model Bilgisini Al${NC}"
echo -e "${YELLOW}Ne olur: Model detaylarını gör (boyut, parametreler vb.)${NC}"
echo ""
echo "Komut:"
echo "--------"
cat << 'EOF'
curl -X POST http://localhost:11434/api/show -d '{
  "name": "qwen2.5:3b"
}'
EOF
echo ""
echo -e "${YELLOW}Çalıştırılıyor...${NC}"
curl -X POST $OLLAMA_URL/api/show -d "{
  \"name\": \"$MODEL\"
}" 2>/dev/null | python3 -m json.tool
echo ""
echo "-------------------------------------------------------------------"
echo ""

# =============================================================================
# Özet
# =============================================================================

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                          ANA ÇIKARIMLAR                           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "1. LLM API'leri JSON ile yapılan HTTP POST istekleridir"
echo "   → Bunları HERHANGİ BİR dilden/araçtan çağırabilirsiniz"
echo ""
echo "2. 'messages' dizisi çekirdek yapıdır"
echo "   → rol: 'system', 'user' veya 'assistant'"
echo "   → içerik: asıl mesaj metni"
echo ""
echo "3. Konuşma geçmişi = tüm önceki mesajları göndermek"
echo "   → LLM hiçbir şey saklamaz"
echo "   → Konuşma dizisini SİZ yönetirsiniz"
echo ""
echo "4. Sistem promptları davranışı kontrol eder"
echo "   → role='system' olan ilk mesaj"
echo "   → Kişiliği/talimatları ayarlar"
echo ""
echo "5. Akış UX'i iyileştirir"
echo "   → stream: true → tokenlar yavaş yavaş gelir"
echo "   → stream: false → tam yanıtı bekle"
echo ""
echo -e "${GREEN}Sıradaki: Bu örnekleri kendi promptlarınızla değiştirmeyi deneyin!${NC}"
echo ""
