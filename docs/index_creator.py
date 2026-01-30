import os


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


def read_all_cps_dirs(root_dir):
    all_objects = []

    for cps_dir in list_cps_dirs(root_dir):
        objs = read_txt_dir(cps_dir)
        all_objects.extend(objs)

    return all_objects


def read_objects(txtfile, txt_dir):
    with open(txtfile, 'r') as f:
        # remove empty lines and strip whitespace
        lines = [l.strip() for l in f if l.strip()]

    if len(lines) % 6 != 0:
        raise ValueError("Input file does not have enough information")

    base = os.path.splitext(os.path.basename(txtfile))[0]
    html_path = os.path.join(txt_dir, base + ".html")

    return {
        "weave_id": lines[0],
        "galaxy": lines[1],
        "ob_id": lines[2],
        "mode": lines[3],
        "date": lines[4],
        "trimester": lines[5],
        "html_file": html_path
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


text = f'''
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

root_dir = "."   # or wherever the CPS directories live

objects = read_all_cps_dirs(root_dir)
objects = sort_objects(objects)

table_rows = make_table_rows(objects)

html = text.replace("<!-- TABLE_ROWS -->", table_rows)

with open("index.html", "w") as f:
    f.write(html)
