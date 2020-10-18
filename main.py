import random

import urllib.parse
import webbrowser
import os
import socket
from http.cookies import SimpleCookie
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

class MyHandler(SimpleHTTPRequestHandler):

    player_usernames = set()
    first_user = None
    game_mode = 'waiting_room'
    role_list = []

    def do_GET(self):

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
            elif self.path == '/game_state':
                return self.get_gamestate()
            elif self.path == '/pick_roles':
                return self.pick_roles()
            elif self.path.endswith('.jpg'):
                return self.load_image()
            elif self.path == '/':
                return self.handleHomepage()
            elif self.path == '/waiting_room':
                return self.waiting_room()
            elif self.path.startswith('/set_username'):
                return self.set_username()
            elif self.path.startswith('/set_roles'):
                return self.set_roles()
            elif self.path == '/view_roles':
                return self.view_roles()

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
            if username in MyHandler.player_usernames:
                self.wfile.write(f'Sorry, the username "{username}" was already taken. Please choose another username.'.encode('utf8'))
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
            self.send_header('Set-Cookie', 'username=%s; domain=werewolf.joelmccandless.com' % username)
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
        self.send_response(200)
        self.end_headers()
        if MyHandler.game_mode == 'waiting_room':
            game_state = {'mode': 'waiting_room', 'players': list(MyHandler.player_usernames)}
        elif MyHandler.game_mode == 'pick_roles':
            game_state = {'mode': 'pick_roles', 'roles': MyHandler.role_list}
        self.wfile.write(json.dumps(game_state).encode('utf8'))

    def pick_roles(self):
        MyHandler.game_mode = 'pick_roles'
        print('GAME MODE SWITCHED TO PICK ROLES')
        self.send_response(200)
        self.end_headers()
        self.wfile.write('''
<html>
<head>
<style>
div.fixed {
	position : fixed;
	top : 40%;
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
<font id = 'total_role_number'color = '#FFFFFF' size = '32'>
0
</font>
<br />
<font color = '#FFFFFF' size = '6'>
roles selected
</font>
</div>

<h2>
<button type = 'button' style = 'position : fixed; top : 55%; left : 50; z-index : 1'>
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
        updateRoles(total_roles_selected)
	document.getElementById('total_role_number').innerHTML = total_roles_selected.length;
}
function updateRoles(roleList) {
        var xhttp = new XMLHttpRequest();
        xhttp.open("GET", "/set_roles?roles=" + roleList.join(), true);
        xhttp.send();
}
</script>
</body>
</html>
'''.encode('utf8'))

    def load_image(self):
        return SimpleHTTPRequestHandler.do_GET(self)

    def handleHomepage(self):
        print('handleHomepage')
        cookies = SimpleCookie(self.headers.get('Cookie'))
        self.send_response(302)
        if 'username' not in cookies:
            self.send_header('Location', '/set_username')
        else:
            self.send_header('Location', '/waiting_room')
        self.end_headers()

    def waiting_room(self):
        self.send_response(200)
        self.end_headers()

        cookies = SimpleCookie(self.headers.get('Cookie'))
        if 'username' not in cookies:
            self.wfile.write('''<html><body>Sorry, your username was not found.</body></html>'''.encode('utf-8'))
        else:
            username = cookies['username'].value
            MyHandler.player_usernames.add(username)
            if len(MyHandler.player_usernames) == 1:
                first_user = username
            arguments = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

            self.wfile.write(f'''
    <html>
    <body>
    Welcome {username}!
    <br />
    You are player {len(MyHandler.player_usernames)}.
    <br />'''.encode('utf-8'))
            self.wfile.write(f'Here are the current players:<ul id = "player_list">'.encode('utf-8'))
            for username in MyHandler.player_usernames:
                self.wfile.write(f'<li>{username}</li>'.encode('utf-8'))
            self.wfile.write('''
    </ul>
    <button type = 'button' onclick = 'document.location.href = "/change_username"'>
    Change username
    </button>
    <script>
    function refreshPage() {
        var xhttp = new XMLHttpRequest();
        xhttp.open("GET", "/game_state", true);
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
                }
                else if (response['mode'] == 'pick_roles') {
                    document.location.href = '/view_roles'
                }
                console.log('updatedPlayerList: ' + this.responseText);
            }
        };
        setTimeout(refreshPage, 1000);
    }
    setTimeout(refreshPage, 1000);
    </script>
    '''.encode('utf-8'))
            MyHandler.player_usernames.add(username)

            if len(MyHandler.player_usernames) == 1:
                self.wfile.write('''
    <button type = 'button' onclick = 'document.location.href = "/pick_roles"'>
    Select Roles
    </button>
    '''.encode('utf8'))
            self.wfile.write('''
    </body>
    </html>
    '''.encode('utf8'))

    def set_roles(self):
        print('path = ' + self.path)
        arguments = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query, keep_blank_values=True)
        print(arguments)
        MyHandler.role_list = arguments['roles'][0].split(",")
        print(MyHandler.role_list)

    def view_roles(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write('''
<html>
<head>
<style>
div.fixed {
	position : fixed;
	top : 40%;
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
<font id = 'total_role_number'color = '#FFFFFF' size = '32'>
0
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
 	document.getElementById('total_role_number').innerHTML = total_roles_selected.length;
}

    function refreshPage() {
        var xhttp = new XMLHttpRequest();
        xhttp.open("GET", "/game_state", true);
        xhttp.send();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var response = JSON.parse(this.responseText);
                var updatedRoles = response['roles']
                if (response['mode'] == 'pick_roles') {
                    console.log('updated roles: ' + updatedRoles);
                    for (var index = 0; index < total_roles_selected.length; index++) {
                        var role = updatedRoles[index];
                        if (updatedRoles.indexOf(role) == -1) {
                            var element = document.getElementById(role);
	                    element.style.border = '0px solid white';	
               		    element.width = '215';
 		            element.height = '300';
	                    total_roles_selected.splice(total_roles_selected.indexOf(element.id), 1);
                        }
                    }
                    for (var index = 0; index < updatedRoles.length; index++) {
                        var role = updatedRoles[index];
                        if (total_roles_selected.indexOf(role) != -1) {
                            var element = document.getElementById(role);
		            element.style.border = '6px solid white';
		            element.width = '203';
	                    element.height = '288';
                        }
                        total_roles_selected = updatedRoles;
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
   
    httpd = ReuseHTTPServer(('0.0.0.0', 8000), MyHandler)
    httpd.serve_forever()
   

if __name__ == '__main__':
    main()
 
players = 0
