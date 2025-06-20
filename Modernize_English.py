import srt
import os
from tqdm import tqdm
from time import sleep
from openai import OpenAI

# CONFIGURATION
BATCH_SIZE = 50  # You can experiment with values like 20–100
MODEL = "gpt-4o"
SRT_INPUT_PATH = "XXXX.srt" # Replace with name of source srt
SRT_OUTPUT_PATH = "XXXX.srt" # Replace with desired name of output srt

client = OpenAI(api_key="XXXX") # Replace with your actual OpenAI API key

# ✅ System prompt: line-by-line with 1-to-1 enforcement
SYSTEM_PROMPT = (
    "You will receive a numbered list of individual subtitle lines.\n"
    "Each line represents one sentence or phrase of dialogue or sound.\n"
    "Rewrite each line in natural modern English. Keep the numbering format: 1. <modernized line>\n"
    "Do NOT merge or split lines.\n"
    "Keep sound cues like [BELL CHIMING] unchanged.\n"
    "Return the same number of lines if possible, one numbered line per original input.\n"
    "If you must skip a line, do not renumber — just omit the line and continue."
)

def chunk_subtitles(subtitles, batch_size):
    for i in range(0, len(subtitles), batch_size):
        yield subtitles[i:i + batch_size]

def format_batch(batch):
    lines = []
    for sub in batch:
        for line in sub.content.strip().split("\n"):
            lines.append(line.strip())
    return "\n".join(f"{i + 1}. {line}" for i, line in enumerate(lines))

def parse_response(original_batch, response_text):
    # Flatten all original lines and store their order in (sub_index, line_index) form
    original_lines = []
    for sub in original_batch:
        for line in sub.content.strip().split("\n"):
            original_lines.append(line.strip())

    # Build GPT line map using their declared numbering (e.g., "1. <text>")
    gpt_lines = {}
    for line in response_text.strip().split("\n"):
        line = line.strip()
        if not line or not line[0].isdigit() or ". " not in line:
            continue
        try:
            num_str, text = line.split(". ", 1)
            index = int(num_str)
            gpt_lines[index] = text.strip()
        except ValueError:
            continue

    # Reconstruct aligned lines: fill in missing ones with [MISSING LINE]
    aligned_lines = []
    for i in range(1, len(original_lines) + 1):
        aligned_lines.append(gpt_lines.get(i, "[MISSING LINE]"))

    # Rebuild the subtitles block by block
    new_subs = []
    cursor = 0
    for sub in original_batch:
        line_count = len(sub.content.strip().split("\n"))
        updated_lines = aligned_lines[cursor:cursor + line_count]
        new_sub = srt.Subtitle(
            index=sub.index,
            start=sub.start,
            end=sub.end,
            content="\n".join(updated_lines),
            proprietary=sub.proprietary
        )
        new_subs.append(new_sub)
        cursor += line_count

    return new_subs

def send_batch_to_openai(batch_text):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": batch_text}
            ],
            temperature=0.3,
            timeout=60
        )
        return response.choices[0].message.content
    except Exception as e:
        print("❌ Error communicating with OpenAI:", e)
        return None

def save_raw_response(batch_index, response_text):
    os.makedirs("logs", exist_ok=True)
    with open(f"logs/batch_{batch_index:03}.txt", "w", encoding="utf-8") as f:
        f.write(response_text)

def main():
    print("📂 Loading subtitles...")
    with open(SRT_INPUT_PATH, 'r', encoding='utf-8') as f:
        subtitles = list(srt.parse(f.read()))

    translated_subtitles = []
    print("⚙️ Processing Batches:")
    for i, batch in enumerate(tqdm(list(chunk_subtitles(subtitles, BATCH_SIZE)))):
    # for i, batch in enumerate(tqdm(list(chunk_subtitles(subtitles, BATCH_SIZE))[:5])):
        batch_text = format_batch(batch)
        response = send_batch_to_openai(batch_text)

        if not response:
            print(f"❌ Batch {i + 1}: No response. Skipping.")
            continue

        try:
            translated = parse_response(batch, response)
            translated_subtitles.extend(translated)
        except Exception as e:
            print(f"⚠️ Batch {i + 1}: {e} — retrying once...")
            response = send_batch_to_openai(batch_text)

            try:
                translated = parse_response(batch, response)
                translated_subtitles.extend(translated)
            except Exception as e:
                print(f"❌ Batch {i + 1}: Failed again. Skipping.")
                save_raw_response(i + 1, response)
                continue

        sleep(1.5)

    if translated_subtitles:
        # First, write the full subtitle file including [MISSING LINE]
        temp_path = SRT_OUTPUT_PATH + ".raw"
        with open(temp_path, 'w', encoding='utf-8') as out_file:
            out_file.write(srt.compose(translated_subtitles))

        # Then, read it back and strip out all [MISSING LINE] lines
        with open(temp_path, 'r', encoding='utf-8') as f:
            cleaned_lines = []
            for line in f:
                if "[MISSING LINE]" not in line:
                    cleaned_lines.append(line)

        # Write final cleaned version
        with open(SRT_OUTPUT_PATH, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)

        # Optionally remove temp file
        os.remove(temp_path)

        print(f"\n✅ All subtitles saved to: {SRT_OUTPUT_PATH}")

    else:
        print("❌ No subtitles were translated.")


if __name__ == "__main__":
    main()
