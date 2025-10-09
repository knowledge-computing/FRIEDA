#!/usr/bin/env python3
import os
import csv
import json
from html import escape

# =========================
# Paths & Config
# =========================
QUESTION_FILE = "questions_config.json"   # Each item: {question_text, image_urls[], map_count, spatial_relationship}
USER_FILE = "users.csv"                   # CSV with headers: user_id,user_name
OUTPUT_DIR = "pages"                      # Generated HTML output
ASSIGNMENTS_FILE = "assignments.json"     # Optional: mapping question_ref -> [user_id, user_id, user_id]
STARTING_IDX = 1

# Location to image repository
IMAGE_URL = "image_url"

# Where the static HTML pages are served (use a local HTTP server)
#   cd pages && python -m http.server 8001
PAGES_BASE_URL = "frontend_url"

# Your Django REST backend (submit endpoint at /api/submit/)
BACKEND_BASE_URL = "db_url"

# Validity options (two categories)
VALIDATION_OPTIONS = [
    "Can be answered",
    "Map doesn't contain information to answer the question",
]

# =========================
# Load Data
# =========================
with open(QUESTION_FILE, "r", encoding="utf-8") as f:
    questions = json.load(f)

with open(USER_FILE, "r", newline="", encoding="utf-8") as f:
    users = list(csv.DictReader(f))

if not users:
    raise SystemExit("users.csv is empty — need at least one user.")

# =========================
# Assign each question to 2 users (round-robin)
# =========================
# We also generate an internal question_ref for each question (q_0001, q_0002, ...)
question_refs = []
for idx, _ in enumerate(questions, start=STARTING_IDX):
    question_refs.append(f"q_{idx:04d}")

assignments = {ref: [] for ref in question_refs}
user_index = 0
for ref in question_refs:
    for _ in range(2):
        user = users[user_index % len(users)]
        assignments[ref].append(user["user_id"])
        user_index += 1

# Build per-user ordered list of page filenames (MUST match write-out naming)
user_pages = {u["user_id"]: [] for u in users}

for i, _ in enumerate(questions):
    ref = question_refs[i]                 # e.g., q_0001
    for uid in assignments[ref]:
        user_pages[uid].append(f"{uid}_{ref}.html")   # <-- exact same pattern as this_filename

print("Assignment summary:")
for uid, files in user_pages.items():
    print(f"  {uid}: {len(files)} page(s) -> {files[:5]}{' ...' if len(files) > 5 else ''}")

# =========================
# Styles (Google-Forms-like minimal, no purple header) + lightbox
# =========================
GOOGLE_FORMS_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
  :root {
    --g-purple: #673ab7;
    --g-purple-dark: #5e35b1;
    --g-bg: #f6f6f6;
    --g-text: #202124;
    --g-muted: #5f6368;
    --g-card: #ffffff;
    --g-border: #dadce0;
  }
  html, body { margin: 0; background: var(--g-bg); color: var(--g-text); font-family: Roboto, Arial, sans-serif; }
  .g-container { max-width: 880px; margin: 24px auto 64px auto; padding: 0 16px; }
  .g-card { background: var(--g-card); border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,.12), 0 1px 3px rgba(0,0,0,.24); border: 1px solid var(--g-border); margin-bottom: 16px; }
  .g-card-header { padding: 24px 24px 12px 24px; border-bottom: 1px solid var(--g-border); }
  .g-title { font-size: 28px; font-weight: 500; margin: 0 0 4px 0; }
  .g-subtitle { color: var(--g-muted); font-size: 14px; margin: 0; }
  .g-section { padding: 20px 24px 24px 24px; }
  .g-q-title { font-size: 18px; font-weight: 500; margin: 0 0 12px 0; }
  .g-required::after { content: " *"; color: #d93025; font-weight: 700; }
  .g-help { color: var(--g-muted); font-size: 12px; margin-top: 6px; }
  .g-img-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; margin: 12px 0 8px 0; }
  .g-img-grid img { width: 100%; height: auto; border: 1px solid var(--g-border); border-radius: 6px; background: #fff; cursor: zoom-in; }
  textarea { width: 100%; min-height: 96px; resize: vertical; padding: 10px 12px; border: 1px solid var(--g-border); border-radius: 6px; font-family: Roboto, Arial, sans-serif; font-size: 14px; box-sizing: border-box; }
  .g-radio-group { margin-top: 6px; }
  .g-radio { display: flex; align-items: center; gap: 8px; margin: 8px 0; font-size: 14px; }
  .g-actions { display: flex; justify-content: flex-start; gap: 12px; padding: 16px 24px 24px 24px; }
  .g-btn { background: var(--g-purple); color: #fff; border: none; border-radius: 24px; padding: 10px 20px; font-weight: 500; cursor: pointer; }
  .g-btn[disabled] { opacity: .6; cursor: not-allowed; }
  .g-btn:hover { background: var(--g-purple-dark); }
  details.g-instructions summary { font-weight: 500; cursor: pointer; list-style: none; }
  details.g-instructions summary::-webkit-details-marker { display:none; }
  details.g-instructions summary:after { content: "▾"; float: right; color: var(--g-muted); }
  details.g-instructions[open] summary:after { content: "▴"; }
  .g-muted-note { color: var(--g-muted); font-size: 12px; margin-left: 4px; }
  /* Image lightbox */
  .lightbox { position: fixed; inset: 0; background: rgba(0,0,0,.8); display: none; align-items: center; justify-content: center; z-index: 9999; }
  .lightbox img { max-width: 95vw; max-height: 95vh; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,.5); }
  .lightbox.visible { display: flex; }
  .lightbox:after { content: "×"; position: fixed; top: 16px; right: 24px; font-size: 28px; color: #fff; cursor: pointer; }
</style>
"""

# =========================
# Instructions Block
# =========================
INSTRUCTIONS = """
<details class="g-instructions" open>
  <summary>Instructions</summary>
  <div style="margin-top:12px;">
    <p><strong>General</strong></p>
    <ul>
      <li>If question can be answered, write answer in short answer box</li>
      <li>If answer is a text from the map, copy it as it appears</li>
    </ul>
    <p><strong>Numerical Answers</strong></p>
    <ul>
      <li>Include units as indicated on the map <em>(Don’t convert 1200m to 1.2km)</em></li>
      <li>If both map frame and ruler scale is available, <u>use the ruler scale</u></li>
      <li>If question asks for an area, use &#123;unit&#125;&#178;</li>
      <li>Use numerical values <em>(e.g., 4 instead of four)</em></li>
    </ul>
    <p><strong>Directional Answers</strong></p>
    <ul>
      <li>Use 8 cardinal directions only: North, North East, East, South East, South, South West, West, North West</li>
      <li>Write 'North' or 'South' before 'East' or 'West'</li>
      <li><strong>Notice that the north arrow compass do not always point upward</strong></li>
    </ul>
    <p><strong>Multi-Part Answers</strong></p>
    <ul>
      <li>Separate with semicolon (;) <em>(e.g., Zone A; Zone B)</em></li>
    </ul>
  </div>
</details>
"""

def write_user_start_page(uid: str, ordered_files: list[str]):
    """
    Create <uid>_start.html with the instructions and a 'Next' button.
    'Next' → last answered question for this user; if none answered → first question;
    if all answered → thankyou.html.
    """
    # Build structured info for JS (qref + url) so we can check localStorage keys.
    # Example filename pattern: "{user_id}_{qref}.html"
    items = []
    for fname in ordered_files:
        # extract qref after the first underscore and before ".html"
        try:
            qref = fname.split("_", 1)[1].removesuffix(".html")
        except Exception:
            qref = fname  # fallback; shouldn't happen with our generator
        items.append({"qref": qref, "url": f"{fname}"})

    start_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{uid} — Start</title>
  {GOOGLE_FORMS_CSS}
</head>
<body>
  <div class="g-container">
    <div class="g-card">
      <div class="g-card-header">
        <h1 class="g-title">Cartographical Reasoning Annotations</h1>
        <p class="g-subtitle">Please read the instructions below, then click Next to begin or resume.</p>
      </div>
      <div class="g-section">
        <p>Thank you for participating!</p>
        <p><strong>If you are on secret/incognito mode, please switch to regular browsing mode before starting.</strong></p>
        <p>Your progress will be saved automatically, so you can exit at any time and return to complete the annotations. When you return, you will be directed to the last unanswered questions.</p>
        <p></p>
        <p>You can find more details about the benchmark dataset in this <a href="https://docs.google.com/presentation/d/18Uyi8yrRcqPfmEPfHU6XJw8pYBatW2l3vv4OiM5GGqQ/edit?usp=sharing" target="_blank" rel="noopener">Google Slides</a>.</p>
        <p>For each question, please verify whether it can be answered (Q# Validation) using the provided map(s). If an image appears too small, click on the image. For questions with multiple images, please mark whether all images were required to correctly answer the question (Q# M). You may use tools like a ruler or calculator, but do not use online search.</p>
        {INSTRUCTIONS}
      </div>
      <div class="g-actions">
        <button id="go-next" class="g-btn">Next</button>
      </div>
    </div>
  </div>

  <script>
    (function() {{
      const USER = "{escape(uid, quote=True)}";
      // Ordered list of this user's pages (qref + url)
      const PAGES = {json.dumps(items)};

      function go() {{
        if (!PAGES.length) {{
          // No pages assigned; go to thank you.
          window.location.href = "thankyou.html";
          return;
        }}

        // Find the last answered question (highest index with answered=1)
        let lastAnsweredIndex = -1;
        for (let i = 0; i < PAGES.length; i++) {{
          const key = `answered:${{USER}}:${{PAGES[i].qref}}`;
          if (localStorage.getItem(key) === '1') lastAnsweredIndex = i;
        }}

        if (lastAnsweredIndex === -1) {{
          // None answered → go to first question
          window.location.href = PAGES[0].url;
          return;
        }}

        // Prefer next unanswered if available; otherwise last answered
        const next = (lastAnsweredIndex + 1 < PAGES.length) ? lastAnsweredIndex + 1 : lastAnsweredIndex;
        window.location.href = PAGES[next].url;
      }}

      document.getElementById('go-next').addEventListener('click', go);
    }})();
  </script>
</body>
</html>"""

    out_path = os.path.join(OUTPUT_DIR, f"{uid}_start.html")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(start_html)


# Generate a start page per user
for uid, files in user_pages.items():
    write_user_start_page(uid, files)

print("\nOpen a user's Start page like:")
some_uid = next(iter(user_pages.keys()))
print(f"  {PAGES_BASE_URL}/{some_uid}_start.html")

# =========================
# Generate Thank You page (static, not Django)
# =========================
def write_thankyou_page():
    path = os.path.join(OUTPUT_DIR, "thankyou.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Thank you</title>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap" rel="stylesheet">
<style>
  body{font-family:Roboto,Arial,sans-serif;background:#f6f6f6;color:#202124;margin:0}
  .wrap{max-width:720px;margin:80px auto;padding:32px;background:#fff;border:1px solid #dadce0;border-radius:8px;
        box-shadow:0 1px 2px rgba(0,0,0,.12),0 1px 3px rgba(0,0,0,.24)}
  h1{margin:0 0 12px 0}
  p{color:#5f6368}
  a{color:#5e35b1;text-decoration:none}
</style>
                <script>
  // Clear localStorage keys used by the survey
  (function() {
    try {
      const keys = Object.keys(localStorage);
      for (const k of keys) {
        if (k.startsWith('answered:') || k.startsWith('progress:')) {
          localStorage.removeItem(k);
        }
      }
    } catch (err) {
      console.error("Error clearing localStorage:", err);
    }
  })();
</script>
</head>
<body>
  <div class="wrap">
    <h1>Thank you for participating!</h1>
    <p>Your responses have been recorded.</p>
  </div>
</body></html>""")

# =========================
# Generate Pages
# =========================
os.makedirs(OUTPUT_DIR, exist_ok=True)
write_thankyou_page()

for i, q in enumerate(questions):
    question_ref = question_refs[i]
    qtext = q["question_text"]
    image_urls = q.get("image_urls", [])
    map_count = q.get("map_count", "Single")  # 'Single' or 'Multi'
    spatial = q.get("spatial_relationship", "Distance")  # fallback default

    # Generate a page per assigned user
    for user_id in assignments[question_ref]:
        pages_for_user = user_pages[user_id]
        this_filename = f"{user_id}_{question_ref}.html"

        try:
            idx = pages_for_user.index(this_filename)
            display_num = idx + 1
            total_num = len(pages_for_user)
        except ValueError:
            raise RuntimeError(
                f"Filename mismatch: {this_filename} not found in pages_for_user for user {user_id}. "
                f"List has: {pages_for_user}"
            )

        if idx + 1 < len(pages_for_user):
            next_url = f"{PAGES_BASE_URL}/{pages_for_user[idx+1]}"
        else:
            next_url = f"{PAGES_BASE_URL}/thankyou.html"

        # Build HTML
        html_parts = [f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{question_ref}</title>
  {GOOGLE_FORMS_CSS}
</head>
<body>
  <div class="g-container">
    <div class="g-card">
      <div class="g-card-header">
        <h1 class="g-title">Map Question</h1>
        <p class="g-subtitle">Map Survey <span class="g-muted-note">(Fields marked * are required)</span></p>
      </div>
      <div class="g-section">
        {INSTRUCTIONS}
      </div>
    </div>
"""]

        # Form card
        qtext_attr = escape(qtext, quote=True)
        map_count_attr = escape(map_count, quote=True)
        spatial_attr = escape(spatial, quote=True)
        next_url_attr = escape(next_url, quote=True)

        form_block = [f'''
    <div class="g-card">
      <form action="{BACKEND_BASE_URL}/api/submit/" method="post" id="form-{user_id}-{question_ref}">
        <input type="hidden" name="user" value="{escape(user_id, quote=True)}">
        <input type="hidden" name="question_ref" value="{escape(question_ref, quote=True)}">
        <input type="hidden" name="question_text" value="{qtext_attr}">
        <input type="hidden" name="map_count" value="{map_count_attr}">
        <input type="hidden" name="spatial_relationship" value="{spatial_attr}">
        <input type="hidden" name="next_url" value="{next_url_attr}">
        <div class="g-section">
          <div class="g-q-title">Q{display_num}/{total_num}: {escape(qtext)}</div>
          <div class="g-img-grid">
''']

        for url in image_urls:
            full_url = f"{IMAGE_URL}/{url}"
            form_block.append(f'            <img src="{escape(full_url, quote=True)}" alt="Map image">')

        form_block.append('''
          </div>
          <label class="g-q-title">Answer</label>
          <textarea name="answer" placeholder="Type your short answer here..."></textarea>

          <div style="margin-top:16px;">
            <label class="g-q-title g-required">Validation</label>
            <div class="g-radio-group">
''')

        # Two-option validity radios (required)
        for option in VALIDATION_OPTIONS:
            opt_attr = escape(option, quote=True)
            form_block.append(
                f'              <label class="g-radio"><input type="radio" name="validity" value="{opt_attr}" required> {escape(option)}</label>'
            )

        form_block.append('            </div>')

        # --- Reason (hidden unless "no info" is selected) ---
        reason_wrap_id = f'noinfo-wrap-{user_id}-{question_ref}'
        reason_text_id = f'noinfo-text-{user_id}-{question_ref}'
        noinfo_label = "Please briefly explain what information was missing (required when selecting this option):"

        form_block.append(f'''
            <div id="{reason_wrap_id}" style="display:none; margin-top:12px;">
              <label class="g-q-title">{escape(noinfo_label)}</label>
              <textarea id="{reason_text_id}" name="noinfo_reason" placeholder="e.g., The map shows roads only; no distances or names to identify the feature."></textarea>
              <div class="g-help">This field is required only when selecting “Map doesn't contain information to answer the question”.</div>
            </div>
''')

        # Necessary only for multi-map
        if map_count == "Multi":
            form_block.append('''
            <div style="margin-top:16px;">
              <label class="g-q-title">Are all images necessary to answer precisely without guessing?</label>
              <div class="g-rad io-group">
                <label class="g-radio"><input type="radio" name="necessary" value="yes"> Yes</label>
                <label class="g-radio"><input type="radio" name="necessary" value="no"> No</label>
              </div>
            </div>
''')

        # Submit button
        button_label = "Submit & Next" if not next_url.endswith("thankyou.html") else "Submit"
        form_block.append(f'''
          <div class="g-actions">
            <button class="g-btn" type="submit">{button_label}</button>
          </div>
        </div>
      </form>
    </div>
''')

        html_parts.extend(form_block)

        # Inline script:
        html_parts.append(f"""
    <script>
  (function() {{
    const USER = "{escape(user_id, quote=True)}";
    const QREF = "{escape(question_ref, quote=True)}";
    const NEXT = "{next_url_attr}";
    const answeredKey = `answered:${{USER}}:${{QREF}}`;
    const progressKey = `progress:${{USER}}`;

    function disableForm(){{
      const form = document.getElementById('form-{escape(user_id, quote=True)}-{escape(question_ref, quote=True)}');
      if (!form) return;
      form.querySelectorAll('input, textarea, button').forEach(el => el.disabled = true);
      const btn = form.querySelector('button.g-btn');
      if (btn) btn.textContent = 'Submitted';
    }}

    // ------- Image Lightbox -------
    const lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.innerHTML = '<img id="lb-img" alt="Zoomed image">';
    document.body.appendChild(lb);
    lb.addEventListener('click', () => lb.classList.remove('visible'));
    document.querySelectorAll('.g-img-grid img').forEach(img => {{
      img.addEventListener('click', () => {{
        document.getElementById('lb-img').src = img.src;
        lb.classList.add('visible');
      }});
    }});

    // Handle ok=1 first, then strip the param from the URL

    (function stripOkParam(){{
      const url = new URL(window.location.href);
      if (url.searchParams.has('ok')) {{
        url.searchParams.delete('ok');
        window.history.replaceState({{}}, '', url.toString());
      }}
    }})();

    // If saved progress points to a different page, navigate there
    const savedProgress = localStorage.getItem(progressKey);
    if (savedProgress && savedProgress !== '' && savedProgress !== 'DONE') {{
      const savedPath = savedProgress.split('#')[0];
      const thisPath = window.location.href.split('#')[0];
      if (savedPath !== thisPath) {{ window.location.replace(savedProgress); return; }}
    }}

    const form = document.getElementById('form-{escape(user_id, quote=True)}-{escape(question_ref, quote=True)}');
    if (!form) return;

    // --- Toggle the reason box when "Map doesn't contain information..." is selected ---
    const NOINFO_VALUE = "Map doesn't contain information to answer the question";
    const reasonWrap = document.getElementById("{escape(reason_wrap_id, quote=True)}");
    const reasonText = document.getElementById("{escape(reason_text_id, quote=True)}");

    function updateReasonVisibility() {{
      const chosen = form.querySelector('input[name="validity"]:checked');
      const show = !!chosen && chosen.value === NOINFO_VALUE;
      if (reasonWrap) reasonWrap.style.display = show ? 'block' : 'none';
      if (reasonText) reasonText.required = !!show;
    }}

    // initialize + bind
    Array.from(form.querySelectorAll('input[name="validity"]')).forEach(r => {{
      r.addEventListener('change', updateReasonVisibility);
    }});
    updateReasonVisibility();

    // Prevent double-submit on the client,
    // but DO NOT disable inputs before the browser serializes the form.
    let submitted = false;
    form.addEventListener('submit', function(e) {{
      if (submitted) {{ e.preventDefault(); return; }}

      // Enforce reason when the "no info" option is selected
      const chosen = form.querySelector('input[name="validity"]:checked');
      const needsReason = !!chosen && chosen.value === NOINFO_VALUE;
      if (needsReason) {{
        const val = (reasonText && reasonText.value || "").trim();
        if (!val) {{
          e.preventDefault();
          alert("Please provide a brief reason for why the map does not contain the required information.");
          if (reasonText) reasonText.focus();
          return;
        }}
      }}

      submitted = true;

      // Record progress now
      try {{
        localStorage.setItem(answeredKey, '1');
        localStorage.setItem(progressKey, NEXT ? NEXT : 'DONE');
      }} catch (err) {{}}

      // Disable only the submit button immediately (buttons don't affect payload)
      const btn = form.querySelector('button.g-btn');
      if (btn) {{
        btn.disabled = true;
        btn.textContent = 'Submitting...';
      }}

      // Then lock the rest (purely UX)
      setTimeout(() => {{
        form.querySelectorAll('input, textarea, button').forEach(el => el.disabled = true);
      }}, 100);
    }}, {{ once: true }});
  }})();
</script>
  </div>
</body>
</html>
""")

        # Write page
        output_path = os.path.join(OUTPUT_DIR, this_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(html_parts))

# Save assignments for reference
with open(ASSIGNMENTS_FILE, "w", encoding="utf-8") as f:
    json.dump(assignments, f, indent=2)

print(f"Generated {sum(len(v) for v in assignments.values())} pages in '{OUTPUT_DIR}/' and a thankyou.html")
