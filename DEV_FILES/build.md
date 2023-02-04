## Building
flatpak-builder --user --install --force-clean build-dir io.github.swanux.hbud.yml
flatpak run io.github.swanux.hbud

## Python
python3 -m venv hbud-env
source hbud-env/bin/activate
pip3 install srt azapi mediafile pyacoustid musicbrainzngs langcodes language_data
pip3 freeze > requirements.txt
deactivate

flatpak-pip-gen.py --runtime='org.gnome.Sdk//43' -r='requirements.txt' --output pypi-dependencies

<!--pip3 install srt azapi mediafile pyacoustid musicbrainzngs langcodes language_data marisa_trie -t /home/daniel/GitRepos/hbud/DEV_FILES/modules/-->

## Useful links
https://hughsie.github.io/oars/generate.html
https://emn178.github.io/online-tools/sha256_checksum.html


<!--flatpak-builder build-dir io.github.swanux.hbud.yml-->
