from flask import Flask, request, redirect
from broker import Broker
from datetime import datetime
from producer import place_order

app    = Flask(__name__)
broker = Broker()


def badge(status: str) -> str:
    colors = {
        "success"  : "background:#2ecc8a;color:#0a3d22;",
        "dead"     : "background:#ff4f6a;color:#4a0010;",
        "retrying" : "background:#f5a623;color:#4a2c00;",
        "running"  : "background:#4f9eff;color:#002b4a;",
        "pending"  : "background:#a78bfa;color:#2d1b69;",
    }
    s = colors.get(status, "background:#ccc;color:#333;")
    return f'<span style="padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;{s}">{status.upper()}</span>'


def calc_duration(started: str, completed: str) -> str:
    if started and completed:
        fmt = "%Y-%m-%dT%H:%M:%S.%f"
        try:
            diff = datetime.strptime(completed, fmt) - datetime.strptime(started, fmt)
            return f"{round(diff.total_seconds(), 2)}s"
        except Exception:
            return "—"
    return "—"


@app.route("/order", methods=["POST"])
def add_order():
    item        = request.form.get("item")
    order_id    = int(request.form.get("order_id", 101))
    quantity    = int(request.form.get("quantity", 1))
    max_retries = int(request.form.get("max_retries", 3))

    task_map = {
        "cook_burger"  : [order_id, quantity],
        "cook_pasta"   : [order_id, quantity],
        "make_dessert" : [order_id],
    }

    args = task_map.get(item, [order_id])
    task_id = place_order(name=item, args=args, max_retries=max_retries)
    print(f"[Dashboard] Order placed: {item} → {task_id[:8]}")

    return redirect("/")

@app.route("/")
def dashboard():
    tasks = broker.get_all_tasks()
    dlq   = broker.get_dlq_tasks()

    total    = len(tasks)
    success  = sum(1 for t in tasks if t.get("status") == "success")
    dead     = sum(1 for t in tasks if t.get("status") == "dead")
    retrying = sum(1 for t in tasks if t.get("status") == "retrying")
    running  = sum(1 for t in tasks if t.get("status") == "running")

    rows = ""
    for t in tasks:
        duration = calc_duration(t.get("started_at"), t.get("completed_at"))
        rows += f"""
        <tr>
            <td>{t.get('name','')}</td>
            <td>{badge(t.get('status',''))}</td>
            <td style="text-align:center">{t.get('retry_count',0)} / {t.get('max_retries',3)}</td>
            <td>{duration}</td>
            <td style="color:green">{t.get('result','') or '—'}</td>
            <td style="color:red;font-size:12px">{t.get('error','') or '—'}</td>
            <td style="color:gray;font-size:12px">{t.get('id','')[:8]}...</td>
        </tr>
        """

    dlq_rows = ""
    for t in dlq:
        dlq_rows += f"""
        <tr>
            <td>{t.get('name','')}</td>
            <td style="color:red">{t.get('error','') or '—'}</td>
            <td style="text-align:center">{t.get('retry_count',0)}</td>
            <td style="color:gray;font-size:12px">{t.get('id','')[:8]}...</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Kitchen Dashboard</title>
    <meta http-equiv='refresh' content='20'>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            padding: 20px;
            color: #333;
        }}

        h1 {{
            font-size: 22px;
            margin-bottom: 4px;
        }}

        .note {{
            color: #777;
            font-size: 13px;
            margin-bottom: 16px;
        }}

        .form-area {{
            background: white;
            border: 1px solid #ccc;
            padding: 12px;
            margin-bottom: 20px;
        }}

        label {{
            font-size: 13px;
            color: #555;
        }}

        select, input {{
            border: 1px solid #ccc;
            padding: 5px;
            font-size: 13px;
        }}

        .btn {{
            background: #0077cc;
            color: white;
            border: none;
            padding: 8px 16px;
            cursor: pointer;
            font-size: 13px;
        }}

        .btn:hover {{
            background: #005fa3;
        }}

        .stats {{
            margin-bottom: 20px;
        }}

        .stat {{
            display: inline-block;
            background: white;
            border: 1px solid #ddd;
            padding: 10px 18px;
            margin-right: 8px;
            text-align: center;
        }}

        .stat-val {{
            font-size: 22px;
            font-weight: bold;
            color: #0077cc;
        }}

        .stat-lbl {{
            font-size: 12px;
            color: #777;
        }}

        h2 {{
            font-size: 14px;
            color: #555;
            margin: 20px 0 8px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            margin-bottom: 10px;
        }}

        th {{
            background: #e8e8e8;
            padding: 8px;
            text-align: left;
            font-size: 13px;
            border: 1px solid #ccc;
        }}

        td {{
            padding: 8px;
            border: 1px solid #ddd;
            font-size: 13px;
        }}

        tr:hover td {{
            background: #f9f9f9;
        }}

        .empty {{
            text-align: center;
            color: #999;
            padding: 20px;
        }}
    </style>
</head>
<body>

<h1>Restaurant Kitchen</h1>
<p class='note'>Auto-refreshes every 20 seconds</p>

<form class='form-area' action='/order' method='POST'>
    <label>Menu Item:</label>
    <select name='item'>
        <option value='cook_burger'>Burger</option>
        <option value='cook_pasta'>Pasta</option>
        <option value='make_dessert'>Dessert</option>
    </select>
    &nbsp;
    <label>Order ID:</label>
    <input type='number' name='order_id' value='101' style='width:80px'>
    &nbsp;
    <label>Quantity:</label>
    <input type='number' name='quantity' value='1' min='1' style='width:60px'>
    &nbsp;
    <label>Max Retries:</label>
    <input type='number' name='max_retries' value='3' min='1' style='width:70px'>
    &nbsp;
    <button class='btn' type='submit'>Place Order</button>
</form>

<div class='stats'>
    <div class='stat'>
        <div class='stat-val'>{total}</div>
        <div class='stat-lbl'>Total</div>
    </div>
    <div class='stat'>
        <div class='stat-val' style='color:green'>{success}</div>
        <div class='stat-lbl'>Success</div>
    </div>
    <div class='stat'>
        <div class='stat-val'>{running}</div>
        <div class='stat-lbl'>Running</div>
    </div>
    <div class='stat'>
        <div class='stat-val' style='color:orange'>{retrying}</div>
        <div class='stat-lbl'>Retrying</div>
    </div>
    <div class='stat'>
        <div class='stat-val' style='color:red'>{dead}</div>
        <div class='stat-lbl'>Dead</div>
    </div>
</div>

<h2>All Orders</h2>
<table>
    <thead>
        <tr>
            <th>Task</th><th>Status</th><th>Retries</th>
            <th>Duration</th><th>Result</th><th>Error</th><th>ID</th>
        </tr>
    </thead>
    <tbody>
        {rows or "<tr><td colspan='7' class='empty'>No orders yet.</td></tr>"}
    </tbody>
</table>

<h2>Dead Letter Queue</h2>
<table>
    <thead>
        <tr>
            <th>Task</th><th>Final Error</th><th>Attempts</th><th>ID</th>
        </tr>
    </thead>
    <tbody>
        {dlq_rows or "<tr><td colspan='4' class='empty'>DLQ is empty!</td></tr>"}
    </tbody>
</table>

</body>
</html>"""

if __name__ == "__main__":
    print("Dashboard → http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)