#!/usr/bin/env bash
# Build llama.cpp with the (unmerged) DiffusionGemma PR #24423 plus our System One read server.
# Usage: ./build.sh   -> binaries in ../build/llama.cpp-diffusiongemma/build-cuda/bin/
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/../build/llama.cpp-diffusiongemma"
PR=24423

if [[ ! -d "$SRC/.git" ]]; then
  git init -q "$SRC"
  git -C "$SRC" remote add origin https://github.com/ggml-org/llama.cpp.git
fi
if [[ "${SKIP_FETCH:-0}" != 1 ]]; then
  git -C "$SRC" fetch -q --depth=1 origin "pull/$PR/head:pr-$PR"
  git -C "$SRC" checkout -q "pr-$PR"
fi

# graft dg-systemone-server into the tree as an example target
mkdir -p "$SRC/examples/dg-systemone"
cp "$HERE/dg-systemone-server.cpp" "$SRC/examples/dg-systemone/"
cat > "$SRC/examples/dg-systemone/CMakeLists.txt" <<'EOF'
set(TARGET dg-systemone-server)
add_executable(${TARGET} dg-systemone-server.cpp)
target_link_libraries(${TARGET} PRIVATE llama llama-common ${CMAKE_THREAD_LIBS_INIT})
target_compile_features(${TARGET} PRIVATE cxx_std_17)
EOF
grep -q dg-systemone "$SRC/examples/CMakeLists.txt" || echo 'add_subdirectory(dg-systemone)' >> "$SRC/examples/CMakeLists.txt"

cmake -S "$SRC" -B "$SRC/build-cuda" \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=120 \
  -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/gcc-13 \
  -DCMAKE_BUILD_TYPE=Release > /dev/null
cmake --build "$SRC/build-cuda" -j "$(nproc)" \
  --target dg-systemone-server llama-diffusion-cli llama-diffusion-gemma-server llama-bench

echo "built: $SRC/build-cuda/bin/dg-systemone-server (PR head $(git -C "$SRC" rev-parse --short HEAD))"
