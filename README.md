# TwitchStreamDownload

Prosty skrypt w Pythonie, który nagrywa transmisję na żywo z Twitcha za pomocą **streamlink** i **ffmpeg**, a po zakończeniu przepakowuje nagranie do **MP4** (bez ponownego kodowania, więc bez utraty jakości).

## Jak to działa

1. `streamlink` pobiera strumień z Twitcha i przekazuje go potokiem do `ffmpeg`.
2. `ffmpeg` zapisuje go do pliku `.ts`. Ten format jest odporny na przerwanie, więc nawet nagłe zatrzymanie nie psuje pliku.
3. Po zakończeniu nagrania plik `.ts` jest przepakowywany do `.mp4`, a `.ts` jest usuwany.

## Wymagania

- Python 3.8+
- streamlink: `python -m pip install streamlink`
- ffmpeg dostępny w PATH (sprawdź: `ffmpeg -version`)

## Użycie

```powershell
python DownloadStream.py CHANNEL
```

Można też podać pełny adres:

```powershell
python DownloadStream.py https://www.twitch.tv/CHANNEL
```

Nagrywanie zatrzymujesz klawiszami **Ctrl+C**. Skrypt poprawnie zamknie plik i przejdzie do konwersji.

## Opcje

| Opcja | Opis | Domyślnie |
|---|---|---|
| `--quality` | `best`, `worst`, `1080p60`, `720p60`, `480p`, `audio_only` itd. | `best` |
| `--output-dir` | katalog na nagrania `.ts` | `./recordings` |
| `--mp4-dir` | osobny katalog na gotowe pliki MP4 | taki sam jak `--output-dir` |
| `--no-convert` | zostawia tylko plik `.ts`, bez konwersji do MP4 | wyłączone |
| `--keep-ts` | nie usuwa `.ts` po udanej konwersji | wyłączone |

Pliki nazywane są według wzoru `channel_YYYY-MM-DD_HH-MM-SS.mp4`.

Pełną listę opcji wyświetlisz poleceniem:

```powershell
python DownloadStream.py --help
```

## Przykłady

Nagranie w 720p:

```powershell
python DownloadStream.py CHANNEL --quality 720p60
```

Nagrywanie na szybki dysk SSD, gotowy MP4 trafia na HDD:

```powershell
python DownloadStream.py CHANNEL --output-dir "D:\temp\twitch" --mp4-dir "E:\Recordings\Twitch"
```

Tylko dźwięk:

```powershell
python DownloadStream.py CHANNEL --quality audio_only
```

Nagranie bez konwersji (tylko plik `.ts`):

```powershell
python DownloadStream.py CHANNEL --no-convert
```

Lista dostępnych jakości dla kanału:

```powershell
python -m streamlink https://www.twitch.tv/CHANNEL
```

## Rozwiązywanie problemów

**„Nothing was recorded”**: kanał jest offline albo wybrana jakość nie istnieje. Sprawdź dostępne jakości poleceniem powyżej.

**„ffmpeg not found”**: dodaj folder `bin` z rozpakowanego ffmpeg do zmiennej PATH i otwórz terminal ponownie.

**„streamlink not installed”**: zainstaluj go tym samym Pythonem, którym uruchamiasz skrypt: `python -m pip install streamlink`.

**„Conversion failed”**: plik `.ts` zostaje na dysku i da się go normalnie odtworzyć (np. w VLC). Możesz spróbować przepakować go ręcznie:

```powershell
ffmpeg -i recording.ts -c copy -dn -bsf:a aac_adtstoasc recording.mp4
```
