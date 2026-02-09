import os
from collections import defaultdict
import re


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
            <td>{o['galaxy']}</td>
            <td>{o['ob_id']}</td>
            <td>{o['mode']}</td>
            <td>{o['date']}</td>
            <td>{o['trimester']}</td>
            <td></td>
        </tr>
        """)

    return "\n".join(rows)


def parse_cps_version(cps_name):
    """
    Extract CPS version number from directory name.
    Example: CPSv0.92_APSv1.4 -> 0.92
    """
    m = re.search(r"CPSv([\d.]+)", cps_name)
    if m is None:
        raise ValueError(f"Cannot parse CPS version from '{cps_name}'")
    return float(m.group(1))


def read_all_cps_dirs(root_dir):
    all_objects = []

    for cps_dir in list_cps_dirs(root_dir):
        objs = read_txt_dir(cps_dir)
        all_objects.extend(objs)

    return all_objects


def read_objects(txtfile, txt_dir):
    with open(txtfile, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]

    if len(lines) % 6 != 0:
        raise ValueError("Input file does not have enough information")

    base = os.path.splitext(os.path.basename(txtfile))[0]
    html_path = os.path.join(txt_dir, base + ".html").replace(os.sep, "/")

    return {
        "weave_id": lines[0],
        "galaxy": lines[1],
        "ob_id": lines[2],
        "mode": lines[3],
        "date": lines[4],
        "trimester": lines[5],
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


def sort_objects(objects):
    return sorted(
        objects,
        key=lambda o: (o["trimester"], int(o["ob_id"]))
    )


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
  if (localStorage.getItem("loggedIn") !== "true") {{
    window.location.href = "login.html";
  }}
</script>

<button id="logout-btn" onclick="logout()">Logout</button>

<style>
  #logout-btn {{
    position: fixed;
    top: 12px;
    right: 16px;
    padding: 6px 12px;
    font-size: 14px;
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
    
            tr:nth-child(even) {{
                background-color: Moccasin;
            }}
        </style>
    
       </head>
    
       <body>
          <h1>Welcome to WEAVE-Apertif quality control data</h1>
          <p>
             Here you can find the links to quality control plots of the WEAVE LIFU data observed.
          </p>
          <p>
             For details on WEAVE, please take a look into the 
             <a href="https://ingconfluence.ing.iac.es/confluence/display/WEAV/The+WEAVE+Project" 
             target="_blank">WEAVE main website</a>.
          </p>
          <p>
             Below you can find the links for the quality control plots of each galaxy observed so far using LIFU data.
             <a href="WA_QC_plots_doc.pdf" target="_blank">In this document</a> 
             you can find further information about these plots.
          </p>
          
          <!-- CPS_DROPDOWN -->
    
    
    
        <table>
        <colgroup>
        <col style="width:250px">
        <col style="width:300px">
        <col style="width:250px">
        <col style="width:250px">
        <col style="width:250px">
        <col style="width:300px">
        </colgroup>
        <tr>
        <th><b>WEAVE ID (CNAME)</b></th>
        <th><b>Galaxy name (NED)</b></th>
        <th><b>OB ID</b></th>
        <th><b>LIFU MODE</b></th>
        <th><b>Observation date</b></th>
        <th><b>Trimester</b></th>
        <th><b>Notes</b></th>
        </tr>
        
        <!-- TABLE_ROWS -->
        
        </table>
    
          <p>
            &nbsp
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

# with open("index.html", "w") as f:
#     f.write(index_html)
