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
        duration = calc_duration(
            t.get("started_at"),
            t.get("completed_at")
        )
        rows += f"""
        <tr>
            <td>{t.get('name','')}</td>
            <td>{badge(t.get('status',''))}</td>
            <td style='text-align:center'>
                {t.get('retry_count',0)} / {t.get('max_retries',3)}
            </td>
            <td>{duration}</td>
            <td style='color:#2ecc8a'>{t.get('result','') or '—'}</td>
            <td style='color:#ff4f6a;font-size:12px'>
                {t.get('error','') or '—'}
            </td>
            <td style='color:#555;font-size:11px'>
                {t.get('id','')[:8]}...
            </td>
        </tr>
        """

    dlq_rows = ""
    for t in dlq:
        dlq_rows += f"""
        <tr>
            <td>{t.get('name','')}</td>
            <td style='color:#ff4f6a'>{t.get('error','') or '—'}</td>
            <td style='text-align:center'>{t.get('retry_count',0)}</td>
            <td style='color:#555;font-size:11px'>
                {t.get('id','')[:8]}...
            </td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Kitchen Dashboard</title>
    <meta http-equiv='refresh' content='20'>
    <style>
        * {{ box-sizing:border-box; margin:0; padding:0; }}
        body {{
            font-family: monospace;
            background: #0d0f14;
            color: #e2e6f0;
            padding: 32px;
        }}
        h1 {{ font-size:22px; margin-bottom:4px; }}
        .note {{ font-size:12px; color:#555; margin-bottom:24px; }}

        .form-card {{
            background: #13161e;
            border: 1px solid #1e2330;
            border-radius: 10px;
            padding: 20px 24px;
            margin-bottom: 28px;
            display: flex;
            gap: 16px;
            align-items: flex-end;
            flex-wrap: wrap;
        }}
        .form-group {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        .form-group label {{
            font-size: 11px;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .form-group select,
        .form-group input {{
            background: #0d0f14;
            border: 1px solid #2a3045;
            border-radius: 6px;
            color: #e2e6f0;
            padding: 8px 12px;
            font-family: monospace;
            font-size: 13px;
            outline: none;
        }}
        .form-group select:focus,
        .form-group input:focus {{
            border-color: #4f9eff;
        }}
        .btn {{
            background: #4f9eff;
            color: #002b4a;
            border: none;
            border-radius: 6px;
            padding: 9px 20px;
            font-family: monospace;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            margin-bottom: 1px;
        }}
        .btn:hover {{ background: #2ecc8a; color: #0a3d22; }}

        .stats {{
            display: flex;
            gap: 12px;
            margin-bottom: 28px;
            flex-wrap: wrap;
        }}
        .stat {{
            background: #13161e;
            border: 1px solid #1e2330;
            border-radius: 10px;
            padding: 14px 22px;
            min-width: 100px;
        }}
        .stat-val {{ font-size: 26px; font-weight: 700; }}
        .stat-lbl {{ font-size: 11px; color: #555; margin-top: 4px; }}

        h2 {{
            font-size: 11px;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin: 24px 0 10px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: #13161e;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 8px;
        }}
        th {{
            background: #1e2330;
            padding: 10px 14px;
            text-align: left;
            font-size: 11px;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        td {{
            padding: 12px 14px;
            border-top: 1px solid #1e2330;
            font-size: 13px;
        }}
        tr:hover td {{ background: #1a1d26; }}
        .empty {{
            text-align: center;
            color: #555;
            padding: 24px;
        }}
    </style>
</head>
<body>

<h1>Restaurant Kitchen</h1>
<p class='note'>Auto-refreshes every 3 seconds</p>

<!-- ── Order Form ── -->
<form class='form-card' action='/order' method='POST'>

    <div class='form-group'>
        <label>Menu Item</label>
        <select name='item'>
            <option value='cook_burger'>Burger</option>
            <option value='cook_pasta'>Pasta</option>
            <option value='make_dessert'>Dessert</option>
        </select>
    </div>

    <div class='form-group'>
        <label>Order ID</label>
        <input type='number' name='order_id' value='101' style='width:90px'>
    </div>

    <div class='form-group'>
        <label>Quantity</label>
        <input type='number' name='quantity' value='1' min='1' style='width:70px'>
    </div>

    <div class='form-group'>
        <label>Max Retries</label>
        <input type='number' name='max_retries' value='3' min='1' style='width:80px'>
    </div>

    <button class='btn' type='submit'>Place Order</button>

</form>

<div class='stats'>
    <div class='stat'>
        <div class='stat-val' style='color:#4f9eff'>{total}</div>
        <div class='stat-lbl'>Total</div>
    </div>
    <div class='stat'>
        <div class='stat-val' style='color:#2ecc8a'>{success}</div>
        <div class='stat-lbl'>Success</div>
    </div>
    <div class='stat'>
        <div class='stat-val' style='color:#4f9eff'>{running}</div>
        <div class='stat-lbl'>Running</div>
    </div>
    <div class='stat'>
        <div class='stat-val' style='color:#f5a623'>{retrying}</div>
        <div class='stat-lbl'>Retrying</div>
    </div>
    <div class='stat'>
        <div class='stat-val' style='color:#ff4f6a'>{dead}</div>
        <div class='stat-lbl'>Dead</div>
    </div>
</div>

<h2>All Orders</h2>
<table>
    <thead>
        <tr>
            <th>Task</th>
            <th>Status</th>
            <th>Retries</th>
            <th>Duration</th>
            <th>Result</th>
            <th>Error</th>
            <th>ID</th>
        </tr>
    </thead>
    <tbody>
        {rows or "<tr><td colspan='7' class='empty'>No orders yet. Place one above!</td></tr>"}
    </tbody>
</table>

<h2>Dead Letter Queue</h2>
<table>
    <thead>
        <tr>
            <th>Task</th>
            <th>Final Error</th>
            <th>Attempts</th>
            <th>ID</th>
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