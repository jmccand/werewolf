import random
import urllib.parse
import webbrowser
import os
import socket
from http.cookies import SimpleCookie
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import uuid

class MyHandler(SimpleHTTPRequestHandler):

    player_usernames = set()

    def do_GET(self):
        print('\npath = ' + self.path)

        host = self.headers.get('Host')
        print(host)
        if host != 'werewolf.joelmccandless.com:8000':
            self.send_response(302)
            self.send_header('Location', 'http://werewolf.joelmccandless.com:8000')
            self.end_headers()
            return
        else:
            if self.path == '/change_username':
                return self.change_username()
            elif self.path.startswith('/set_username'):
                return self.set_username()
            elif self.path.startswith('/new_game'):
                return self.new_game()
            elif self.path.startswith('/join_game'):
                return self.join_game()
            elif self.path == '/':
                return self.handleHomepage()
            elif self.path.endswith('.jpg'):
                return self.load_image()
            elif self.path.startswith('/waiting_room'):
                return self.waiting_room()
            elif self.path.startswith('/game_state'):
                return self.get_gamestate()
            elif self.path.startswith('/pick_roles'):
                return self.pick_roles()
            elif self.path.startswith('/set_roles'):
                return self.set_roles()
            elif self.path.startswith('/view_roles'):
                return self.view_roles()
            elif self.path.startswith('/deal_cards'):
                return self.deal_cards()
            elif self.path.startswith('/show_cards'):
                return self.show_cards()
            elif self.path.startswith('/start_night'):
                return self.start_night()
                    
    def set_username(self):
        print('set username')
        arguments = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if 'username' in arguments:
            username = arguments['username'][0]
            print(username)
        else:
            username = None
        if 'username' not in arguments or username in MyHandler.player_usernames:
            self.send_response(200)
            self.end_headers()
            self.wfile.write('<html><body>'.encode('utf8'))
#            if username in MyHandler.player_usernames:
#                self.wfile.write(f'Sorry, the username "{username}" was already taken. Please choose another username.'.encode('utf8'))
            self.wfile.write('''
    <form method = 'GET' action = '/set_username'>
    Please enter your username:
    <input type = 'text' name = 'username'/>
    <input type = 'submit' value = 'submit'/>
    </form>
    </body>
    </html>
    '''.encode('utf8'))
        else:
            self.send_response(302)
            self.send_header('Set-Cookie', 'username="%s"; domain=werewolf.joelmccandless.com' % username)
            self.send_header('Location', '/')
            self.end_headers()

    def change_username(self):
        print('change username called')
        self.send_response(302)
        print('sending expired cookie...')
        self.send_header('Set-Cookie', 'username=None; domain=werewolf.joelmccandless.com; expires=Mon, 14 Sep 2020 07:00:00 GMT')
        print('expired cookie sent!')
        self.send_header('Location', '/set_username')
        self.end_headers()
        cookies = SimpleCookie(self.headers.get('Cookie'))
        username = cookies['username'].value
        MyHandler.player_usernames.remove(username)

    def get_gamestate(self):
        myID = self.get_game_id()
        myGame = Game.running_games[myID]
        self.send_response(200)
        self.end_headers()
        if myGame.gamestate == 'waiting_room':
            game_state = {'mode': 'waiting_room', 'players': list(myGame.players)}
        elif myGame.gamestate == 'pick_roles':
            game_state = {'mode': 'pick_roles', 'roles': myGame.selected_roles}
        elif myGame.gamestate == 'show_cards':
            game_state = {'mode': 'show_cards', 'roles': myGame.position_username_role}
        elif myGame.gamestate == 'night':
            game_state = {'mode': 'night', 'active_roles': myGame.active_roles}
            print(f'active_roles: {myGame.active_roles}')
        self.wfile.write(json.dumps(game_state).encode('utf8'))

    def pick_roles(self):
        myID = self.get_game_id()
        myGame = Game.running_games[myID]
        myGame.gamestate = 'pick_roles'
        print(myGame.uuid + ' GAME: MODE SWITCHED TO PICK ROLES')
        self.send_response(200)
        self.end_headers()
        self.wfile.write(str('''
<html>
<head>
<style>
div.fixed {
        position : fixed;
        top : 40%%;
        left : 38;
        width : 200px;
        height : 100px;
        border: 3px solid #FFFFFF;
        z-index : 1;
`}
div.relative {
        position : relative;
        left : 110px;
        width : 1091px;
        height : 300px;
        border : 0px solid #FFFFFF;
        z-index : 0;
}
</style>
</head>
<body bgcolor = '#000033' align = 'center'>
<div class = 'fixed' align = 'center'>
<font id = 'total_role_number' color = '#FFFFFF' size = '32'>
0 / %s
</font>
<br />
<font color = '#FFFFFF' size = '6'>
roles selected
</font>
</div>

<h2>
<button id='start_game' onclick='document.location.href = "/deal_cards?id=%s"' type = 'button' style = 'position : fixed; top : 55%%; left : 50; z-index : 1' disabled='true'>
<font size = '6'>
Start Game
</font>
</button>
</h2>

<div class = 'relative' style = 'display : inline-block'>
<h1>
<font color = '#FFFFFF'> One Night Ultimate Werewolf </font>
</h1>
<img src = 'sentinel.jpg' id = 'sentinel' width = '215px' height = '300px' style = 'border : 0px solid white' onclick = 'selectCard(this)'/>
<img src = 'doppleganger.jpg' id = 'doppleganger' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'werewolf.jpg' id = 'werewolf1' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'werewolf.jpg' id = 'werewolf2' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'alpha wolf.jpg' id = 'alpha wolf' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<br />
<img src = 'mystic wolf.jpg' id = 'mystic wolf' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'minion.jpg' id = 'minion' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'mason.jpg' id = 'mason1' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'mason.jpg' id = 'mason2' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'seer.jpg' id = 'seer' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<br />
<img src = 'apprentice seer.jpg' id = 'apprentice seer' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'paranormal investigator.jpg' id = 'paranormal investigator' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'robber.jpg' id = 'robber' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'witch.jpg' id = 'witch' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'troublemaker.jpg' id = 'troublemaker' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<br />
<img src = 'village idiot.jpg' id = 'village idiot' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'drunk.jpg' id = 'drunk' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'insomniac.jpg' id = 'insomniac' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'revealer.jpg' id = 'revealer' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'curator.jpg' id = 'curator' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<br />
<img src = 'villager.jpg' id = 'villager1' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'villager.jpg' id = 'villager2' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'villager.jpg' id = 'villager3' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'hunter.jpg' id = 'hunter' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'tanner.jpg' id = 'tanner' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<br />
<img src = 'dream wolf.jpg' id = 'dream wolf' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
<img src = 'bodyguard.jpg' id = 'bodyguard' width = '215px' height = '300px' style = 'border:0px solid white' onclick = 'selectCard(this)'/>
</div>
<script>

var total_roles_selected = [];
var number_of_players = %s;

function selectCard(element) {
        if (element.style.border == '6px solid white') {
                element.style.border = '0px solid white';        
                element.width = '215';
                element.height = '300';
                total_roles_selected.splice(total_roles_selected.indexOf(element.id), 1);
        }
        else {
                element.style.border = '6px solid white';
                element.width = '203';
                element.height = '288';
                total_roles_selected.push(element.id);
        }
        updateRoles(total_roles_selected);
        document.getElementById('total_role_number').innerHTML = total_roles_selected.length + ' / ' + number_of_players;
        if (total_roles_selected.length == number_of_players) {
                document.getElementById('start_game').disabled = false;
        }
        else {
                document.getElementById('start_game').disabled = true;
        }
}
function updateRoles(roleList) {
        var xhttp = new XMLHttpRequest();
        xhttp.open("GET", "/set_roles?id=%s&roles=" + roleList.join(), true);
        xhttp.send();
}
</script>
</body>
</html>
''' % (len(myGame.players) + 3, myID, len(myGame.players) + 3, myID)).encode('utf8'))

    def load_image(self):
        if self.path.startswith('/werewolf'):
            self.path = '/werewolf.jpg'
        return SimpleHTTPRequestHandler.do_GET(self)

    def handleHomepage(self, invalidId=False):
        cookies = SimpleCookie(self.headers.get('Cookie'))
        self.send_response(200)
        self.end_headers()
        if 'username' not in cookies:
            self.wfile.write('''<html><body>We noticed you are not signed in. To create or join a game, please sign in below.<br />
<button onclick='document.location.href="/set_username"'>SIGN IN</button>
<br /><br /><br />
'''.encode('utf8'))
            
        else:
            self.wfile.write('<html><body>'.encode('utf8'))
            if invalidId != False:
                self.wfile.write(f'''Error, the ID you entered was not found.<br />
<button onclick='document.location.href="/new_game"'>Host new game</button><br />
<br />
OR
<br />
<br />
<form action='/join_game' method='GET'>
Game Pin:<br />
<input type='text' name='gamepin' value='{invalidId}'/>
<input type='submit' value='Join!'/>
</form>
                '''.encode('utf8'))
            else:
                self.wfile.write('''
<button onclick='document.location.href="/new_game"'>Host new game</button><br />
<br />
OR
<br />
<br />
<form action='/join_game' method='GET'>
Game Pin:<br />
<input type='text' name='gamepin'/>
<input type='submit' value='Join!'/>
</form>
                '''.encode('utf8'))

            self.wfile.write('''<br />
Here is a list of public games that you can join:<br />
<ul>
            '''.encode('utf8'))
            for game in Game.running_games.values():
                self.wfile.write(f'''<li><a href='/waiting_room?id={game.uuid}'>{len(game.players)} player game</a></li>'''.encode('utf8'))
            self.wfile.write('</ul></body></html>'.encode('utf8'))

    def getUsername(self):
        cookies = SimpleCookie(self.headers.get('Cookie'))
        if 'username' not in cookies:
            self.send_response(400)
            self.end_headers()
            raise KeyError('username not in cookies; sent response 400')
        else:
            return cookies['username'].value

    def waiting_room(self):
        myID = self.get_game_id()
        myGame = Game.running_games[self.get_game_id()]
        username = self.getUsername()
        
        self.send_response(200)
        self.end_headers()
        
        Game.running_games[myID].players.append(username)

        self.wfile.write(f'''
<html>
<body>
Welcome {username}!
<br />
There are <span id='player_number'>{len(myGame.players)}</span> players.
<br />'''.encode('utf-8'))
        self.wfile.write('Here are the current players:<ol id = "player_list">'.encode('utf-8'))
        for username in myGame.players:
            self.wfile.write(f'<li>{username}</li>'.encode('utf-8'))
        self.wfile.write(('''
</ol>
<button type = 'button' onclick = 'document.location.href = "/change_username"'>
Change username
</button>
<script>
function refreshPage() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/game_state?id=%s", true);
    xhttp.send();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            var updatedPlayers = response['players']
            if (response['mode'] == 'waiting_room') {
                var player_list = document.getElementById('player_list');
                while (player_list.firstChild) {
                    player_list.removeChild(player_list.firstChild);
                }
                for (element = 0; element < updatedPlayers.length; element++) {
                    var player = document.createElement('li');
                    player.innerHTML = updatedPlayers[element]
                    player_list.appendChild(player);
                }
                document.getElementById('player_number').innerHTML = updatedPlayers.length;
            }
            else if (response['mode'] == 'pick_roles') {
                document.location.href = '/view_roles?id=%s'
            }
            console.log('updatedPlayerList: ' + this.responseText);
        }
    };
    setTimeout(refreshPage, 1000);
}
setTimeout(refreshPage, 1000);
</script>
        ''' % (myID, myID)).encode('utf8'))

        if myGame.players[0] == username:
            self.wfile.write(('''
<button type = 'button' onclick = 'document.location.href = "/pick_roles?id=%s"'>
Select Roles
</button>
            ''' % myID).encode('utf8'))

        self.wfile.write('''
</body>
</html>
        '''.encode('utf8'))

    def set_roles(self):
        myID = self.get_game_id()
        myGame = Game.running_games[myID]
        arguments = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query, keep_blank_values=True)
        if 'roles' in arguments:
            if arguments['roles'] == ['']:
                myGame.selected_roles = []
            else:
                myGame.selected_roles = arguments['roles'][0].split(",")

    def view_roles(self):
        myID = self.get_game_id()
        myGame = Game.running_games[myID]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(str('''
<html>
<head>
<style>
div.fixed {
        position : fixed;
        top : 40%%;
        left : 38;
        width : 200px;
        height : 100px;
        border: 3px solid #FFFFFF;
        z-index : 1;
}
div.relative {
        position : relative;
        left : 110px;
        width : 1091px;
        height : 300px;
        border : 0px solid #FFFFFF;
        z-index : 0;
}
</style>
</head>
<body bgcolor = '#000033' align = 'center'>
<div class = 'fixed' align = 'center'>
<font id = 'total_role_number' color = '#FFFFFF' size = '32'>
0 / %s
</font>
<br />
<font color = '#FFFFFF' size = '6'>
roles selected
</font>
</div>
<div class = 'relative' style = 'display : inline-block'>
<h1>
<font color = '#FFFFFF'> One Night Ultimate Werewolf </font>
</h1>
<img src = 'sentinel.jpg' id = 'sentinel' width = '215px' height = '300px' style = 'border : 0px solid white'/>
<img src = 'doppleganger.jpg' id = 'doppleganger' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'werewolf.jpg' id = 'werewolf1' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'werewolf.jpg' id = 'werewolf2' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'alpha wolf.jpg' id = 'alpha wolf' width = '215px' height = '300px' style = 'border:0px solid white'/>
<br />
<img src = 'mystic wolf.jpg' id = 'mystic wolf' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'minion.jpg' id = 'minion' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'mason.jpg' id = 'mason1' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'mason.jpg' id = 'mason2' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'seer.jpg' id = 'seer' width = '215px' height = '300px' style = 'border:0px solid white'/>
<br />
<img src = 'apprentice seer.jpg' id = 'apprentice seer' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'paranormal investigator.jpg' id = 'paranormal investigator' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'robber.jpg' id = 'robber' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'witch.jpg' id = 'witch' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'troublemaker.jpg' id = 'troublemaker' width = '215px' height = '300px' style = 'border:0px solid white'/>
<br />
<img src = 'village idiot.jpg' id = 'village idiot' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'drunk.jpg' id = 'drunk' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'insomniac.jpg' id = 'insomniac' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'revealer.jpg' id = 'revealer' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'curator.jpg' id = 'curator' width = '215px' height = '300px' style = 'border:0px solid white'/>
<br />
<img src = 'villager.jpg' id = 'villager1' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'villager.jpg' id = 'villager2' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'villager.jpg' id = 'villager3' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'hunter.jpg' id = 'hunter' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'tanner.jpg' id = 'tanner' width = '215px' height = '300px' style = 'border:0px solid white'/>
<br />
<img src = 'dream wolf.jpg' id = 'dream wolf' width = '215px' height = '300px' style = 'border:0px solid white'/>
<img src = 'bodyguard.jpg' id = 'bodyguard' width = '215px' height = '300px' style = 'border:0px solid white'/>
</div>
<script>

var total_roles_selected = [];
var number_of_players = %s;

function refreshPage() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/game_state?id=%s", true);
    xhttp.send();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            var updatedRoles = response['roles']
            if (response['mode'] == 'pick_roles') {
                console.log('updated roles: ' + updatedRoles);
                for (var index = 0; index < total_roles_selected.length; index++) {
                    var role = total_roles_selected[index];
                    if (updatedRoles.indexOf(role) == -1) {
                        var element = document.getElementById(role);
                        element.style.border = '0px solid white';
                        element.width = '215';
                        element.height = '300';
                    }
                }
                for (var index = 0; index < updatedRoles.length; index++) {
                    var role = updatedRoles[index];
                    var element = document.getElementById(role);
                    element.style.border = '6px solid white';
                    element.width = '203';
                    element.height = '288';
                }
                total_roles_selected = updatedRoles;
                document.getElementById('total_role_number').innerHTML = total_roles_selected.length + ' / ' + number_of_players;
            }
            else {
                document.location.href = '/show_cards?id=%s';
            }
        }
    }
    setTimeout(refreshPage, 1000);
}
setTimeout(refreshPage, 1000);
</script>
</body>
</html>
''' % (len(myGame.players) + 3, len(myGame.players) + 3, myID, myID)).encode('utf8'))

    def deal_cards(self):
        myID = self.get_game_id()
        myGame = Game.running_games[myID]
        if len(myGame.players) + 3 != len(myGame.selected_roles):
            print('there was an error: incorrect number of roles')
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f'''<html><body>I'm sorry, you must've pressed the start game too fast. The server sees {myGame.players} as players and {myGame.selected_roles} as roles.</body></html>'''.encode('utf8'))
        else:
            print('DEALING CARDS')
            available_roles = myGame.selected_roles[:]
            for player in myGame.players:
                choice = random.choice(available_roles)
                myGame.position_username_role.append((player, choice))
                available_roles.remove(choice)
            myGame.gamestate = 'show_cards'
            self.send_response(302)
            self.send_header('Location', '/show_cards?id=%s' % myID)
            self.end_headers()

    def show_cards(self):
        myID = self.get_game_id()
        myGame = Game.running_games[myID]
        self.send_response(200)
        self.end_headers()
        cookies = SimpleCookie(self.headers.get('Cookie'))
        username = cookies['username'].value
        my_index = None
        for index, player_role in enumerate(myGame.position_username_role):
            if player_role[0] == username:
                my_index = index
        my_role = myGame.position_username_role[my_index][1]
        self.wfile.write('''
<html>
<head>
<title>ONUW TABLE</title>
<style>
body {
    background-image : url('Table.jpg');
}
</style>
</head>
<body>
<!--<div style = 'position : fixed; height : 1; width : 1; left : 700; top : 360; border : 3px solid #000000'>
</div>-->'''.encode('utf8'))
        if my_index == 0:
            self.wfile.write(f'''<button id='start_night_button' type='button' onclick='document.location.href="/start_night?id={myID}"'>Start night</button>'''.encode('utf8'))
        self.wfile.write(('''
<script>
var firstRefresh = true;
var player_role_list = %s;
var my_index = %s;
var my_role;
var alreadyRefreshedNight = false;
var selected;
function drawBoard() {
    var total_player_number = player_role_list.length;
    for (var player = 0; player < total_player_number; player++) {
        var angle = (360.0 / total_player_number) * player - 90;
        var y = Math.sin((angle / 360.0) * (2 * Math.PI)) * 280;
        var x = Math.cos((angle / 360.0) * (2 * Math.PI)) * 280;
        var image = document.createElement('img');
        if (player == 0) {
            image.src = player_role_list[my_index][1] + '.jpg'
            image.id = 'my_card';
        }
        else {
            image.src = 'Card Backside.jpg';
        }
        image.width = '71';
        image.height = '100';
        image.style.transform = 'rotate(' + (-(angle + 90)) + 'deg)';
        image.style.position = 'fixed';
        image.style.left = 735 + x - 35;
        image.style.top = 380 - y - 50;
        //really important onclick for selection:
        image.setAttribute('onclick', 'select(this)');
        document.body.appendChild(image);
        
        y *= 13/10;
        x *= 13/10;
        var name = document.createElement('div');
        name.innerHTML = player_role_list[(player + my_index) %% total_player_number][0];
        name.style.transform = 'rotate(' + (-(angle + 90)) + 'deg)';
        name.style.position = 'fixed';
        name.style.width = '300';
        name.style.left = 735 + x - 150;
        name.style.top = 372 - y;
        name.style.textAlign = 'center';
        name.style.fontWeight = 'bold';
        name.style.color = 'white';
        document.body.appendChild(name);
    }

    var centerRotation = my_index * 360 / total_player_number;

    for (var player = 0; player < 2; player++) {
        var angle = -(360.0 / 2) * player - centerRotation;
        var card;
        y = Math.sin((angle / 360.0) * (2 * Math.PI)) * 80;
        x = Math.cos((angle / 360.0) * (2 * Math.PI)) * 80;
        card = document.createElement('img');
        card.src = 'Card Backside.jpg';
        card.width = '71';
        card.height = '100';
        card.style.transform = 'rotate(' + (-angle + 180 * player) + 'deg)';
        card.style.position = 'fixed';
        card.style.left = 735 + x - 35;
        card.style.top = 380 - y - 50;
        document.body.appendChild(card);
    }
    var card = document.createElement('img');
    card.src = 'Card Backside.jpg';
    card.width = '71';
    card.height = '100';
    card.style.transform = 'rotate(' + (centerRotation) + 'deg)';
    card.style.position = 'fixed';
    card.style.left = 735 - 35;
    card.style.top = 380 - 50;
    document.body.appendChild(card);
}

function myTurn() {
    my_role = player_role_list[my_index][1];
    var div = document.createElement('div');
    div.innerHTML = 'Awaken ' + my_role + '!<br />';
    switch (my_role) {
        case 'alpha wolf':
            div.innerHTML += alpha_wolf();
        case 'mystic wolf':
            div.innerHTML += mystic_wolf();
        case 'werewolf1':
        case 'werewolf2':
            div.innerHTML += werewolf();
            break;
        case 'apprentice seer':
            div.innerHTML += apprentice_seer();
            break;
        case 'bodyguard':
            div.innerHTML += bodyguard();
            break;
        case 'curator':
            div.innerHTML += curator();
            break;
        case 'doppleganger':
            div.innerHTML += doppleganger();
            break;
        case 'dream wolf':
            div.innerHTML += dream_wolf();
            break;
        case 'drunk':
            div.innerHTML += drunk();
            break;
        case 'hunter':
            div.innerHTML += hunter();
            break;
        case 'insomniac':
            div.innerHTML += insomniac();
            break;
        case 'mason1':
        case 'mason2':
            div.innerHTML += mason();
            break;
        case 'minion':
            div.innerHTML += minion();
            break;
        case 'paranormal investigator':
            div.innerHTML += paranormal_investigator();
            break;
        case 'revealer':
            div.innerHTML += revealer();
            break;
        case 'robber':
            div.innerHTML += robber();
            break;
        case 'seer':
            div.innerHTML += seer();
            break;
        case 'sentinel':
            div.innerHTML += sentinel();
            break;
        case 'tanner':
            div.innerHTML += tanner();
            break;
        case 'troublemaker':
            div.innerHTML += troublemaker();
            break;
        case 'village idiot':
            div.innerHTML += village_idiot();
            break;
        case 'villager':
            div.innerHTML += villager();
            break;
        case 'witch':
            div.innerHTML += witch();
            break;
    }
    div.style = 'position: absolute; top: 20px; left: 40%%; background-color: white; border-style: solid; border-color: red; width: 20%%;';
    div.align = 'center';
    document.body.appendChild(div);
}

function werewolf() {
    console.log('werewolf function called!');
    var partnerWolf = false;
    for (var index = 0; index < player_role_list.length; index++) {
        if ((player_role_list[index][1].indexOf('wolf') != -1) && player_role_list[index][1] != my_role) {
            partnerWolf = player_role_list[index][0];
        }
    }
    if (partnerWolf != false) {
        return 'Your partner is ' + partnerWolf + '.';
    }
    else {
        return 'You are the lone wolf. Select a card in the center to view.';
        var thisSelection = selectNext();
        /*while (thisSelection.indexOf('Center') == -1) {
            thisSelection = selectNext();
        }*/
        
    }
}

function selectNext() {
    selected = null;
    while (selected == null) {
    }
    console.log('selectNext caught ' + selected.src);
    return selected;
}

function select(element) {
    selected = element;
}

function refreshPage() {
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/game_state?id=%s", true);
    xhttp.send();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            if (firstRefresh) {
                drawBoard();
                firstRefresh = false;
            }
            else if (response['mode'] == 'night') {
                if (alreadyRefreshedNight == false) {
                    alreadyRefreshedNight = true;''' % ([list(tuplepair) for tuplepair in myGame.position_username_role], my_index, myID)).encode('utf8'))
        if my_index == 0:
            self.wfile.write('''
                    var child = document.getElementById('start_night_button');
                    child.parentNode.removeChild(child);
            '''.encode('utf8'))
        self.wfile.write('''
                    document.getElementById('my_card').src = 'Card Backside.jpg';
                    if (response['active_roles'].indexOf(player_role_list[my_index][1]) != -1) {
                        myTurn();
                    }
                }
            }
        }
    }
    setTimeout(refreshPage, 1000);
}
setTimeout(refreshPage, 1000);

</script>
</body>
</html>
'''.encode('utf8'))

    def start_night(self):
        myID = self.get_game_id()
        myGame = Game.running_games[myID]
        myGame.gamestate = 'night'
        myGame.active_roles = ['werewolf1', 'werewolf2']
        self.send_response(302)
        self.send_header('Location', f'/show_cards?id={myID}')
        self.end_headers()

    def get_game_id(self):
        arguments = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query, keep_blank_values=True)
        print('get game id arguments: ' + str(arguments))
        if 'id' in arguments:
            if arguments['id'][0] in Game.running_games:
                return arguments['id'][0]
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write('<html><body>This game is not currently running. Return to the homepage <a href="/">here</a>.'.encode('utf8'))
                raise ValueError('no running games under pin; sent response 400')
        else:
            self.send_response(400)
            self.end_headers()
            raise KeyError(f'no ID given in url; sent response 400 (path was {self.path})')

    def new_game(self):
        gameID = uuid.uuid1().hex
        Game.newGame(gameID)
        self.send_response(302)
        self.send_header('Location', '/join_game?id=%s' % gameID)
        self.end_headers()
        self.wfile.write('You should be redirected'.encode('utf8'))

    def join_game(self):
        myID = self.get_game_id()
        if Game.canJoin(myID):
            self.send_response(302)
            self.send_header('Location', '/waiting_room?id=%s' % myID)
            self.end_headers()
        else:
            return self.handleHomepage(myID)

class Game:

    running_games = {}

    def __init__(self, uuid, gamestate, players=[], selected_roles=[], position_username_role=[], active_roles=None):
        self.uuid = uuid
        self.gamestate = gamestate
        self.players = players
        self.selected_roles = selected_roles
        self.position_username_role = position_username_role
        self.active_roles = active_roles

    def newGame(uuid):
        Game.running_games[uuid] = Game(uuid, 'waiting_room')

    def canJoin(uuid):
        if uuid in Game.running_games:
            myGame = Game.running_games[uuid]
        else:
            return False
        
        if myGame.gamestate == 'waiting_room':
            return True
        else:
            return False

    def seed_game(self):
        self.uuid = uuid
        #self.gamestate = 'show_cards'
        self.gamestate = 'night'
        self.players = ['Jmccand', 'Safari', 'DadMcDadDad']
        self.selected_roles = ['werewolf1', 'minion', 'sentinel', 'doppelganger', 'villager1', 'villager2']
        self.position_username_role = [('Jmccand', 'werewolf1'), ('Safari', 'villager1'), ('DadMcDadDad', 'minion')]
        self.active_roles = ['werewolf1', 'werewolf2']
        

class ReuseHTTPServer(HTTPServer):
    
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

class Cards:
    
    def __init__(self, name, frontside, validation, ability = 1):
        self.name = name
        self.frontside = frontside
        self.validation = validation
        self.ability = ability
    
#    center, edge, werewolves, oneself
    def validate(self, selected_player, matched_roles):
        center = selected_player in ("Center1", "Center2", "Center3")
        werewolves = matched_roles[selected_player].is_a_werewolf()
        oneself = (matched_roles[selected_player] != self)
        edge = not center and not werewolves and oneself
        for factor in range(0, 4):
            if(list(center, edge, werewolves, oneself)[factor]):
                if(not self.validation[factor]):
                    return False
        return True
    
    def is_a_werewolf(self):
        return self.name in ("alpha wolf", "dream wolf", "mystic wolf", "werewolf", "doppelganger-alpha wolf", "doppelganger-dream wolf", "doppelganger-mystic wolf", "doppelganger-werewolf")
    
    def switch_cards(self, player1, player2, players):
        original = players[player1]
        players[player1] = players[player2]
        players[player2] = original
        return players
    
    #def place_token(self, player, tokens):
     
#    def see(self, player, players):

active_roles = {
    Cards("alpha wolf", None, (False, True, False, False)) : False,
    Cards("apprentice seer", None, (True, False, False, False)) : False,
    Cards("bodyguard", None, None) : False,
    Cards("curator", None, (False, True, True, True)) : False,
    Cards("doppelganger", None, (False, True, True, False)) : False,
    Cards("dream wolf", None, None) : False,
    Cards("drunk", None, (True, False, False, False)) : False,
    Cards("hunter", None, None) : False,
    Cards("insomniac", None, None) : False,
    Cards("mason", None, None) : False,
    Cards("mason", None, None) : False,
    Cards("minion", None, None) : False,
    Cards("mystic wolf", None, (False, True, True, False)) : False,
    Cards("paranormal investigator", None, (False, True, True, False)) : False,
    Cards("revealer", None, (False, True, True, False)) : False,
    Cards("robber", None, (False, True, True, False)) : False,
    Cards("seer", None, (True, True, True, False)) : False,
    Cards("sentinel", None, (False, True, True, True)) : False,
    Cards("tanner", None, None) : False,
    Cards("troublemaker", None, (False, True, True, False)) : False,
    Cards("village idiot", None, None) : False,
    Cards("villager", None, None) : False,
    Cards("villager", None, None) : False,
    Cards("villager", None, None) : False,
    Cards("werewolf", None, None) : False,
    Cards("werewolf", None, None) : False,
    #!!!!! FIX THE WITCH VALIDATIONS
    Cards("witch", None, (True, True, True, True)) : False
}

matched_roles = {
}

night_order = (
    Cards("sentinel", None, (False, True, True, True)),
    Cards("doppelganger", None, (False, True, True, False)),
    Cards("werewolf", None, None),
    Cards("alpha wolf", None, (False, True, False, False)),
    Cards("mystic wolf", None, (False, True, True, False)),
    Cards("minion", None, None),
    Cards("mason", None, None),
    Cards("seer", None, (True, True, True, False)),
    Cards("apprentice seer", None, (True, False, False, False)),
    Cards("paranormal investigator", None, (False, True, True, False)),
    Cards("robber", None, (False, True, True, False)),
    Cards("witch", None, (True, True, True, True)),
    Cards("troublemaker", None, (False, True, True, False)),
    Cards("village idiot", None, None),
    Cards("drunk", None, (True, False, False, False)),
    #These three have the doppelganger after them:
    Cards("insomniac", None, None),
    Cards("revealer", None, (False, True, True, False)),
    Cards("curator", None, (False, True, True, True))
)

def main():
    print("One Night Werewolf Web")
    Game.newGame('16e7691a8f5211eb80a4a683e7b3717c')
    myGame = Game.running_games['16e7691a8f5211eb80a4a683e7b3717c']
    myGame.seed_game()

    httpd = ReuseHTTPServer(('0.0.0.0', 8000), MyHandler)
    httpd.serve_forever()
   

if __name__ == '__main__':
    main()
