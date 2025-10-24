# LBTAS Build and Deployment Guide

## Python Implementation

### Requirements
- Python 3.7 or higher
- No external dependencies

### Installation
```bash
# Direct execution
python3 lbtas.py --help

# Make executable (Unix/Linux/macOS)
chmod +x lbtas.py
./lbtas.py --help

# Install as system command (optional)
sudo cp lbtas.py /usr/local/bin/lbtas
lbtas --help
```

### Package Distribution
```bash
# Create distribution package
# setup.py (create this file):
from setuptools import setup

setup(
    name='lbtas',
    version='1.0.0',
    py_modules=['lbtas'],
    entry_points={
        'console_scripts': [
            'lbtas=lbtas:main',
        ],
    },
)

# Build and install
python3 setup.py sdist
pip install dist/lbtas-1.0.0.tar.gz
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY lbtas.py .
ENTRYPOINT ["python3", "lbtas.py"]
```

---

## TypeScript/Node.js Implementation

### Requirements
- Node.js 16.0 or higher
- npm or yarn

### Installation
```bash
# Install dependencies
npm install

# Compile TypeScript
npm run build

# Run
node lbtas.js rate --exchange "MyService"
```

### Package Distribution
```bash
# Publish to npm (after authentication)
npm publish

# Install from npm
npm install -g lbtas
lbtas rate --exchange "MyService"
```

### Development
```bash
# Watch mode for development
npx tsc --watch

# Run directly with ts-node (optional)
npm install -g ts-node
ts-node lbtas.ts rate --exchange "MyService"
```

### Docker
```dockerfile
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY lbtas.ts tsconfig.json ./
RUN npm run build
ENTRYPOINT ["node", "lbtas.js"]
```

---

## Go Implementation

### Requirements
- Go 1.21 or higher

### Build
```bash
# Standard build
go build -o lbtas lbtas.go

# Run
./lbtas rate --exchange "MyService"

# Build with optimizations
go build -ldflags="-s -w" -o lbtas lbtas.go
```

### Cross-Platform Builds
```bash
# Linux (64-bit)
GOOS=linux GOARCH=amd64 go build -o lbtas-linux-amd64 lbtas.go

# Linux (ARM64)
GOOS=linux GOARCH=arm64 go build -o lbtas-linux-arm64 lbtas.go

# macOS (Intel)
GOOS=darwin GOARCH=amd64 go build -o lbtas-darwin-amd64 lbtas.go

# macOS (Apple Silicon)
GOOS=darwin GOARCH=arm64 go build -o lbtas-darwin-arm64 lbtas.go

# Windows (64-bit)
GOOS=windows GOARCH=amd64 go build -o lbtas-windows-amd64.exe lbtas.go

# FreeBSD
GOOS=freebsd GOARCH=amd64 go build -o lbtas-freebsd-amd64 lbtas.go
```

### Installation
```bash
# Install to GOPATH
go install lbtas.go

# Or copy to system path
sudo cp lbtas /usr/local/bin/
```

### Docker
```dockerfile
# Multi-stage build
FROM golang:1.21-alpine AS builder
WORKDIR /build
COPY lbtas.go go.mod ./
RUN go build -ldflags="-s -w" -o lbtas lbtas.go

FROM alpine:latest
COPY --from=builder /build/lbtas /usr/local/bin/
ENTRYPOINT ["lbtas"]
```

---

## Rust Implementation

### Requirements
- Rust 1.70 or higher
- Cargo

### Build
```bash
# Debug build
cargo build
./target/debug/lbtas rate --exchange "MyService"

# Release build (optimized)
cargo build --release
./target/release/lbtas rate --exchange "MyService"
```

### Installation
```bash
# Install from source
cargo install --path .

# Or copy to system path
sudo cp target/release/lbtas /usr/local/bin/
```

### Cross-Compilation
```bash
# Install cross-compilation tool
cargo install cross

# Build for different targets
cross build --release --target x86_64-unknown-linux-gnu
cross build --release --target aarch64-unknown-linux-gnu
cross build --release --target x86_64-apple-darwin
cross build --release --target x86_64-pc-windows-gnu
```

### Docker
```dockerfile
# Multi-stage build
FROM rust:1.75 AS builder
WORKDIR /build
COPY Cargo.toml lbtas.rs ./
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /build/target/release/lbtas /usr/local/bin/
ENTRYPOINT ["lbtas"]
```

---

## GitHub Actions CI/CD

### Example workflow for all languages

```yaml
name: Build All Implementations

on: [push, pull_request]

jobs:
  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Test Python
        run: |
          python3 lbtas.py --help
          python3 -m py_compile lbtas.py

  typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Build TypeScript
        run: |
          npm install
          npm run build
          node lbtas.js --help

  go:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - name: Build Go
        run: |
          go build -o lbtas lbtas.go
          ./lbtas --help

  rust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - name: Build Rust
        run: |
          cargo build --release
          ./target/release/lbtas --help
```

---

## Performance Testing

### Benchmark Script (bash)
```bash
#!/bin/bash

echo "Creating test data..."
for i in {1..100}; do
    echo "$i,reliability,3" >> test_data.csv
done

echo "Python:"
time for i in {1..100}; do
    python3 lbtas.py add "test$i" reliability 3 > /dev/null 2>&1
done

echo "Go:"
time for i in {1..100}; do
    ./lbtas add "test$i" reliability 3 > /dev/null 2>&1
done

echo "Rust:"
time for i in {1..100}; do
    ./target/release/lbtas add "test$i" reliability 3 > /dev/null 2>&1
done
```

---

## Distribution Strategy

### GitHub Releases

Create releases for each implementation:

```bash
# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Build binaries for release
./build-all.sh

# Create GitHub release with binaries:
# - lbtas.py (Python)
# - lbtas-linux-amd64 (Go)
# - lbtas-darwin-amd64 (Go)
# - lbtas-windows-amd64.exe (Go)
# - lbtas-linux-amd64 (Rust)
# - lbtas-darwin-amd64 (Rust)
```

### Package Registries

- **Python**: PyPI via `twine`
- **TypeScript**: npm via `npm publish`
- **Go**: Go modules (no registry needed)
- **Rust**: crates.io via `cargo publish`

---

## Troubleshooting

### Python
```bash
# Permission denied
chmod +x lbtas.py

# Python not found
which python3
```

### TypeScript
```bash
# Module not found
npm install

# TypeScript errors
npx tsc --noEmit
```

### Go
```bash
# Go not in PATH
export PATH=$PATH:/usr/local/go/bin

# Module errors
go mod tidy
```

### Rust
```bash
# Cargo not found
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Dependency errors
cargo clean
cargo build
```
