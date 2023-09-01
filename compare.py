import os
import time

def list_files(directory):
    with os.scandir(directory) as entries:
        return [entry.name for entry in entries if entry.is_file() and entry.name.endswith('.txt')]

def select_file(directory, prompt):
    files = list_files(directory)
    for i, filename in enumerate(files, 1):
        print(f"{i}. {filename}")

    selected = int(input(prompt)) - 1
    return files[selected]

def read_capture_to_dict(filename):
    data_dict = {}
    with open(filename, 'r') as f:
        next(f)  # skip the header line
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 5:
                data_dict[parts[1]] = {'Type': parts[0], 'Status_Code': parts[2], 'Size': parts[3], 'Height': parts[4]}
    return data_dict

def compare_captures(file1, file2):
    if not os.path.exists('./compares'):
        os.makedirs('./compares')

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    txt_output_file = f'./compares/compare-{timestamp}.txt'
    html_output_file = f'./compares/compare-{timestamp}.html'

    print(f"Generating comparison files: {txt_output_file}, {html_output_file}")

    dict1 = read_capture_to_dict(file1)
    dict2 = read_capture_to_dict(file2)

    with open(txt_output_file, 'w') as f_txt, open(html_output_file, 'w') as f_html:
        header = "Type\tURL\tOld Status Code\tNew Status Code\tOld Size\tNew Size\tOld Height\tNew Height\tFlag\n"
        f_txt.write(header)

        # HTML setup
        f_html.write("""
        <html>
        <head>
            <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .table {
                    width:100vw;
                }
                .table td {
                    padding: 10px;
                    max-width: 38vw;
                    display: table-cell;
                    text-wrap: wrap;
                    overflow-wrap: anywhere;
                    min-width: 77px;
                }
                .flag-pill {
                    display: inline-block;
                    padding: 5px 10px;
                    margin: 2px;
                    border: 1px solid #ccc;
                    border-radius: 15px;
                }
                .not-found-in-old {
                    background-color: darkblue;
                    color: white;
                }
                .not-found-in-new,
                .fatal-error {
                    background-color: red;
                    color: white;
                }
                .status-code-different {
                    background-color: pink;
                    color: black;
                }
                .size-different {
                    background-color: blue;
                    color: white;
                }
                .height-different {
                    background-color: blueviolet;
                    color: white;
                }
            </style>
        </head>
        <body>
        <table class='table table-bordered table-striped'>
            <tr>
                <th>Type</th><th>URL</th><th>Old Status Code</th><th>New Status Code</th><th>Old Size</th><th>New Size</th><th>Old Height</th><th>New Height</th><th>Flag</th>
            </tr>
        """)

        all_urls = set(dict1.keys()) | set(dict2.keys())

        for url in all_urls:
            flags = []
            details1 = dict1.get(url, {})
            details2 = dict2.get(url, {})

            old_status_code = details1.get('Status_Code', 'N/A')
            new_status_code = details2.get('Status_Code', 'N/A')

            if new_status_code == '404' or new_status_code == '400' or new_status_code == 'N/A':
                flags.append('Not found in new')

            if new_status_code == '500':
                flags.append('Fatal error')

            old_size = details1.get('Size', 'N/A')
            new_size = details2.get('Size', 'N/A')

            old_height = details1.get('Height', 'N/A')
            new_height = details2.get('Height', 'N/A')

            if old_status_code == 'N/A':
                flags.append('Not found in old')

            if old_status_code != 'N/A' and new_status_code != 'N/A':
                if old_status_code != new_status_code:
                    flags.append('Status code different')
                if old_size != new_size:
                    flags.append('Size different')
                if old_height != new_height:
                    flags.append('Height different')

            f_txt.write(f"{details1.get('Type', details2.get('Type', 'N/A'))}\t{url}\t{old_status_code}\t{new_status_code}\t{old_size}\t{new_size}\t{old_height}\t{new_height}\t{'; '.join(flags)}\n")

            flag_pills = []
            for flag in flags:
                css_class = flag.lower().replace(' ', '-')
                flag_pills.append(f'<span class="flag-pill {css_class}">{flag}</span>')

            f_html.write(f"<tr><td>{details1.get('Type', details2.get('Type', 'N/A'))}</td><td><a href='{url}' target='_blank'>{url}</a></td><td>{old_status_code}</td><td>{new_status_code}</td><td>{old_size}</td><td>{new_size}</td><td>{old_height}</td><td>{new_height}</td><td>{''.join(flag_pills)}</td></tr>")

        f_html.write("</table></body></html>")

    print("Comparison complete.")

if __name__ == "__main__":
    print("Select the first capture file (older):")
    file1 = select_file('./captures', 'Choose a file by number: ')

    print("Select the second capture file (newer):")
    file2 = select_file('./captures', 'Choose a file by number: ')

    if file1 == file2:
        print("Error: You selected the same file twice. Comparison cannot be performed.")
    else:
        full_path1 = os.path.join('./captures', file1)
        full_path2 = os.path.join('./captures', file2)

        if not (os.path.exists(full_path1) and os.path.exists(full_path2)):
            print("Error: One or both of the specified files do not exist.")
        else:
            compare_captures(full_path1, full_path2)
