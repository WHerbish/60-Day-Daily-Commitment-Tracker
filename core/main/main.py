from flask import Flask, request, jsonify
import os, signal, json, calendar
from datetime import date

app = Flask(__name__)

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "resources", "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def build_buttons_html(year, month):
    today = date.today()
    num_days = calendar.monthrange(year, month)[1]
    html = ""
    for day in range(1, num_days + 1):
        d = date(year, month, day)
        abbr = d.strftime("%a")
        col = ((day - 1) % 7) + 1
        row = ((day - 1) // 7) + 1
        is_today = (d == today)
        today_class = ' today' if is_today else ''
        html += f"""
        <button id="day-{day}" class="{today_class.strip()}" onclick="selectDay({day})" style="grid-column: {col}; grid-row: {row};">
            <span class="abbr">{abbr}</span>
            <span class="daynum">{day}</span>
            <div class="day-progress-bar" style="visibility:hidden;"><div class="day-progress-fill"></div></div>
        </button>"""
    return html

@app.route("/")
def home():
    today = date.today()
    year, month = today.year, today.month
    month_name = today.strftime("%B %Y")
    config = load_config()
    buttons_html = build_buttons_html(year, month)
    saved_name = config.get("name", "")

    return """
    <style>
        body {
            background: #f9f9f9;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding-top: 40px;
            min-height: 100vh;
            margin: 0;
            font-family: Helvetica, Arial, sans-serif;
        }
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 70px);
            grid-template-rows: repeat(5, 70px);
            gap: 8px;
            margin-bottom: 0;
            border: none;
            outline: none;
        }
        .calendar-grid button {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 70px;
            width: 70px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            box-shadow: 1px 2px 4px rgba(0,0,0,0.2);
            font-family: Helvetica, Arial, sans-serif;
            padding: 0;
            background-color: white;
        }
        .calendar-grid button:hover {
            box-shadow: 2px 3px 6px rgba(0,0,0,0.3);
            border: 2px solid #C8A2C8;
            transform: translateY(-1px);
        }
        .calendar-grid button.selected {
            border: 4px solid #C8A2C8;
        }
        .calendar-grid button.today:not(:hover):not(.selected) {
            border: 3px solid transparent;
            border-image: repeating-linear-gradient(
                45deg,
                #C8A2C8 0px, #C8A2C8 4px,
                white 4px, white 8px
            ) 1;
        }
        .abbr {
            font-size: 11px;
            color: #999;
        }
        .daynum {
            font-size: 20px;
        }
        .day-progress-bar {
            width: 80%;
            height: 4px;
            background: #e0e0e0;
            border-radius: 2px;
            margin-top: 4px;
            overflow: hidden;
        }
        .day-progress-fill {
            height: 100%;
            width: 0%;
            background: #C8A2C8;
            border-radius: 2px;
            transition: width 0.3s;
        }
        #quitBtn {
            font-family: Helvetica, Arial, sans-serif;
            background: #ffffff;
            border: none;
            padding: 10px 28px;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 1px 2px 4px rgba(0,0,0,0.2);
            border-radius: 4px;
            width: 120px;
        }
        #quitBtn:hover {
            box-shadow: 2px 3px 6px rgba(0,0,0,0.3);
        }
        .panel {
            background: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 20px 24px;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.1);
            display: inline-flex;
            flex-direction: column;
            align-items: flex-start;
            margin-bottom: 20px;
        }
        .month-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            margin: 0 0 8px 0;
        }
        .month-label {
            font-size: 18px;
            font-weight: bold;
            color: #555;
            margin: 0;
        }
        .nav-btn {
            background: white;
            border: none;
            border-radius: 4px;
            width: 28px;
            height: 28px;
            cursor: pointer;
            font-size: 14px;
            box-shadow: 1px 2px 4px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
        }
        .nav-btn:hover {
            box-shadow: 2px 3px 6px rgba(0,0,0,0.3);
            border: 1px solid #C8A2C8;
            transform: translateY(-1px);
        }
        .greeting {
            font-size: 15px;
            color: #777;
            margin: 6px 0 16px 0;
        }
        .panel hr {
            width: 100%;
            border: none;
            border-top: 2px solid #f9f9f9;
            margin: 0 0 16px 0;
        }
        .panels-row {
            display: flex;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 20px;
        }
        .tasks-panel {
            background: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 20px 24px;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            width: 330px;
            align-self: stretch;
            box-sizing: border-box;
        }
        .tasks-label {
            font-size: 18px;
            font-weight: bold;
            color: #555;
            margin: 0 0 8px 0;
        }
        .tasks-panel hr {
            width: 100%;
            border: none;
            border-top: 2px solid #f9f9f9;
            margin: 0 0 16px 0;
        }
        .add-task-row {
            display: none;
            align-items: center;
            gap: 10px;
            margin-top: 12px;
        }
        .add-btn {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #C8A2C8;
            border: none;
            color: white;
            font-size: 20px;
            line-height: 1;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 1px 2px 4px rgba(0,0,0,0.2);
            flex-shrink: 0;
        }
        .add-btn:hover {
            box-shadow: 2px 3px 6px rgba(0,0,0,0.3);
            border: 1px solid #C8A2C8;
            transform: translateY(-1px);
        }
        .add-task-label {
            font-size: 13px;
            color: #888;
        }
        .task-item {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 10px;
        }
        .task-item input[type="checkbox"] {
            accent-color: #C8A2C8;
            width: 16px;
            height: 16px;
            cursor: pointer;
            flex-shrink: 0;
        }
        .task-item label {
            font-size: 13px;
            color: #444;
            flex: 1;
        }
        .delete-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 15px;
            color: #bbb;
            padding: 0;
            line-height: 1;
            flex-shrink: 0;
        }
        .delete-btn:hover { color: #e57373; }
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.3);
            z-index: 100;
            align-items: center;
            justify-content: center;
        }
        .modal-overlay.active { display: flex; }
        .modal {
            background: white;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 4px 8px 24px rgba(0,0,0,0.2);
            width: 320px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .modal h3 {
            margin: 0;
            font-size: 16px;
            color: #555;
        }
        .modal label {
            font-size: 13px;
            color: #666;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .modal input[type="text"], .modal input[type="number"] {
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 6px 8px;
            font-size: 13px;
            font-family: Helvetica, Arial, sans-serif;
            outline: none;
        }
        .modal input:focus { border-color: #C8A2C8; }
        .modal-btns {
            display: flex;
            justify-content: flex-end;
            gap: 8px;
        }
        .modal-btns button {
            font-family: Helvetica, Arial, sans-serif;
            font-size: 13px;
            padding: 6px 16px;
            border-radius: 4px;
            cursor: pointer;
            border: 1px solid #ccc;
            background: white;
        }
        .modal-btns button.primary {
            background: #C8A2C8;
            color: white;
            border-color: #C8A2C8;
        }
    </style>
    <h1>Daily Commitment Tracker</h1>
    <p id="greeting" class="greeting"></p>
    <div class="panels-row">
        <div class="panel" style="margin-bottom:0;">
            <div class="month-header">
                <p id="month-label" class="month-label">""" + month_name + """</p>
                <div style="display:flex; gap:6px;">
                    <button class="nav-btn" onclick="changeMonth(-1)">&lt;</button>
                    <button class="nav-btn" onclick="goToToday()" style="width:auto; padding:0 8px; font-size:12px; font-weight:bold;">Today</button>
                    <button class="nav-btn" onclick="changeMonth(1)">&gt;</button>
                </div>
            </div>
            <hr>
            <div id="calendar-grid" class="calendar-grid">""" + buttons_html + """
            </div>
        </div>
        <div class="tasks-panel">
            <p class="tasks-label">Tasks</p>
            <hr>
            <p id="selected-date" style="font-size:14px; color:#C8A2C8; margin:0; font-weight:bold">Select a date.</p>
            <div id="task-list"></div>
            <div class="add-task-row">
                <button class="add-btn" onclick="openModal()">+</button>
                <span class="add-task-label">Add Task</span>
            </div>
        </div>
    </div>
    <button id="quitBtn" onclick="quit()">Quit</button>

    <div class="modal-overlay" id="modal-overlay">
        <div class="modal">
            <h3>New Task</h3>
            <label>Describe your Task:
                <input type="text" id="task-desc" placeholder="e.g. Go for a run">
            </label>
            <label>How many days will you do this:
                <input type="number" id="task-days" placeholder="e.g. 7" min="1">
            </label>
            <div class="modal-btns">
                <button onclick="closeModal()">Cancel</button>
                <button class="primary" onclick="submitTask()">Add</button>
            </div>
        </div>
    </div>
    <script>
        let currentYear = """ + str(year) + """;
        let currentMonth = """ + str(month) + """;

        const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
        const dayNames = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];

        let selectedYear = null, selectedMonth = null, selectedDay = null;

        function selectDay(day) {
            document.querySelectorAll('#calendar-grid button').forEach(b => b.classList.remove('selected'));
            document.getElementById('day-' + day).classList.add('selected');
            selectedYear = currentYear;
            selectedMonth = currentMonth;
            selectedDay = day;
            const d = new Date(currentYear, currentMonth - 1, day);
            const label = `${dayNames[d.getDay()]}, ${monthNames[currentMonth - 1]} ${day}, ${currentYear}`;
            document.getElementById('selected-date').textContent = label;
            document.querySelector('.add-task-row').style.display = 'flex';
            loadTasks();
        }

        function restoreSelection() {
            if (selectedDay && selectedYear === currentYear && selectedMonth === currentMonth) {
                document.getElementById('day-' + selectedDay).classList.add('selected');
            }
        }

        async function goToToday() {
            const today = new Date();
            const todayYear = today.getFullYear();
            const todayMonth = today.getMonth() + 1;
            const todayDay = today.getDate();
            if (currentYear !== todayYear || currentMonth !== todayMonth) {
                currentYear = todayYear;
                currentMonth = todayMonth;
                const res = await fetch(`/month?year=${currentYear}&month=${currentMonth}`);
                const data = await res.json();
                document.getElementById('month-label').textContent = data.month_name;
                document.getElementById('calendar-grid').innerHTML = data.buttons_html;
            }
            selectDay(todayDay);
        }

        async function changeMonth(direction) {
            currentMonth += direction;
            if (currentMonth > 12) { currentMonth = 1; currentYear++; }
            if (currentMonth < 1)  { currentMonth = 12; currentYear--; }
            const res = await fetch(`/month?year=${currentYear}&month=${currentMonth}`);
            const data = await res.json();
            document.getElementById('month-label').textContent = data.month_name;
            document.getElementById('calendar-grid').innerHTML = data.buttons_html;
            restoreSelection();
            loadMonthStatus();
        }

        (async function initGreeting() {
            let name = """ + json.dumps(saved_name) + """;
            if (!name) {
                name = prompt("Please enter your first name:");
                if (name && name.trim()) {
                    name = name.trim().charAt(0).toUpperCase() + name.trim().slice(1).toLowerCase();
                    await fetch('/save-name', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: name })
                    });
                }
            }
            if (name) {
                const hour = new Date().getHours();
                let greeting;
                if (hour >= 1 && hour < 12)       greeting = "Good morning, " + name + ".";
                else if (hour >= 12 && hour < 14)  greeting = "Good day, " + name + ".";
                else if (hour >= 14 && hour < 18)  greeting = "Good afternoon, " + name + ".";
                else                               greeting = "Good evening, " + name + ".";
                document.getElementById('greeting').textContent = greeting;
            }
        })();

        loadMonthStatus();

        function updateDayButton(day, total, done) {
            const btn = document.getElementById('day-' + day);
            if (!btn) return;
            const bar = btn.querySelector('.day-progress-bar');
            const fill = btn.querySelector('.day-progress-fill');
            if (total === 0) {
                bar.style.visibility = 'hidden';
                btn.style.backgroundColor = 'white';
                return;
            }
            bar.style.visibility = 'visible';
            fill.style.width = (done / total * 100) + '%';
            const hour = new Date().getHours();
            if (done === total) {
                btn.style.backgroundColor = '#d4f5d4';
            } else if (done > 0) {
                btn.style.backgroundColor = '#fff9c4';
            } else if (hour >= 20) {
                btn.style.backgroundColor = '#ffd6d6';
            } else {
                btn.style.backgroundColor = 'white';
            }
        }

        async function loadMonthStatus() {
            const res = await fetch(`/month-tasks?year=${currentYear}&month=${currentMonth}`);
            const data = await res.json();
            for (const [day, status] of Object.entries(data)) {
                updateDayButton(parseInt(day), status.total, status.done);
            }
        }

        function openModal() {
            document.getElementById('task-desc').value = '';
            document.getElementById('task-days').value = '';
            document.getElementById('modal-overlay').classList.add('active');
            document.getElementById('task-desc').focus();
        }

        function closeModal() {
            document.getElementById('modal-overlay').classList.remove('active');
        }

        function renderTasks(tasks) {
            const list = document.getElementById('task-list');
            list.innerHTML = '';
            tasks.forEach(task => {
                const dateKey = `${selectedYear}-${selectedMonth}-${selectedDay}`;
                const checked = task.checked[dateKey] || false;
                const item = document.createElement('div');
                item.className = 'task-item';
                item.innerHTML = `
                    <input type="checkbox" id="task-${task.id}" ${checked ? 'checked' : ''}
                        onchange="toggleTask('${task.id}', this.checked)">
                    <label for="task-${task.id}">${task.desc}</label>
                    <button class="delete-btn" onclick="deleteTask('${task.id}')" title="Remove task">&#128465;</button>`;
                list.appendChild(item);
            });
        }

        async function loadTasks() {
            if (!selectedDay) return;
            const res = await fetch(`/get-tasks?year=${selectedYear}&month=${selectedMonth}&day=${selectedDay}`);
            const data = await res.json();
            renderTasks(data.tasks);
        }

        async function submitTask() {
            const desc = document.getElementById('task-desc').value.trim();
            const days = parseInt(document.getElementById('task-days').value) || 1;
            if (!desc) return;
            await fetch('/save-task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ desc, days, year: selectedYear, month: selectedMonth, day: selectedDay })
            });
            await loadTasks();
            loadMonthStatus();
            closeModal();
        }

        async function deleteTask(id) {
            await fetch('/delete-task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id })
            });
            await loadTasks();
            loadMonthStatus();
        }

        async function toggleTask(id, checked) {
            const dateKey = `${selectedYear}-${selectedMonth}-${selectedDay}`;
            await fetch('/toggle-task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, date: dateKey, checked })
            });
            loadMonthStatus();
        }

        document.getElementById('modal-overlay').addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });

        async function quit() {
            await fetch('/quit', { method: 'POST' });
            window.close();
        }
    </script>
    """

@app.route("/month-tasks")
def month_tasks():
    year = int(request.args.get("year"))
    month = int(request.args.get("month"))
    num_days = calendar.monthrange(year, month)[1]
    config = load_config()
    tasks = config.get("tasks", [])
    result = {}
    for day in range(1, num_days + 1):
        requested = date(year, month, day)
        date_key = f"{year}-{month}-{day}"
        day_tasks = []
        for task in tasks:
            sy, sm, sd = (int(x) for x in task["start"].split("-"))
            start = date(sy, sm, sd)
            end = date.fromordinal(start.toordinal() + task["days"] - 1)
            if start <= requested <= end:
                day_tasks.append(task)
        total = len(day_tasks)
        done = sum(1 for t in day_tasks if t["checked"].get(date_key, False))
        result[str(day)] = {"total": total, "done": done}
    return jsonify(result)

@app.route("/month")
def get_month():
    year = int(request.args.get("year"))
    month = int(request.args.get("month"))
    config = load_config()
    month_name = date(year, month, 1).strftime("%B %Y")
    buttons_html = build_buttons_html(year, month)
    return jsonify({"month_name": month_name, "buttons_html": buttons_html})

@app.route("/save-name", methods=["POST"])
def save_name():
    data = request.get_json()
    config = load_config()
    config["name"] = data["name"]
    save_config(config)
    return "", 204


@app.route("/save-task", methods=["POST"])
def save_task():
    data = request.get_json()
    config = load_config()
    tasks = config.get("tasks", [])
    import time
    task = {
        "id": str(int(time.time() * 1000)),
        "desc": data["desc"],
        "days": data["days"],
        "start": f"{data['year']}-{data['month']}-{data['day']}",
        "checked": {}
    }
    tasks.append(task)
    config["tasks"] = tasks
    save_config(config)
    return "", 204

@app.route("/get-tasks")
def get_tasks():
    year = int(request.args.get("year"))
    month = int(request.args.get("month"))
    day = int(request.args.get("day"))
    requested = date(year, month, day)
    config = load_config()
    result = []
    for task in config.get("tasks", []):
        sy, sm, sd = (int(x) for x in task["start"].split("-"))
        start = date(sy, sm, sd)
        end = date.fromordinal(start.toordinal() + task["days"] - 1)
        if start <= requested <= end:
            result.append(task)
    return jsonify({"tasks": result})

@app.route("/delete-task", methods=["POST"])
def delete_task():
    data = request.get_json()
    config = load_config()
    config["tasks"] = [t for t in config.get("tasks", []) if t["id"] != data["id"]]
    save_config(config)
    return "", 204

@app.route("/toggle-task", methods=["POST"])
def toggle_task():
    data = request.get_json()
    config = load_config()
    for task in config.get("tasks", []):
        if task["id"] == data["id"]:
            task["checked"][data["date"]] = data["checked"]
            break
    save_config(config)
    return "", 204

@app.route("/quit", methods=["POST"])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return "Shutting down..."

if __name__ == "__main__":
    import threading, webbrowser
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Timer(1, lambda: webbrowser.open("http://localhost:8080")).start()
    app.run(port=8080, debug=True)
