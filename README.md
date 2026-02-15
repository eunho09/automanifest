# Manifest 자동 생성

1. 폴더에 원하는 모드, 리소스팩 넣기
2. `/AutoManifest/manifest_config.json` 파일에서 설정
3. `/AutoManifest/` 해당 위치에서 CMD `python generate_manifest.py` 실행
4. `/AutoManifest/mcpack-files/manifest.json` 파일 생성 여부 확인 및 설정 확인
5. 깃헙에 올리기

1) git add .
2) git commit -m "message"
3) git push

```
manifest.json 자동 생성 스크립트

사용법:
  python generate_manifest.py                          # manifest_config.json 자동 로드
  python generate_manifest.py --config my_config.json  # 지정한 설정 파일 로드
```
