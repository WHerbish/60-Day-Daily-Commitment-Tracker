from flask import Flask, request, jsonify
import os, signal, json, time
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

def find_task(tasks, task_id):
    return next((t for t in tasks if t["id"] == task_id), None)

@app.route("/")
def home():
    config = load_config()
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
        #quitBtn {
            position: fixed;
            bottom: 16px;
            right: 20px;
            background: none;
            border: none;
            font-family: Helvetica, Arial, sans-serif;
            font-size: 15px;
            color: #777;
            cursor: pointer;
            padding: 0;
        }
        #quitBtn:hover { color: #555; }
        .greeting {
            font-size: 15px;
            color: #777;
            margin: 6px 0 16px 0;
        }
        .add-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 24px;
            cursor: pointer;
        }
        .add-row:hover .add-btn {
            box-shadow: 2px 3px 6px rgba(0,0,0,0.3);
        }
        .add-btn {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #C8A2C8;
            border: none;
            color: white;
            font-size: 20px;
            font-weight: bold;
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
            font-size: 15px;
            color: #777;
        }
        .task-cards {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 20px;
            max-width: calc(560px * 3 + 16px * 2);
        }
        .task-card {
            background: #ffffff;
            border-radius: 8px;
            padding: 20px 24px;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.1);
            width: 560px;
            box-sizing: border-box;
        }
        .task-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }
        .tick-btn {
            width: 36px;
            height: 36px;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .task-card-title {
            font-size: 15px;
            font-weight: bold;
            color: #555;
            margin: 0 0 4px 0;
            outline: none;
            border-radius: 3px;
            cursor: text;
            word-break: break-word;
        }
        .task-card-title:focus {
            background: #f0f0f0;
            padding: 1px 5px;
            margin-left: -5px;
        }
        .task-card-date {
            font-size: 12px;
            color: #777;
            margin: 0;
        }
        .delete-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 18px;
            color: #555;
            padding: 0;
            line-height: 1;
        }
        .task-card hr {
            border: none;
            border-top: 1px solid #e8e8e8;
            margin: 0 0 16px 0;
        }
        .days-grid {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 6px;
        }
        .day-btn {
            aspect-ratio: 1;
            border: none;
            border-radius: 4px;
            cursor: default;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            line-height: 1.3;
            font-family: Helvetica, Arial, sans-serif;
        }
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
        .modal input[type="text"] {
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 6px 8px;
            font-size: 13px;
            font-family: Helvetica, Arial, sans-serif;
            outline: none;
        }
        .modal input:focus { border-color: #C8A2C8; }
        .colour-label {
            font-size: 13px;
            color: #666;
            margin: 0;
        }
        .colour-swatches {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .swatch {
            width: 26px;
            height: 26px;
            border-radius: 50%;
            cursor: pointer;
            border: 2px solid transparent;
            box-sizing: border-box;
            flex-shrink: 0;
        }
        .swatch.selected { border-color: #444; }
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
    <h1>60-Day Daily Commitment Tracker</h1>
    <p id="greeting" class="greeting"></p>
    <div class="task-cards" id="task-cards"></div>
    <div class="add-row" onclick="openModal()">
        <button class="add-btn">+</button>
        <span class="add-task-label">Add Task</span>
    </div>
    <button id="quitBtn" onclick="quit()">Quit</button>

    <div class="modal-overlay" id="confirm-overlay">
        <div class="modal">
            <h3 style="text-align:center;">Delete this Task?</h3>
            <div class="modal-btns" style="justify-content:center;">
                <button class="primary" id="confirm-yes">Yes</button>
                <button class="secondary" onclick="closeConfirm()">No</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="modal-overlay">
        <div class="modal">
            <h3>New Task</h3>
            <label>Describe your Task:
                <input type="text" id="task-desc" placeholder="e.g. Go for a run">
            </label>
            <p class="colour-label">Choose a colour:</p>
            <div class="colour-swatches" id="colour-swatches">
                <div class="swatch" data-color="#8BAFD6" style="background:#8BAFD6"></div>
                <div class="swatch" data-color="#F090A8" style="background:#F090A8"></div>
                <div class="swatch" data-color="#EDE068" style="background:#EDE068"></div>
                <div class="swatch" data-color="#5AAA8E" style="background:#5AAA8E"></div>
                <div class="swatch" data-color="#F05898" style="background:#F05898"></div>
                <div class="swatch" data-color="#9868C8" style="background:#9868C8"></div>
                <div class="swatch" data-color="#80C0E8" style="background:#80C0E8"></div>
                <div class="swatch" data-color="#F0A068" style="background:#F0A068"></div>
            </div>
            <div class="modal-btns">
                <button class="primary" onclick="submitTask()">Add</button>
                <button onclick="closeModal()">Cancel</button>
            </div>
        </div>
    </div>
    <script>
        const MONTH_ABBRS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        const MONTH_NAMES = ['January','February','March','April','May','June','July','August','September','October','November','December'];
        const DAY_NAMES   = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
        const TICK_SVG    = `<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="2.5,8.5 6.5,12.5 13.5,4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>`;

        async function post(url, body = {}) {
            await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
        }

        function lightenColor(hex, factor) {
            const r = parseInt(hex.slice(1,3), 16);
            const g = parseInt(hex.slice(3,5), 16);
            const b = parseInt(hex.slice(5,7), 16);
            return `rgb(${Math.round(r+(255-r)*factor)},${Math.round(g+(255-g)*factor)},${Math.round(b+(255-b)*factor)})`;
        }

        function getDayNum(createdStr) {
            const [y, m, d] = createdStr.split('-').map(Number);
            const created = new Date(y, m - 1, d);
            const today   = new Date();
            today.setHours(0, 0, 0, 0);
            created.setHours(0, 0, 0, 0);
            return Math.floor((today - created) / 86400000) + 1;
        }

        function formatCreated(createdStr) {
            const [y, m, d] = createdStr.split('-').map(Number);
            const dow = new Date(y, m - 1, d).getDay();
            return `Created ${DAY_NAMES[dow]}, ${d} ${MONTH_NAMES[m - 1]} ${y}`;
        }

        (async function initGreeting() {
            let name = """ + json.dumps(saved_name) + """;
            if (!name) {
                name = prompt("Please enter your first name:");
                if (name && name.trim()) {
                    name = name.trim().charAt(0).toUpperCase() + name.trim().slice(1).toLowerCase();
                    await post('/save-name', { name });
                }
            }
            if (name) {
                const hour = new Date().getHours();
                let greeting;
                if      (hour >= 1  && hour < 12) greeting = `Good morning, ${name}.`;
                else if (hour >= 12 && hour < 14) greeting = `Good day, ${name}.`;
                else if (hour >= 14 && hour < 18) greeting = `Good afternoon, ${name}.`;
                else                              greeting = `Good evening, ${name}.`;
                document.getElementById('greeting').textContent = greeting;
            }
        })();

        loadTasks();

        let selectedColor = '#8BAFD6';

        document.getElementById('colour-swatches').addEventListener('click', function(e) {
            if (!e.target.classList.contains('swatch')) return;
            document.querySelectorAll('.swatch').forEach(s => s.classList.remove('selected'));
            e.target.classList.add('selected');
            selectedColor = e.target.dataset.color;
        });

        function openModal() {
            document.getElementById('task-desc').value = '';
            selectedColor = '#8BAFD6';
            document.querySelectorAll('.swatch').forEach(s => s.classList.remove('selected'));
            document.querySelector('.swatch').classList.add('selected');
            document.getElementById('modal-overlay').classList.add('active');
            document.getElementById('task-desc').focus();
        }

        function closeModal() {
            document.getElementById('modal-overlay').classList.remove('active');
        }

        function renderTasks(tasks) {
            const container = document.getElementById('task-cards');
            container.innerHTML = '';
            tasks.forEach(task => {
                const dayNum = getDayNum(task.created);
                const active = dayNum >= 1 && dayNum <= 60;
                const [cy, cm, cd] = task.created.split('-').map(Number);
                const createdDate  = new Date(cy, cm - 1, cd);

                // Grid (built first to capture todayBlock reference)
                const grid = document.createElement('div');
                grid.className = 'days-grid';
                let todayBlock = null;
                for (let i = 1; i <= 60; i++) {
                    const blockDate = new Date(createdDate);
                    blockDate.setDate(blockDate.getDate() + (i - 1));

                    const isChecked = !!task.checked[String(i)];
                    const btn = document.createElement('button');
                    btn.className = 'day-btn';
                    btn.style.background = isChecked ? task.color : lightenColor(task.color, 0.82);
                    btn.style.color      = isChecked ? 'white' : '#555';
                    btn.innerHTML = `<span style="font-size:7px;">${MONTH_ABBRS[blockDate.getMonth()]}</span>
                                     <span style="font-size:11px;font-weight:500;">${blockDate.getDate()}</span>`;
                    if (i === dayNum && !isChecked) {
                        btn.style.outline       = `2px solid ${task.color}`;
                        btn.style.outlineOffset = '-2px';
                    }
                    if (i === dayNum) todayBlock = btn;
                    grid.appendChild(btn);
                }

                // Tick button
                const isTicked = active && !!task.checked[String(dayNum)];
                const tickBtn  = document.createElement('button');
                tickBtn.className      = 'tick-btn';
                tickBtn.innerHTML      = TICK_SVG;
                tickBtn.dataset.ticked = isTicked;
                tickBtn.style.background = isTicked ? task.color : lightenColor(task.color, 0.82);
                tickBtn.style.color      = isTicked ? 'white' : '#555';
                if (!active) {
                    tickBtn.style.opacity = '0.35';
                    tickBtn.style.cursor  = 'default';
                } else {
                    tickBtn.addEventListener('click', () => toggleTick(task.id, dayNum, tickBtn, task.color, todayBlock));
                }

                // Title (editable)
                const titleEl = document.createElement('p');
                titleEl.className       = 'task-card-title';
                titleEl.contentEditable = 'true';
                titleEl.spellcheck      = false;
                titleEl.textContent     = task.desc;
                let originalText = task.desc;
                titleEl.addEventListener('focus', () => { originalText = titleEl.textContent.trim(); });
                titleEl.addEventListener('keydown', e => {
                    if (e.key === 'Enter')  { e.preventDefault(); titleEl.blur(); }
                    if (e.key === 'Escape') { titleEl.textContent = originalText; titleEl.blur(); }
                });
                titleEl.addEventListener('blur', async () => {
                    const newText = titleEl.textContent.trim();
                    if (!newText) { titleEl.textContent = originalText; return; }
                    if (newText !== originalText) {
                        await post('/rename-task', { id: task.id, desc: newText });
                        originalText = newText;
                    }
                });

                const dateEl = document.createElement('p');
                dateEl.className   = 'task-card-date';
                dateEl.textContent = formatCreated(task.created);

                const descBlock = document.createElement('div');
                descBlock.style.flex = '1';
                descBlock.appendChild(titleEl);
                descBlock.appendChild(dateEl);

                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'delete-btn';
                deleteBtn.innerHTML = '&#x2715;';
                deleteBtn.title     = 'Remove task';
                deleteBtn.onclick   = () => deleteTask(task.id);
                deleteBtn.addEventListener('mouseenter', () => deleteBtn.style.color = task.color);
                deleteBtn.addEventListener('mouseleave', () => deleteBtn.style.color = '#555');

                const header = document.createElement('div');
                header.className = 'task-card-header';
                header.appendChild(tickBtn);
                header.appendChild(descBlock);
                header.appendChild(deleteBtn);

                const card = document.createElement('div');
                card.className = 'task-card';
                card.appendChild(header);
                card.appendChild(document.createElement('hr'));
                card.appendChild(grid);
                container.appendChild(card);
            });
        }

        async function loadTasks() {
            const res  = await fetch('/get-all-tasks');
            const data = await res.json();
            renderTasks(data.tasks);
        }

        async function submitTask() {
            const desc = document.getElementById('task-desc').value.trim();
            if (!desc) return;
            await post('/save-task', { desc, color: selectedColor });
            await loadTasks();
            closeModal();
        }

        function deleteTask(id) {
            const overlay = document.getElementById('confirm-overlay');
            overlay.classList.add('active');
            document.getElementById('confirm-yes').onclick = async () => {
                overlay.classList.remove('active');
                await post('/delete-task', { id });
                await loadTasks();
            };
        }

        function closeConfirm() {
            document.getElementById('confirm-overlay').classList.remove('active');
        }

        async function toggleTick(id, dayNum, tickBtn, color, todayBlock) {
            const ticked = tickBtn.dataset.ticked !== 'true';
            tickBtn.dataset.ticked   = ticked;
            tickBtn.style.background = ticked ? color : lightenColor(color, 0.82);
            tickBtn.style.color      = ticked ? 'white' : '#555';
            if (todayBlock) {
                todayBlock.style.background   = ticked ? color : lightenColor(color, 0.82);
                todayBlock.style.color        = ticked ? 'white' : '#555';
                todayBlock.style.outline      = ticked ? 'none' : `2px solid ${color}`;
                todayBlock.style.outlineOffset = '-2px';
            }
            await post('/toggle-task', { id, date: String(dayNum), checked: ticked });
        }

        document.getElementById('modal-overlay').addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });
        document.getElementById('confirm-overlay').addEventListener('click', function(e) {
            if (e.target === this) closeConfirm();
        });

        async function quit() {
            await post('/quit');
            window.close();
        }
    </script>
    """

@app.route("/save-name", methods=["POST"])
def save_name():
    data   = request.get_json()
    config = load_config()
    config["name"] = data["name"]
    save_config(config)
    return "", 204

@app.route("/save-task", methods=["POST"])
def save_task():
    data   = request.get_json()
    config = load_config()
    today  = date.today()
    task   = {
        "id":      str(int(time.time() * 1000)),
        "desc":    data["desc"],
        "color":   data.get("color", "#8BAFD6"),
        "created": f"{today.year}-{today.month}-{today.day}",
        "checked": {}
    }
    config.setdefault("tasks", []).append(task)
    save_config(config)
    return "", 204

@app.route("/get-all-tasks")
def get_all_tasks():
    config = load_config()
    return jsonify({"tasks": config.get("tasks", [])})

@app.route("/rename-task", methods=["POST"])
def rename_task():
    data   = request.get_json()
    config = load_config()
    task   = find_task(config.get("tasks", []), data["id"])
    if task:
        task["desc"] = data["desc"]
    save_config(config)
    return "", 204

@app.route("/delete-task", methods=["POST"])
def delete_task():
    data   = request.get_json()
    config = load_config()
    config["tasks"] = [t for t in config.get("tasks", []) if t["id"] != data["id"]]
    save_config(config)
    return "", 204

@app.route("/toggle-task", methods=["POST"])
def toggle_task():
    data   = request.get_json()
    config = load_config()
    task   = find_task(config.get("tasks", []), data["id"])
    if task:
        task["checked"][data["date"]] = data["checked"]
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
