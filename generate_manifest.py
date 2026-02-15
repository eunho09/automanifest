#!/usr/bin/env python3
"""
manifest.json 자동 생성 스크립트

사용법:
  python generate_manifest.py                          # manifest_config.json 자동 로드
  python generate_manifest.py --config my_config.json  # 지정한 설정 파일 로드
"""

import hashlib
import json
import os
import sys
import argparse

SCAN_DIRS = ["mods", "resourcepacks", "shaderpacks", "config"]

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def scan_files(base_dir, base_url):
    files = []
    for scan_dir in SCAN_DIRS:
        full_dir = os.path.join(base_dir, scan_dir)
        if not os.path.isdir(full_dir):
            continue
        for root, _, filenames in os.walk(full_dir):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, base_dir).replace("\\", "/")
                size = os.path.getsize(filepath)
                sha256 = sha256_file(filepath)
                url = f"{base_url.rstrip('/')}/{rel_path}"

                files.append({
                    "path": rel_path,
                    "sha256": sha256,
                    "url": url,
                    "size": size,
                    "required": True,
                })
                print(f"  [{scan_dir}] {filename} ({size:,} bytes)")
    return files

def generate(config):
    base_dir = config["dir"]
    base_url = config["base_url"]
    mc_version = config["mc_version"]
    loader_type = config.get("loader_type", "vanilla")
    loader_version = config.get("loader_version", "")
    java_args = config.get("java_args", "-Xmx4G -Xms2G")
    server_address = config.get("server_address", "") or None

    print(f"=== Manifest Generator ===")
    print(f"Directory : {base_dir}")
    print(f"Base URL  : {base_url}")
    print(f"MC Version: {mc_version}")
    print(f"Loader    : {loader_type} {loader_version}")
    print(f"Server    : {server_address or '(none)'}")
    print()

    print("Scanning files...")
    files = scan_files(base_dir, base_url)
    print(f"\nFound {len(files)} file(s)\n")

    manifest = {
        "mc_version": mc_version,
        "mod_loader": {
            "type": loader_type,
            "version": loader_version,
        },
        "files": files,
        "java_args": java_args,
        "server_address": server_address,
    }

    os.makedirs(base_dir, exist_ok=True)
    output_path = os.path.join(base_dir, "manifest.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"manifest.json saved to: {output_path}")
    print("Done!")

def main():
    parser = argparse.ArgumentParser(description="Generate manifest.json for MCPack")
    parser.add_argument("--config", default="manifest_config.json",
                        help="설정 파일 경로 (기본: manifest_config.json)")
    args = parser.parse_args()

    config_path = args.config

    if not os.path.exists(config_path):
        print(f"설정 파일을 찾을 수 없습니다: {config_path}")
        print(f"manifest_config.json 파일을 만들어주세요.")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 필수 필드 확인
    required = ["dir", "base_url", "mc_version"]
    for key in required:
        if key not in config:
            print(f"설정 파일에 '{key}' 필드가 없습니다.")
            sys.exit(1)

    generate(config)

if __name__ == "__main__":
    main()