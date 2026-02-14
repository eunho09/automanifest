"""
manifest.json 자동 생성 스크립트

사용법:
1. 이 스크립트를 모드팩 폴더 옆에 놓기
2. 폴더 구조 예시:
   modpack/
     mods/
       jei.jar
       sodium.jar
     resourcepacks/
       custom.zip
     config/
       options.json
     shaderpacks/
       shader.zip

3. 실행:
   python generate_manifest.py --dir ./modpack --base-url https://your-server.com/files
   python generate_manifest.py --dir ./mcpack-files --base-url https://raw.githubusercontent.com/eunho09/mcpack/main/mcpack-files --mc-version 1.21.1 --loader-type neoforge --loader-version 21.1.172

4. manifest.json이 생성됨
"""

import hashlib
import json
import os
import argparse


def get_sha256(filepath):
    """파일의 SHA256 해시 계산"""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_file_size(filepath):
    """파일 크기 (bytes)"""
    return os.path.getsize(filepath)


def scan_directory(base_dir, base_url, folders):
    """지정된 폴더들을 스캔하여 파일 목록 생성"""
    files = []

    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        if not os.path.exists(folder_path):
            continue

        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                # base_dir 기준 상대 경로 (/ 구분자로 통일)
                relative_path = os.path.relpath(filepath, base_dir).replace("\\", "/")

                sha256 = get_sha256(filepath)
                size = get_file_size(filepath)
                url = f"{base_url.rstrip('/')}/{relative_path}"

                files.append({
                    "path": relative_path,
                    "sha256": sha256,
                    "url": url,
                    "size": size,
                    "required": True
                })

                print(f"  {relative_path} ({size:,} bytes) - {sha256[:16]}...")

    return files


def generate_manifest(args):
    print(f"Scanning: {args.dir}")
    print(f"Base URL: {args.base_url}")
    print()

    # 스캔할 폴더들
    folders = ["mods", "resourcepacks", "shaderpacks", "config"]

    files = scan_directory(args.dir, args.base_url, folders)

    manifest = {
        "mc_version": args.mc_version,
        "mod_loader": {
            "type": args.loader_type,
            "version": args.loader_version
        },
        "files": files,
        "java_args": args.java_args,
        "server_address": args.server_address
    }

    output_path = os.path.join(args.dir, "manifest.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print()
    print(f"========================================")
    print(f"manifest.json 생성 완료!")
    print(f"파일 수: {len(files)}")
    print(f"총 크기: {sum(f['size'] for f in files):,} bytes")
    print(f"저장 위치: {output_path}")
    print(f"========================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate manifest.json for MCPack")
    parser.add_argument("--dir", required=True, help="모드팩 폴더 경로")
    parser.add_argument("--base-url", required=True, help="파일 다운로드 기본 URL")
    parser.add_argument("--mc-version", default="1.21.1", help="MC 버전 (기본: 1.21.1)")
    parser.add_argument("--loader-type", default="neoforge", help="모드 로더 (기본: neoforge)")
    parser.add_argument("--loader-version", default="21.1.172", help="모드 로더 버전")
    parser.add_argument("--java-args", default="-Xmx4G -Xms2G", help="JVM 인자")
    parser.add_argument("--server-address", default=None, help="서버 주소")

    args = parser.parse_args()
    generate_manifest(args)