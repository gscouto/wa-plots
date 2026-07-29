import os
from collections import defaultdict
import re
import math


def fluxcal_badge(value):
    try:
        v = float(value)
        if math.isnan(v):
            raise ValueError
    except:
        return '<span class="res-box res-unknown">-</span>'

    if v >= 50:
        cls = "res-good"
    elif v >= 30:
        cls = "res-passable"
    else:
        cls = "res-bad"

    return f'<span class="res-box {cls}">{int(round(v))}</span>'


def group_by_cps(objects):
    grouped = defaultdict(list)
    for o in objects:
        grouped[o["cps_dir"]].append(o)
    return grouped


def keep_latest_cps_per_obid(objects):
    """
    For each OBID, keep only the object with the highest CPS version.
    """
    latest = {}

    for o in objects:
        obid = o["ob_id"]
        cps = o["cps_dir"]
        cps_version = parse_cps_version(cps)

        if obid not in latest:
            latest[obid] = (cps_version, o)
        else:
            if cps_version > latest[obid][0]:
                latest[obid] = (cps_version, o)

    # return only the object dicts
    return [v[1] for v in latest.values()]


def list_cps_dirs(root_dir):
    return sorted(
        os.path.join(root_dir, d)
        for d in os.listdir(root_dir)
        if os.path.isdir(os.path.join(root_dir, d)) and "CPS" in d
    )


def list_txt_files(txt_dir):
    return sorted(
        os.path.join(txt_dir, f)
        for f in os.listdir(txt_dir)
        if f.endswith(".txt")
    )


def make_dropdown(cps_pages, current=None):
    options = []

    # "All CPS" option
    selected = ' selected' if current is None else ''
    options.append(
        f'<option value="index.html"{selected}>All versions</option>'
    )

    for cps, fname in cps_pages:
        selected = ' selected' if cps == current else ''
        options.append(
            f'<option value="{fname}"{selected}>{cps}</option>'
        )

    return f"""
    <label for="cpsSelect"><b>Select CPS version:</b></label>
    <select id="cpsSelect" onchange="location = this.value;">
        {''.join(options)}
    </select>
    """


def make_table_rows(objects):
    rows = []

    for o in objects:
        rows.append(f"""
        <tr>
            <td><a href="{o['html_file']}" target="_blank">{o['weave_id']}</a></td>
            <td>{o['wa_id']}</td>
            <td>{o['galaxy']}</td>
            <td>{o['ob_id']}</td>
            <td>{o['mode']}</td>
            <td>{o['date']}</td>
            <td>{o['trimester']}</td>
            <td>{overall_badge(overall_score(o))}</td>
            <td>{resolution_badge(o['blue_res'])}</td>
            <td>{resolution_badge(o['red_res'])}</td>
            <td>{throughput_badge(o['blue_thr'])}</td>
            <td>{throughput_badge(o['red_thr'])}</td>
            <td>{wavelength_badge(o['blue_wave'])}</td>
            <td>{wavelength_badge(o['red_wave'])}</td>
            <td>{fluxcal_badge(o['fluxcal_median'])}</td>
            <td>{fluxcal_badge(o['fluxcal_std'])}</td>
            <td></td>
        </tr>
        """)

    return "\n".join(rows)


def overall_badge(value):
    if value is None:
        return '<span class="res-unknown overall-box">-</span>'

    v = float(value)

    if v >= 70:
        cls = "res-good"
    elif v >= 40:
        cls = "res-passable"
    else:
        cls = "res-bad"

    return f'<span class="res-box overall-box {cls}">{int(v)}</span>'


def overall_score(o):
    values = [
        o["blue_res"], o["red_res"],
        o["blue_thr"], o["red_thr"],
        o["blue_wave"], o["red_wave"],
        o["fluxcal_median"], o["fluxcal_std"]
    ]

    # remove invalid values if needed
    vals = [v for v in values if v is not None and not math.isnan(v)]

    if not vals:
        return None

    return sum(vals) / len(vals)


def parse_cps_version(cps_name):
    """
    Extract CPS version number from directory name.
    Example: CPSv0.92_APSv1.4 -> 0.92
    """
    m = re.search(r"CPSv([\d.]+)", cps_name)
    if m is None:
        raise ValueError(f"Cannot parse CPS version from '{cps_name}'")
    return float(m.group(1))


def parse_float(value):
    try:
        return float(value)
    except:
        return None


def read_all_cps_dirs(root_dir):
    all_objects = []

    for cps_dir in list_cps_dirs(root_dir):
        objs = read_txt_dir(cps_dir)
        all_objects.extend(objs)

    return all_objects


def read_objects(txtfile, txt_dir):
    with open(txtfile, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    if len(lines) < 15:
        raise ValueError("Input file does not have enough information")

    base = os.path.splitext(os.path.basename(txtfile))[0]
    html_path = os.path.join(txt_dir, base + ".html").replace(os.sep, "/")

    return {
        "weave_id": lines[0],
        "galaxy": lines[1],
        "ob_id": lines[2],
        "wa_id": lines[14],
        "mode": lines[3],
        "date": lines[4],
        "trimester": lines[5],
        "blue_res": int(float(lines[6])),
        "red_res": int(float(lines[7])),
        "blue_thr": int(float(lines[8])),
        "red_thr": int(float(lines[9])),
        "blue_wave": int(float(lines[10])),
        "red_wave": int(float(lines[11])),
        "fluxcal_median": parse_float(lines[12]),
        "fluxcal_std": parse_float(lines[13]),
        "html_file": html_path,
        "cps_dir": os.path.basename(txt_dir),
    }


def read_txt_dir(txt_dir):
    objects = []

    for txtfile in list_txt_files(txt_dir):
        try:
            obj = read_objects(txtfile, txt_dir)
            objects.append(obj)
        except Exception as e:
            print(f"⚠️ Skipping {txtfile}: {e}")

    return objects


def resolution_badge(value):
    try:
        v = float(value)
    except:
        return '<span class="res-unknown">-</span>'

    if v >= 50:
        cls = "res-good"
    elif v >= 30:
        cls = "res-passable"
    else:
        cls = "res-bad"

    return f'<span class="res-box {cls}">{int(v)}</span>'


def sort_objects(objects):
    return sorted(
        objects,
        key=lambda o: (o["trimester"], int(o["ob_id"]))
    )


def throughput_badge(value):
    try:
        v = float(value)
    except:
        return '<span class="res-unknown">-</span>'

    if v >= 50:
        cls = "res-good"
    elif v >= 30:
        cls = "res-passable"
    else:
        cls = "res-bad"

    return f'<span class="res-box {cls}">{int(v)}</span>'


def wavelength_badge(value):
    try:
        v = float(value)
    except:
        return '<span class="res-unknown">-</span>'

    if v >= 50:
        cls = "res-good"
    elif v >= 30:
        cls = "res-passable"
    else:
        cls = "res-bad"

    return f'<span class="res-box {cls}">{int(v)}</span>'


def write_cps_pages(grouped_objects, html_template, cps_pages):
    for cps_dir, objs in grouped_objects.items():
        objs = sort_objects(objs)
        rows = make_table_rows(objs)

        dropdown_html = make_dropdown(cps_pages, current=cps_dir)

        html = html_template.replace("<!-- CPS_DROPDOWN -->", dropdown_html)
        html = html.replace("<!-- TABLE_ROWS -->", rows)

        fname = f"index_{cps_dir}.html"
        with open(fname, "w") as f:
            f.write(html)


def write_main_index(objects, html_template, cps_pages):
    # 🔹 Keep only latest CPS per OBID
    filtered = keep_latest_cps_per_obid(objects)

    # 🔹 Sort as before
    filtered = sort_objects(filtered)

    rows = make_table_rows(filtered)
    dropdown_html = make_dropdown(cps_pages, current=None)

    html = html_template.replace("<!-- CPS_DROPDOWN -->", dropdown_html)
    html = html.replace("<!-- TABLE_ROWS -->", rows)

    with open("index.html", "w") as f:
        f.write(html)


text = f'''
<script>
  const TIMEOUT_MINUTES = 30;

  const loggedIn = localStorage.getItem("loggedIn") === "true";
  const loginTime = localStorage.getItem("loginTime");

  if (!loggedIn || !loginTime) {{
    window.location.href = "login.html";
  }} else {{
    const elapsed = (Date.now() - parseInt(loginTime, 10)) / 1000 / 60;

    if (elapsed > TIMEOUT_MINUTES) {{
      localStorage.clear();
      window.location.href = "login.html";
    }}
  }}
</script>

<button id="logout-btn" onclick="logout()">Logout</button>

<style>
  /* Center columns */
  td:nth-child(7),
  td:nth-child(8),
  td:nth-child(9),
  td:nth-child(10),
  td:nth-child(11),
  td:nth-child(12),
  td:nth-child(13),
  td:nth-child(14),
  td:nth-child(15),
  th:nth-child(7),
  th:nth-child(8),
  th:nth-child(9),
  th:nth-child(10),
  th:nth-child(11),
  th:nth-child(12),
  th:nth-child(13),
  th:nth-child(14),
  th:nth-child(15) {{
    text-align: center;
  }}

  /* Base box */
  .res-box {{
    display: inline-block;
    min-width: 32px;
    padding: 4px 6px;
    border-radius: 6px;
    font-weight: bold;
    text-align: center;
    color: white;
    font-size: 14px;
  }}
  
  /* Overall score styling */
  .overall-box {{
    font-size: 16px;
    min-width: 40px;
    padding: 6px 8px;
    border: 2px solid black;
    box-shadow: 0 0 6px rgba(0,0,0,0.3);
    transform: scale(1.1);
  }}

  /* Colors */
  .res-good {{
    background-color: #2ecc71;  /* green */
  }}

  .res-passable {{
    background-color: #f1c40f;  /* yellow */
    color: black;
  }}

  .res-bad {{
    background-color: #e74c3c;  /* red */
  }}

  .res-unknown {{
    background-color: gray;
    color: white;
  }}

  th {{
  cursor: pointer;
  }}
</style>

<script>
  function logout() {{
    localStorage.removeItem("loggedIn");
    localStorage.removeItem("loginTime");
    window.location.href = "login.html";
  }}
</script>

<script>
  function refreshSession() {{
    localStorage.setItem("loginTime", Date.now());
  }}

  document.addEventListener("click", refreshSession);
  document.addEventListener("keydown", refreshSession);
</script>

<script>
let sortDirection = {{}};
let currentSortedCol = null;

function getCellValue(td) {{
  const sortKey = td.getAttribute("data-sort");
  if (sortKey !== null) return sortKey;

  const text = td.textContent.trim();
  const num = parseFloat(text);
  if (!isNaN(num) && text.match(/^\d+(\.\d+)?$/)) return num;

  return text.toLowerCase();
}}

function sortTable(colIndex) {{
  const table = document.getElementById("qc-table");
  const tbody = table.tBodies[0];
  const rows = Array.from(tbody.rows);

  // toggle direction
  sortDirection[colIndex] = !sortDirection[colIndex];
  const dir = sortDirection[colIndex] ? 1 : -1;

  // sort rows
  rows.sort((a, b) => {{
    const A = getCellValue(a.cells[colIndex]);
    const B = getCellValue(b.cells[colIndex]);

    if (A < B) return -1 * dir;
    if (A > B) return 1 * dir;
    return 0;
  }});

  rows.forEach(row => tbody.appendChild(row));

  // 🔽 UPDATE ARROWS
  updateSortIndicators(colIndex, dir);
}}

function updateSortIndicators(colIndex, dir) {{
  const headers = document.querySelectorAll("#qc-table th");

  headers.forEach((th, i) => {{
    // remove existing arrows
    th.innerHTML = th.textContent.replace(/[\u2191\u2193]/g, "").trim();

    if (i === colIndex) {{
      const arrow = dir === 1 ? " ↑" : " ↓";
      th.innerHTML += arrow;
    }}
  }});
}}
</script>

    <html>
       <head>
          <title>WEAVE Apertif Quality Assurance</title>
    
        <!-- CSS style to set alternate table
                row using color -->
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
            }}
    
            th, td {{
                text-align: left;
                padding: 8px;
            }}
            
            tbody tr:nth-child(odd) {{
              background-color: #f7f7f7;
            }}
            
            tbody tr:nth-child(even) {{
              background-color: #eaeaea;
            }}
            
            tr:hover {{
              background-color: #dcdcdc;
            }}
        </style>
    
       </head>
    
       <body>
          <h1>Welcome to WEAVE-Apertif quality control data</h1>
          <p>
             Here you can find the links to quality control plots of the WEAVE LIFU data observed. <br>
             For details on WEAVE, please take a look into the 
             <a href="https://ingconfluence.ing.iac.es/confluence/display/WEAV/The+WEAVE+Project" 
             target="_blank">WEAVE main website</a>. <br>
             Below you can find the links for the quality control plots of each galaxy OB observed so far using LIFU 
             data. <a href="WA_QC_plots_doc.pdf" target="_blank">In this document</a> you can find further information 
             about these plots. <br>
             Details on the values shown in the table columns are given in the bottom of this page. 
          </p>
          
          <!-- CPS_DROPDOWN -->
    
    
    
        <table id="qc-table">
            <colgroup>
            <col style="width:200px">
            <col style="width:200px">
            <col style="width:200px">
            <col style="width:100px">
            <col style="width:100px">
            <col style="width:100px">
            <col style="width:100px">
            <col style="width:60px">
            <col style="width:60px">
            <col style="width:60px">
            <col style="width:60px">
            <col style="width:60px">
            <col style="width:60px">
            <col style="width:60px">
            <col style="width:60px">
            <col style="width:60px">
            <col style="width:150px">
            </colgroup>
            <thead>
                <tr>
                    <th onclick="sortTable(0)">WEAVE ID (CNAME)</th>
                    <th onclick="sortTable(1)">WA_ID</th>
                    <th onclick="sortTable(2)">Galaxy name (NED)</th>
                    <th onclick="sortTable(3)">OB ID</th>
                    <th onclick="sortTable(4)">LIFU Mode</th>
                    <th onclick="sortTable(5)">Observation date</th>
                    <th onclick="sortTable(6)">Trimester</th>
                    <th onclick="sortTable(7)">QC score</th>
                    <th onclick="sortTable(8)">Blue Res</th>
                    <th onclick="sortTable(9)">Red Res</th>
                    <th onclick="sortTable(10)">Blue Thr</th>
                    <th onclick="sortTable(11)">Red Thr</th>
                    <th onclick="sortTable(12)">Blue Wave</th>
                    <th onclick="sortTable(13)">Red Wave</th>
                    <th onclick="sortTable(14)">Flux Cal Median</th>
                    <th onclick="sortTable(15)">Flux Cal Std</th>
                    <th onclick="sortTable(16)">Notes</th>
                </tr>
            </thead>
        
            <tbody>
            <!-- TABLE_ROWS -->
            </tbody>
        
        </table>
    
          <p>
            &nbsp
          </p>
          <p>
            <div style="margin-top: 15px; margin-bottom: 15px;">
              <b>QC Score:</b>
              <p>
              These values represent the overall score of the quality control parameters used to analyse the data. <br>
              They are given as the values average of all parameters listed below (shown in the numbered columns). <br>
              Color-coded classification follows the values below:
              </p>
              <ul style="margin-top: 5px;">
                <li><span class="res-box res-good">70+</span> Good</li>
                <li><span class="res-box res-passable">40–69</span> Passable</li>
                <li><span class="res-box res-bad">0–39</span> Bad</li>
              </ul>
            </div>
          </p>
          <p>
            <div style="margin-top: 15px; margin-bottom: 15px;">
              <b>Spectral Resolution Values (Blue/Red Res):</b>
              <p>
              This parameter is estimated using L0 (singles) files. <br>
              These values represent the percentage of measured sky lines resolution (R) above 90% of the nominal value 
              along all wavelengths and fiber positions. <br>
              For example: in low resolution mode, where the nominal resolution is R = 2500, this number represents the 
              percentage of measured sky lines with R > 2350. <br>
              Color-coded classification follows the values below:
              </p>
              <ul style="margin-top: 5px;">
                <li><span class="res-box res-good">50+</span> Good</li>
                <li><span class="res-box res-passable">30–49</span> Passable</li>
                <li><span class="res-box res-bad">0–29</span> Bad</li>
              </ul>
            </div>
          </p>
          <p>
            <div style="margin-top: 15px; margin-bottom: 15px;">
              <b>Fiber Throughput Values (Blue/Red Thr):</b>
              <p>
              This parameter is estimated using L0 (singles) files. <br>
              These values represent the percentage of fiber presenting median integrated sky flux within 1% of the 
              overall median sky fluxes (measured within all fibers). <br>
              Color-coded classification follows the values below:
              </p>
              <ul style="margin-top: 5px;">
                <li><span class="res-box res-good">50+</span> Good</li>
                <li><span class="res-box res-passable">30–49</span> Passable</li>
                <li><span class="res-box res-bad">0–29</span> Bad</li>
              </ul>
            </div>
          </p>
          <p>
            <div style="margin-top: 15px; margin-bottom: 15px;">
              <b>Wavelength Calibration Values (Blue/Red Wave):</b>
              <p>
              This parameter is estimated using L0 (singles) files. <br>
              These values represent the percentage of fibers showing median sky lines wavelength offsets lower than 
              20% of the spectral pixel size. <br>
              For example: in low resolution mode (with spectral pixes size of 0.5A), the value shows the percentage of 
              fibers with median (calculate over all measured sky lines) wavelength offsets below 0.1A (in absolute 
              numbers). <br>
              Color-coded classification follows the values below:
              </p>
              <ul style="margin-top: 5px;">
                <li><span class="res-box res-good">50+</span> Good</li>
                <li><span class="res-box res-passable">30–49</span> Passable</li>
                <li><span class="res-box res-bad">0–29</span> Bad</li>
              </ul>
            </div>
          </p>
          <p>
            <div style="margin-top: 15px; margin-bottom: 15px;">
              <b>Flux Calibration Values (Flux Cal Median/Std):</b>
              <p>
              This parameter is estimated using L0 (singles) files. <br>
              These values are obtained in the color magnitudes differences plots, which are calculated comparing the
              estimated magnitudes in g, r and i bands within the single files with the values given in the input 
              catalogues found the in the fibtables. <br>
              Median values are represented by the dashed lines in these plots. In this table the parameter value is 
              given by the equation: median = 100 * (1 - (Δ mag/0.5)), where Δ mag is the mean difference taking into 
              account (g-r), (r-i) and (g-i) colors. <br>
              This equation is = 0 when the median color difference is Δ mag = 0.5 dex (or above), while it has = 100 
              when the difference is Δ mag = 0. <br>
              Std values are represented by the gray filled region in these plots. The parameter values in this table 
              follows the same equation as for the median values mentioned above, with 100 when std = 0 and 0 when 
              std = 0.5 dex.<br>
              Color-coded classification follows the values below:
              </p>
              <ul style="margin-top: 5px;">
                <li><span class="res-box res-good">50+</span> Good</li>
                <li><span class="res-box res-passable">30–49</span> Passable</li>
                <li><span class="res-box res-bad">0–29</span> Bad</li>
              </ul>
            </div>
          </p>
          <p>
             If you have any questions, please send an email to gcouto at aip.de
          </p>
    
       </body>
    </html>
    '''

root_dir = "."

objects = read_all_cps_dirs(root_dir)
objects = sort_objects(objects)

grouped = group_by_cps(objects)

cps_pages = sorted(
    ((cps, f"index_{cps}.html") for cps in grouped),
    key=lambda x: parse_cps_version(x[0])
)

write_cps_pages(grouped, text, cps_pages)
write_main_index(objects, text, cps_pages)
