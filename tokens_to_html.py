import json
import html

def tokens_to_html(tokens: dict) -> str:
    """
    Generate a complete HTML document visualizing JWT headers and claims
    from an access_token and id_token structure.
    """

    def pretty_json(obj):
        return html.escape(json.dumps(obj, indent=2, sort_keys=True))

    access_header = pretty_json(tokens["access_token"]["header"])
    access_claims = pretty_json(tokens["access_token"]["claims"])
    id_header = pretty_json(tokens["id_token"]["header"])
    id_claims = pretty_json(tokens["id_token"]["claims"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Token Viewer</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
      background: #f6f8fa;
      color: #24292e;
      margin: 0;
      padding: 24px;
    }}

    h1 {{
      margin-bottom: 24px;
    }}

    h2 {{
      margin-top: 0;
    }}

    .token {{
      background: #ffffff;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      padding: 20px;
      margin-bottom: 24px;
    }}

    .section {{
      margin-top: 16px;
    }}

    .section-title {{
      font-weight: 600;
      margin-bottom: 8px;
      color: #0366d6;
    }}

    pre {{
      background: #0d1117;
      color: #c9d1d9;
      padding: 16px;
      border-radius: 6px;
      overflow-x: auto;
      font-size: 13px;
      line-height: 1.4;
    }}
  </style>
</head>
<body>

<h1>JWT Token Details</h1>

<div class="token">
  <h2>Access Token</h2>

  <div class="section">
    <div class="section-title">Header</div>
    <pre>{access_header}</pre>
  </div>

  <div class="section">
    <div class="section-title">Claims</div>
    <pre>{access_claims}</pre>
  </div>
</div>

<div class="token">
  <h2>ID Token</h2>

  <div class="section">
    <div class="section-title">Header</div>
    <pre>{id_header}</pre>
  </div>

  <div class="section">
    <div class="section-title">Claims</div>
    <pre>{id_claims}</pre>
  </div>
</div>

</body>
</html>
"""
