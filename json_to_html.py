import json
import sys
from pathlib import Path


def json_to_html(json_file: str, html_file: str) -> None:
    with open(json_file, "r") as f:
        data = json.load(f)

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ruff Lint Report</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
    </head>
    <body>
        <h1>Ruff Lint Report</h1>
        <table>
            <tr>
                <th>File</th>
                <th>Line</th>
                <th>Column</th>
                <th>Code</th>
                <th>Message</th>
                <th>URL</th>
            </tr>
    """

    for item in data:
        html_content += f"""
        <tr>
            <td>{item["filename"]}</td>
            <td>{item["location"]["row"]}</td>
            <td>{item["location"]["column"]}</td>
            <td>{item["code"]}</td>
            <td>{item["message"]}</td>
            <td><a href="{item["url"]}">Link</a></td>
        </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    with open(html_file, "w") as f:
        f.write(html_content)


if __name__ == "__main__":
    input_json_file = Path(R"C:\Users\Darik\PycharmProjects\ruff-html\.ruff.json")
    output_html_file = Path(
        R"C:\Users\Darik\PycharmProjects\ruff-html\ruff-lint-report.html"
    )
    json_to_html(input_json_file, output_html_file)
