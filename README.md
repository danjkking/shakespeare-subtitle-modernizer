# 🎭 Shakespeare Subtitle Modernizer

This tool modernizes Shakespearean English subtitles (like those from *Hamlet*) into clear, natural modern English using OpenAI's GPT-4 model. Unlike traditional modern translations in book or script form, this tool works directly on `.srt` subtitle files — making Shakespeare more accessible in movie format than ever before.

---

## ✨ Features

- Translates line-by-line without merging or splitting lines  
- Preserves the original subtitle structure and timing  
- Inserts placeholders for missing lines to maintain alignment  
- Strips out missing placeholders before final output for clean playback  
- Batch-based processing to comply with rate limits  

---

## 📦 Requirements

To run the tool, you need Python 3.8+ and the following packages:

```
openai
tqdm
srt
```

You can install them all with:

```bash
pip install openai tqdm srt
```

---

## 🔑 API Key Setup

You **must** have an OpenAI API key. You can get one from [platform.openai.com](https://platform.openai.com/account/api-keys). Generating subtitles for the 4-hour 1996 Hamlet cost less than $1.

In the script, update the following line with your key:

```python
client = OpenAI(api_key="your_api_key_here")
```

Or use an environment variable instead (optional but safer):

```bash
export OPENAI_API_KEY=your_api_key_here
```

And update the script to:

```python
client = OpenAI()
```

---

## 🚀 How to Use

1. Save your original `.srt` subtitle file (e.g. `Hamlet.srt`) in the same folder as the script.
2. Edit these lines at the top of the script:

```python
SRT_INPUT_PATH = "Hamlet.srt"
SRT_OUTPUT_PATH = "Hamlet_Modern_English.srt"
```

3. Run the script:

```bash
python Modernize_English.py
```

4. The output file will be saved as `Hamlet_Modern_English.srt`.  
   This version keeps all subtitle blocks aligned and removes `[MISSING LINE]` placeholders before final export.

---

## 📚 Background

Most modernizations of Shakespeare are published in book or play format. These help readers, but they’re not designed for film or real-time viewing. This tool brings that modernization into the world of video subtitles — allowing audiences to watch Shakespearean films with dialogue that feels natural and understandable today.

---

## 🤖 Credit

This tool and documentation were developed with the assistance of [ChatGPT](https://openai.com/chatgpt) from OpenAI.

