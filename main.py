#بوت كامل من صنع ميرو متعوب عليه اكثر من شهرين
#MERO IS KING
#TELEGRAM:@@meroXking
#INSTGRAM:@mero.antiban
#XxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxX
import requests, os, psutil, sys, jwt, pickle, json, binascii, time, urllib3, base64, datetime, re, socket, threading
import asyncio
import random
from protobuf_decoder.protobuf_decoder import Parser
from byte import *
from byte import xSendTeamMsg
from byte import Auth_Chat
from xHeaders import *
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
import telebot
from telebot import types
import tempfile
import requests
import logging
import urllib3

import http.client
#http.client.HTTPConnection.debuglevel = 1

#Enable verbose logging for requests
#logging.basicConfig(level=logging.DEBUG)
#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  

# BoT SeT 
TELEGRAM_BOT_TOKEN  ="8578611979:AAE-5-S8NxeUbEEac8FCV5r1EY_CgFpaQrw"
ADMIN_USER_IDS = [6001028286]
# FiLeS SeT
USERS_FILE = 'users.json'
ACTIVATIONS_FILE = 'activations.json'
ACTIVATION_CODES_FILE = 'activation_codes.json'
ALLOWED_GROUPS_FILE = 'allowed_groups.json'
OWNERS_FILE = 'owners.json'
LOG_FILE = 'bot_log.txt'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, parse_mode='HTML')
import telebot
from telebot import apihelper

# Initialize your bot with your token


bot = telebot.TeleBot("8578611979:AAE-5-S8NxeUbEEac8FCV5r1EY_CgFpaQrw")
# 🎯 ADD THESE 2 LINES FOR DEBUGGING
# --- Safe wrapper for send_message ---
_original_send_message = bot.send_message

def safe_send_message(chat_id, text, **kwargs):
    """Automatically handles 'message to be replied not found' errors."""
    try:
        return _original_send_message(chat_id, text, **kwargs)
    except apihelper.ApiTelegramException as e:
        if "message to be replied not found" in str(e):
            # Retry without reply_to_message_id
            kwargs.pop("reply_to_message_id", None)
            return _original_send_message(chat_id, text, **kwargs)
        else:
            raise e

bot.send_message = safe_send_message


# --- Safe wrapper for reply_to ---
_original_reply_to = bot.reply_to

def safe_reply_to(message, text, **kwargs):
    """Automatically handles 'message to be replied not found' errors."""
    try:
        return _original_reply_to(message, text, **kwargs)
    except apihelper.ApiTelegramException as e:
        if "message to be replied not found" in str(e):
            # Fallback to normal send_message
            return bot.send_message(message.chat.id, text, **kwargs)
        else:
            raise e

bot.reply_to = safe_reply_to
# DaTa SeT
connected_clients = {}
connected_clients_lock = threading.Lock()
active_spam_targets = {}
active_spam_lock = threading.Lock()
activation_codes = {}

#TiMp GrOuPs
allowed_groups_cache = {}
cache_last_updated = 0
CACHE_TIMEOUT = 60  

def clean_text(text):
    if not text:
        return ""
    return str(text).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')

def log_action(action, user_id=None, details=""):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {action}"
    if user_id:
        log_entry += f" | User: {user_id}"
    if details:
        log_entry += f" | Details: {clean_text(details)}"
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")

def load_data(filename):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if not os.path.exists(filename):
                return {}

            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data

        except json.JSONDecodeError as e:
            if attempt == max_retries - 1:
                backup_file = f"{filename}.backup.{int(time.time())}"
                try:
                    os.rename(filename, backup_file)
                except:
                    pass
                return {}
            time.sleep(0.5)

        except Exception as e:
            if attempt == max_retries - 1:
                return {}
            time.sleep(0.5)

    return {}

def save_data(data, filename):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
            
            temp_file = None
            try:
                temp_file = tempfile.NamedTemporaryFile(
                    mode='w', 
                    encoding='utf-8', 
                    delete=False,
                    dir=os.path.dirname(filename) if os.path.dirname(filename) else '.',
                    suffix='.tmp'
                )
                
                json.dump(data, temp_file, indent=4, ensure_ascii=False, sort_keys=True)
                temp_file.flush()
                os.fsync(temp_file.fileno())
                temp_file.close()
                
                if os.path.exists(filename):
                    os.replace(temp_file.name, filename)
                else:
                    os.rename(temp_file.name, filename)
                
                return
                
            except Exception as e:
                if temp_file and os.path.exists(temp_file.name):
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                raise e

        except Exception as e:
            if attempt == max_retries - 1:
                print(f"❌ Save failed {filename} after {max_retries} Attempts")
            time.sleep(0.5)

# OwNeRs SeT
def load_owners():
    return load_data(OWNERS_FILE)

def save_owners(owners_list):
    save_data(owners_list, OWNERS_FILE)

def is_owner(user_id):
    owners = load_owners()
    return str(user_id) in owners

def add_owner(user_id):
    owners = load_owners()
    owners[str(user_id)] = {
        "added_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "added_by": "system"
    }
    save_owners(owners)
    log_action("OWNER_ADDED", details=f"New owner: {user_id}")

def remove_owner(user_id):
    owners = load_owners()
    if str(user_id) in owners:
        del owners[str(user_id)]
        save_owners(owners)
        log_action("OWNER_REMOVED", details=f"Removed owner: {user_id}")
        return True
    return False

# GrOuP SeT
def load_allowed_groups():
    global allowed_groups_cache, cache_last_updated
    
    current_time = time.time()
    if current_time - cache_last_updated < CACHE_TIMEOUT and allowed_groups_cache:
        return allowed_groups_cache
    
    data = load_data(ALLOWED_GROUPS_FILE)
    
    current_time = time.time()
    cleaned_data = {}
    expired_count = 0
    
    for group_id, group_data in data.items():
        expire_time = group_data.get('expire_at', 0)
        if expire_time > current_time:
            cleaned_data[group_id] = group_data
        else:
            expired_count += 1
    
    if expired_count > 0:
        save_data(cleaned_data, ALLOWED_GROUPS_FILE)
    
    allowed_groups_cache = cleaned_data
    cache_last_updated = current_time
    
    return cleaned_data

def save_allowed_groups(data):
    global allowed_groups_cache, cache_last_updated
    save_data(data, ALLOWED_GROUPS_FILE)
    allowed_groups_cache = data
    cache_last_updated = time.time()

def is_group_allowed(group_id):
    allowed_groups = load_allowed_groups()
    group_data = allowed_groups.get(str(group_id), {})
    expire_time = group_data.get('expire_at', 0)
    
    return expire_time > time.time()

def add_allowed_group(group_id, days=365):
    allowed_groups = load_allowed_groups()
    expire_time = int(time.time()) + (days * 24 * 60 * 60)
    
    allowed_groups[str(group_id)] = {
        "expire_at": expire_time,
        "added_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "days": days,
        "expire_date": datetime.fromtimestamp(expire_time).strftime('%Y-%m-%d %H:%M:%S')
    }
    
    save_allowed_groups(allowed_groups)
    
    expire_date = datetime.fromtimestamp(expire_time).strftime('%Y-%m-%d %H:%M:%S')
    print(f"✅ The group has been activated {group_id} For the duration {days} Day, ending on: {expire_date}")
    log_action("GROUP_ADDED", details=f"Group: {group_id}, Days: {days}, Expire: {expire_date}")
    
    return expire_time

def remove_allowed_group(group_id):
    allowed_groups = load_allowed_groups()
    group_id_str = str(group_id)
    
    if group_id_str in allowed_groups:
        del allowed_groups[group_id_str]
        save_allowed_groups(allowed_groups)
        print(f"🗑️ The group has been deactivated: {group_id}")
        log_action("GROUP_REMOVED", details=f"Group: {group_id}")
        
        try:
            bot.send_message(group_id, "👋 GOOD BYE! - The group has been deactivated.")
            time.sleep(1)
            bot.leave_chat(group_id)
            print(f"👋 The bot left the group: {group_id}")
            log_action("GROUP_LEFT", details=f"Group: {group_id} - Removed by owner")
        except Exception as e:
            print(f"⚠️ The bot was unable to leave the group {group_id}: {e}")
            log_action("GROUP_LEAVE_ERROR", details=f"Group: {group_id} | Error: {str(e)}")
        
        return True
    
    print(f"⚠️ The group {group_id} does not exist in the list")
    return False

def check_and_leave_expired_groups():
    allowed_groups = load_allowed_groups()
    current_time = time.time()
    expired_groups = []

    for group_id, group_data in allowed_groups.items():
        if group_data.get('expire_at', 0) < current_time:
            expired_groups.append(group_id)

    for group_id in expired_groups:
        try:
            print(f"👋 Leaving the group that has ended: {group_id}")
            bot.send_message(group_id, "👋 GOOD BYE! - The group activation period has ended.")
            time.sleep(1)
            bot.leave_chat(group_id)
            log_action("GROUP_LEFT", details=f"Group: {group_id} - Subscription expired")
        except Exception as e:
            print(f"⚠️ Error leaving the group {group_id}: {e}")
            log_action("GROUP_LEAVE_ERROR", details=f"Group: {group_id} | Error: {str(e)}")
        finally:
            remove_allowed_group(group_id)
    
    if expired_groups:
        print(f"🧹 Departure {len(expired_groups)} Expired set")

#LoGiN CoDe SeT
def load_activation_codes():
    return load_data(ACTIVATION_CODES_FILE)

def save_activation_codes(data):
    save_data(data, ACTIVATION_CODES_FILE)

def generate_activation_code(days=365):
    code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    activation_codes = load_activation_codes()
    activation_codes[code] = {
        "days": days,
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "used_by": None,
        "expire_at": int(time.time()) + (365 * 24 * 60 * 60),
        "expire_date": datetime.fromtimestamp(int(time.time()) + (365 * 24 * 60 * 60)).strftime('%Y-%m-%d %H:%M:%S')
    }
    save_activation_codes(activation_codes)
    log_action("CODE_GENERATED", details=f"Code: {code}, Days: {days}")
    return code

def use_activation_code(code, user_id):
    activation_codes = load_activation_codes()
    code_data = activation_codes.get(code, {})
    
    if not code_data:
        return False, "Invalid code"
    
    if code_data.get('used_by'):
        return False, "The code is already in use."
    
    if code_data.get('expire_at', 0) < time.time():
        return False, "Expired code"
    
    days = code_data['days']
    expire_time = add_activation(user_id, days)
    
    code_data['used_by'] = user_id
    code_data['used_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    activation_codes[code] = code_data
    save_activation_codes(activation_codes)
    
    log_action("CODE_USED", user_id, f"Code: {code}, Days: {days}")
    return True, f"Your account has been activated for a period of {days} day"

# UsErS & AtTeMpTs SeT
def add_user(user_id, username):
    users = load_data(USERS_FILE)
    users[str(user_id)] = {
        "username": clean_text(username),
        "spam_attempts": 3, # UsErS AtTeMpTs
        "last_reset": time.time(),  
        "first_seen": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "last_active": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "is_owner": is_owner(user_id)
    }
    save_data(users, USERS_FILE)
    log_action("NEW_USER", user_id, f"Username: {username}")

def get_user_attempts(user_id, command_type):
    users = load_data(USERS_FILE)
    user_data = users.get(str(user_id), {})
    
    if not user_data:
        username = "unknown"
        add_user(user_id, username)
        user_data = users.get(str(user_id), {})
    
    if has_unlimited_attempts(user_id) and command_type == 'spam':
        return float('inf')
    
    last_reset = user_data.get('last_reset', 0)
    current_time = time.time()
    
    if current_time - last_reset >= 2 * 60 * 60:
        user_data['spam_attempts'] = 3
        user_data['last_reset'] = current_time
        users[str(user_id)] = user_data
        save_data(users, USERS_FILE)
    
    if command_type == 'spam':
        return user_data.get('spam_attempts', 3)
    return 0

def use_attempt(user_id, command_type):
    if has_unlimited_attempts(user_id) and command_type == 'spam':
        return True
        
    users = load_data(USERS_FILE) 
    user_data = users.get(str(user_id), {})
    
    if command_type == 'spam':
        current_attempts = user_data.get('spam_attempts', 3)
        if current_attempts > 0:
            user_data['spam_attempts'] = current_attempts - 1
            users[str(user_id)] = user_data
            save_data(users, USERS_FILE) 
            return True
        else:
            return False
    
    return False

def has_unlimited_attempts(user_id):
    return is_owner(user_id) or is_user_activated(user_id)

def update_user_activity(user_id):
    users = load_data(USERS_FILE)
    if str(user_id) in users:
        users[str(user_id)]['last_active'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_data(users, USERS_FILE)
        
def restore_expired_attempts():
    users = load_data(USERS_FILE)
    current_time = time.time()
    restored_count = 0
    
    for user_id, user_data in users.items():
        last_reset = user_data.get('last_reset', 0)
        if current_time - last_reset >= 2 * 60 * 60:
            if not has_unlimited_attempts(int(user_id)):
                user_data['spam_attempts'] = 3
                user_data['last_reset'] = current_time
                restored_count += 1
    
    if restored_count > 0:
        save_data(users, USERS_FILE)
        print(f"🔄 Attempts for user {restored_count} have been restored")
    
    return restored_count        

def background_tasks():
    while True:
        try:
            expired_activations = check_expired_activations()
            check_and_leave_expired_groups()
            restore_expired_attempts()
            time.sleep(60 * 30)

        except Exception as e:
            time.sleep(60)
# TeMpOrArY AcTiVaTiOn SeT
def add_activation(user_id, days):
    activations = load_data(ACTIVATIONS_FILE)
    expire_time = int(time.time()) + (days * 24 * 60 * 60)
    activations[str(user_id)] = {
        "expire_at": expire_time,
        "activated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "days": days,
        "expire_date": datetime.fromtimestamp(expire_time).strftime('%Y-%m-%d %H:%M:%S')
    }
    save_data(activations, ACTIVATIONS_FILE)
    log_action("USER_ACTIVATED", user_id, f"Days: {days}")
    return expire_time

def is_user_activated(user_id):
    if is_owner(user_id):
        return True
        
    activations = load_data(ACTIVATIONS_FILE)
    user_activation = activations.get(str(user_id), {})
    expire_time = user_activation.get('expire_at', 0)
    
    if expire_time > time.time():
        return True
    else:
        if str(user_id) in activations:
            del activations[str(user_id)]
            save_data(activations, ACTIVATIONS_FILE)
        return False

def has_unlimited_attempts(user_id):
    return is_owner(user_id) or is_user_activated(user_id)

def get_activation_info(user_id):
    activations = load_data(ACTIVATIONS_FILE)
    return activations.get(str(user_id))

def check_expired_activations():
    activations = load_data(ACTIVATIONS_FILE)
    current_time = time.time()
    expired = []
    
    for user_id, data in activations.items():
        if data.get('expire_at', 0) < current_time:
            expired.append(user_id)
    
    for user_id in expired:
        del activations[user_id]
    
    if expired:
        save_data(activations, ACTIVATIONS_FILE)
        log_action("ACTIVATIONS_EXPIRED", details=f"Count: {len(expired)}")
    
    return expired

# VeRiFy PeRmIsSiOnS SeT
def is_private_chat(message):
    return message.chat.type == 'private'

def check_access(message):
    user_id = message.from_user.id
    
    if is_owner(user_id):
        return True
    
    if not is_private_chat(message):
        return is_group_allowed(message.chat.id)
    
    if is_private_chat(message):
        return is_user_activated(user_id)
    
    return False

def should_respond(message):
    user_id = message.from_user.id
    
    if is_owner(user_id):
        return True
    
    if not is_private_chat(message):
        return is_group_allowed(message.chat.id)
    
    if is_private_chat(message):
        return is_user_activated(user_id)
    
    return False

# RaNdOm CoLoR SeT
def generate_random_color():
    color_list = [
        "[00FF00][b][c]", "[FFDD00][b][c]", "[3813F3][b][c]", "[FF0000][b][c]",
        "[0000FF][b][c]", "[FFA500][b][c]", "[DF07F8][b][c]", "[11EAFD][b][c]",
        "[DCE775][b][c]", "[A8E6CF][b][c]", "[7CB342][b][c]", "[FFB300][b][c]",
        "[90EE90][b][c]", "[FF4500][b][c]", "[FFD700][b][c]", "[32CD32][b][c]",
        "[87CEEB][b][c]", "[9370DB][b][c]", "[FF69B4][b][c]", "[8A2BE2][b][c]",
        "[00BFFF][b][c]", "[1E90FF][b][c]", "[20B2AA][b][c]", "[00FA9A][b][c]",
        "[008000][b][c]", "[FFFF00][b][c]", "[FF8C00][b][c]", "[DC143C][b][c]"
    ]
    return random.choice(color_list)

def get_random_accounts(count=1):
    with connected_clients_lock:
        if not connected_clients:
            return []
        available_clients = list(connected_clients.values())
        if count >= len(available_clients):
            return available_clients
        return random.sample(available_clients, count)

def AuTo_ResTartinG():
    time.sleep(6 * 60 * 60)
    print('\n - AuTo ResTartinG The BoT ... ! ')
    p = psutil.Process(os.getpid())
    for handler in p.open_files():
        try:
            os.close(handler.fd)
        except Exception as e:
            print(f" - Error CLose Files : {e}")
    for conn in p.net_connections():
        try:
            if hasattr(conn, 'fd'):
                os.close(conn.fd)
        except Exception as e:
            print(f" - Error CLose Connection : {e}")
    sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))
    python = sys.executable
    os.execl(python, python, *sys.argv)
       
def ResTarT_BoT():
    print('\n - ResTartinG The BoT ... ! ')
    p = psutil.Process(os.getpid())
    open_files = p.open_files()
    connections = p.net_connections()
    for handler in open_files:
        try:
            os.close(handler.fd)
        except Exception:
            pass           
    for conn in connections:
        try:
            conn.close()
        except Exception:
            pass
    sys.path.append(os.path.dirname(os.path.abspath(sys.argv[0])))
    python = sys.executable
    os.execl(python, python, *sys.argv)
# GhOsT SeT
def execute_ghost_command(client, teamcode, name, user_id, client_number, clients_list):
    success = False
    try:
        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key and hasattr(client, 'iv') and client.iv:
            
            join_packet = JoinTeamCode(teamcode, client.key, client.iv)
            client.CliEnts2.send(join_packet)
            
            start_time = time.time()
            response_received = False
            
            while time.time() - start_time < 8:
                try:
                    if hasattr(client, 'DaTa2') and client.DaTa2 and len(client.DaTa2.hex()) > 30:
                        hex_data = client.DaTa2.hex()
                        if '0500' in hex_data[0:4]:
                            
                            try:
                                if "08" in hex_data:
                                    decoded_data = DeCode_PackEt(f'08{hex_data.split("08", 1)[1]}')
                                else:
                                    decoded_data = DeCode_PackEt(hex_data[10:])
                                
                                dT = json.loads(decoded_data)
                                
                                if "5" in dT and "data" in dT["5"]:
                                    team_data = dT["5"]["data"]
                                    
                                    if "31" in team_data and "data" in team_data["31"]:
                                        sq = team_data["31"]["data"]
                                        idT = team_data["1"]["data"]
                                        
                                        client.CliEnts2.send(ExitBot('000000', client.key, client.iv))
                                        time.sleep(0.2)
                                        
                                        ghost_packet = GhostPakcet(idT, name, sq, client.key, client.iv)
                                        client.CliEnts2.send(ghost_packet)
                                        
                                        success = True
                                        response_received = True
                                        break
                                    
                            except Exception as decode_error:
                                try:
                                    if len(hex_data) > 20:
                                        alternative_data = DeCode_PackEt(hex_data)
                                        if alternative_data:
                                            pass
                                except:
                                    pass
                    
                    time.sleep(0.1)
                    
                except Exception as loop_error:
                    time.sleep(0.1)
            
            if not response_received:
                try:
                    ghost_packet_alt = GhostPakcet(teamcode, name, "1", client.key, client.iv)
                    client.CliEnts2.send(ghost_packet_alt)
                    time.sleep(0.5)
                    success = True
                except Exception as alt_error:
                    pass
            
        else:
            pass
            
    except Exception as e:
        pass
    
    return success

# SpAm SoLo & Sq SeT
def infinite_spam_worker(target_id):
    while True:
        with active_spam_lock:
            if target_id not in active_spam_targets:
                break
                
        try:
            send_spam_from_all_accounts(target_id)
            time.sleep(0.1)
        except Exception as e:
            time.sleep(0.1)

def send_spam_from_all_accounts(target_id):
    with connected_clients_lock:
        for account_id, client in connected_clients.items():
            try:
                if (hasattr(client, 'CliEnts2') and client.CliEnts2 and 
                    hasattr(client, 'key') and client.key and 
                    hasattr(client, 'iv') and client.iv):
                    
                    for i in range(10):
                        try:
                            client.CliEnts2.send(SEnd_InV(1, target_id, client.key, client.iv))                           
                            client.CliEnts2.send(OpEnSq(client.key, client.iv))                            
                            client.CliEnts2.send(SPamSq(target_id, client.key, client.iv))
                        except (BrokenPipeError, ConnectionResetError, OSError) as e:
                            break
                        except Exception as e:
                            break
                else:
                    pass
            except Exception as e:
                pass
                
# GhOsT LaG SeT
def execute_blrx_command(client, teamcode, name, user_id, client_number):
    success = False
    try:
        
        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key and hasattr(client, 'iv') and client.iv:
            
            join_packet = JoinTeamCode(teamcode, client.key, client.iv)
            client.CliEnts2.send(join_packet)
            
            start_time = time.time()
            response_received = False
            idT = None
            sq = None
            
            while time.time() - start_time < 8:
                try:
                    if hasattr(client, 'DaTa2') and client.DaTa2 and len(client.DaTa2.hex()) > 30:
                        hex_data = client.DaTa2.hex()
                        if '0500' in hex_data[0:4]:
                            
                            try:
                                if "08" in hex_data:
                                    decoded_data = DeCode_PackEt(f'08{hex_data.split("08", 1)[1]}')
                                else:
                                    decoded_data = DeCode_PackEt(hex_data[10:])
                                
                                dT = json.loads(decoded_data)
                                
                                if "5" in dT and "data" in dT["5"]:
                                    team_data = dT["5"]["data"]
                                    
                                    if "31" in team_data and "data" in team_data["31"]:
                                        sq = team_data["31"]["data"]
                                        idT = team_data["1"]["data"]
                                        
                                        response_received = True
                                        break
                                    
                            except Exception as decode_error:
                                try:
                                    if len(hex_data) > 20:
                                        alternative_data = DeCode_PackEt(hex_data)
                                        if alternative_data:
                                            pass
                                except:
                                    pass
                    
                    time.sleep(0.1)
                    
                except Exception as loop_error:
                    time.sleep(0.1)
            
            if response_received and idT and sq:
                
                for i in range(999):
                    try:
                        client.CliEnts2.send(JoinTeamCode(teamcode, client.key, client.iv))
                        client.CliEnts2.send(GhostPakcet(idT, name, sq, client.key, client.iv))
                        time.sleep(0.1)
                        client.CliEnts2.send(ExitBot('000000', client.key, client.iv))
                        client.CliEnts2.send(GhostPakcet(idT, name, sq, client.key, client.iv))
                    except Exception as e:
                        break
                
                success = True
                
        else:
            pass
            
    except Exception as e:
        pass
    
    return success

# LaG  SET
def execute_lag_command(client, teamcode, user_id, client_number):
    success = False
    try:
        
        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key and hasattr(client, 'iv') and client.iv:
            
            for i in range(400):
                try:
                    client.CliEnts2.send(JoinTeamCode(teamcode, client.key, client.iv))
                    client.CliEnts2.send(ExitBot('000000', client.key, client.iv))
                    time.sleep(0.1)
                except Exception as e:
                    break
            
            success = True
            
        else:
            pass
            
    except Exception as e:
        pass
    
    return success

#C OnLiNe MeRo KInG SeT
class FF_CLient():

    def __init__(self, id, password):
        self.id = id
        self.password = password
        self.key = None
        self.iv = None
        self.Get_FiNal_ToKen_0115()     
            
    def Connect_SerVer_OnLine(self , Token , tok , host , port , key , iv , host2 , port2):
            try:
                self.AutH_ToKen_0115 = tok    
                self.CliEnts2 = socket.create_connection((host2 , int(port2)))
                self.CliEnts2.send(bytes.fromhex(self.AutH_ToKen_0115))                  
            except:pass        
            while True:
                try:
                    self.DaTa2 = self.CliEnts2.recv(99999)
                    if '0500' in self.DaTa2.hex()[0:4] and len(self.DaTa2.hex()) > 30:	         	    	    
                            self.packet = json.loads(DeCode_PackEt(f'08{self.DaTa2.hex().split("08", 1)[1]}'))
                            self.AutH = self.packet['5']['data']['7']['data']
                    
                except:pass    	
                                                            
    def Connect_SerVer(self , Token , tok , host , port , key , iv , host2 , port2):
            self.AutH_ToKen_0115 = tok    
            self.CliEnts = socket.create_connection((host , int(port)))
            self.CliEnts.send(bytes.fromhex(self.AutH_ToKen_0115))  
            self.DaTa = self.CliEnts.recv(1024)          	        
            threading.Thread(target=self.Connect_SerVer_OnLine, args=(Token , tok , host , port , key , iv , host2 , port2)).start()
            self.Exemple = xMsGFixinG('12345678')
            
            self.key = key
            self.iv = iv
            
            with connected_clients_lock:
                connected_clients[self.id] = self
            
            while True:      
                try:
                    self.DaTa = self.CliEnts.recv(1024)   
                    if len(self.DaTa) == 0 or (hasattr(self, 'DaTa2') and len(self.DaTa2) == 0):	            		
                        try:            		    
                            self.CliEnts.close()
                            if hasattr(self, 'CliEnts2'):
                                self.CliEnts2.close()
                            self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)                    		                    
                        except:
                            try:
                                self.CliEnts.close()
                                if hasattr(self, 'CliEnts2'):
                                    self.CliEnts2.close()
                                self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)
                            except:
                                self.CliEnts.close()
                                if hasattr(self, 'CliEnts2'):
                                    self.CliEnts2.close()
                                ResTarT_BoT()	            
# MeRo KiNg MsG In BoT xFFx                                      
                    if '1200' in self.DaTa.hex()[0:4] and 900 > len(self.DaTa.hex()) > 100:
                        if b"***" in self.DaTa:
                            self.DaTa = self.DaTa.replace(b"***",b"106")         
                        try:
                           self.BesTo_data = json.loads(DeCode_PackEt(self.DaTa.hex()[10:]))	       
                           self.input_msg = 'besto_love' if '8' in self.BesTo_data["5"]["data"] else self.BesTo_data["5"]["data"]["4"]["data"]
                        except: 
                            self.input_msg = None	   	 
                        self.DeCode_CliEnt_Uid = self.BesTo_data["5"]["data"]["1"]["data"]
                        self.CliEnt_Uid = EnC_Uid(self.DeCode_CliEnt_Uid , Tp = 'Uid')
                               
                    if 'besto_love' in self.input_msg[:10]:
                        self.CliEnts.send(GenResponsMsg(f'''
[C][B][000000]━━━━━━━━━━━━   
                     
[FFD700]👑SPIDEERIO GAMING👑

[FF4500]🔥RIO </> VIP BOT🔥

[00FF7F]⚡ Speed - Safety - Power
[87CEEB]🚀 Designed to always be the best

[C][B][000000]━━━━━━━━━━━━

[00BFFF]💎YouTube: @Spideerio
[00BFFF]💎Telegram: @MorpheusBlackEra

[C][B][000000]━━━━━━━━━━━━''', 2 , self.DeCode_CliEnt_Uid , self.DeCode_CliEnt_Uid , key , iv))
                        time.sleep(0.3)
                        self.CliEnts.close()
                        if hasattr(self, 'CliEnts2'):
                            self.CliEnts2.close()
                        self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)	                    	 	 
                                                                         

                except Exception as e:
                    try:
                        self.CliEnts.close()
                        if hasattr(self, 'CliEnts2'):
                            self.CliEnts2.close()
                    except:
                        pass
                    self.Connect_SerVer(Token , tok , host , port , key , iv , host2 , port2)
                                    
    def GeT_Key_Iv(self , serialized_data):
        my_message = xKEys.MyMessage()
        my_message.ParseFromString(serialized_data)
        timestamp , key , iv = my_message.field21 , my_message.field22 , my_message.field23
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        timestamp_seconds = timestamp_obj.seconds
        timestamp_nanos = timestamp_obj.nanos
        combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
        return combined_timestamp , key , iv    

    def Guest_GeneRaTe(self , uid , password):
        self.url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
        self.headers = {
            "Host": "ffmconnect.live.gop.garenanow.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close"
        }
        self.dataa = {
            "uid": f"{uid}",
            "password": f"{password}",
            "response_type": "token",
            "client_type": "2",
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_id": "100067"
        }
        
        try:
            if not uid or not password:
                print(f"❌ Invalid account details: {uid}")
                time.sleep(5)
                return self.Guest_GeneRaTe(uid, password)
                
            self.response = requests.post(self.url, headers=self.headers, data=self.dataa, timeout=30)
            
            if self.response.status_code != 200:
                print(f"❌ Response error: {self.response.status_code}")
                time.sleep(5)
                return self.Guest_GeneRaTe(uid, password)
                
            response_data = self.response.json()
            
            if 'access_token' not in response_data or 'open_id' not in response_data:
                print(f"❌ Incomplete response data: {response_data}")
                time.sleep(5)
                return self.Guest_GeneRaTe(uid, password)
            
            self.Access_ToKen = response_data['access_token']
            self.Access_Uid = response_data['open_id']
            
            print(f'✅ The account token has been obtained: {uid}')
            time.sleep(0.5)

            return self.ToKen_GeneRaTe(self.Access_ToKen , self.Access_Uid)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Account connection error {uid}: {e}")
            time.sleep(5)
            return self.Guest_GeneRaTe(uid, password)
        except Exception as e:
            print(f"❌ Unexpected calculation error {uid}: {e}")
            time.sleep(2)
            return self.Guest_GeneRaTe(uid, password)
                                        
    def GeT_LoGin_PorTs(self , JwT_ToKen , PayLoad):
        self.UrL = 'https://client.us.freefiremobile.com/GetLoginData'
        self.HeadErs = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {JwT_ToKen}',
            'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': 'OB52',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)',
            'Host': 'client.us.freefiremobile.com',
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate, br'
        }       
        try:
            self.Res = requests.post(self.UrL, headers=self.HeadErs, data=PayLoad, verify=False, timeout=30)
            
            if self.Res.content:
                hex_content = self.Res.content.hex()
                try:
                    self.BesTo_data = json.loads(DeCode_PackEt(hex_content))  
                    address = self.BesTo_data['32']['data'] 
                    address2 = self.BesTo_data['14']['data']
                    
                    ip = address[:len(address) - 6] 
                    ip2 = address2[:len(address) - 6]
                    port = address[len(address) - 5:] 
                    port2 = address2[len(address2) - 5:]             
                    
                    return ip , port , ip2 , port2
                except Exception as e:
                    print(f"❌ Port data processing error: {e}")
                    return None, None, None, None
            else:
                print("❌ No data in the response")
                return None, None, None, None
                
        except requests.RequestException as e:
            print(f"❌ Port request error: {e}")
            return None, None, None, None
        except Exception as e:
            print(f"❌ Unexpected error in port request: {e}")
            return None, None, None, None
#PyL MeRo        
#PyL MeRo        
    def ToKen_GeneRaTe(self , Access_ToKen , Access_Uid):
        self.UrL = "https://loginbp.ggblueshark.com/MajorLogin"
        self.HeadErs = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB52',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'Content-Length': '880',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': 'clientbp.ggblueshark.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'   
        }   
        
        base_data = '1a13323032352d31312d32362030313a35313a3238220966726565206669726528013a07312e3132302e314232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520c4d544e2f537061636574656c5a045749464960800a68d00572033234307a2d7838362d3634205353453320535345342e3120535345342e32204156582041565832207c2032343030207c20348001e61e8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c36323566373136662d393161372d343935622d396631362d303866653964336336353333a2010e3137362e32382e3133392e313835aa01026172b201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010d4f6e65506c7573204135303130ea014063363961653230386661643732373338623637346232383437623530613361316466613235643161313966616537343566633736616334613065343134633934f00101ca020c4d544e2f537061636574656cd2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003b5ee02e8039a8002f003af13f80384078004a78f028804b5ee029004a78f029804b5ee02b00404c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f6c69622f61726de00401ea045f65363261623933353464386662356662303831646233333861636233333439317c2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f626173652e61706bf00406f804018a050233329a050a32303139313139303236a80503b205094f70656e474c455332b805ff01c00504e005be7eea05093372645f7061727479f205704b717348543857393347646347335a6f7a454e6646775648746d377171316552554e6149444e67526f626f7a4942744c4f695943633459367a767670634943787a514632734f453463627974774c7334785a62526e70524d706d5752514b6d654f35766373386e51594268777148374bf805e7e4068806019006019a060134a2060134b2062213521146500e590349510e460900115843395f005b510f685b560a6107576d0f0366'
        
        try:
            self.dT = bytes.fromhex(base_data)
            
            current_time = str(datetime.now())[:-7].encode()
            self.dT = self.dT.replace(b'2025-07-30 14:11:20', current_time)        
            self.dT = self.dT.replace(b'4e79affe31414901544eaabebc4705738fe683a92dd4c5ee3db33662b2e9664f', Access_ToKen.encode())
            self.dT = self.dT.replace(b'4306245793de86da425a52caadf21eed', Access_Uid.encode())
            
            try:
                hex_data = self.dT.hex()
                if all(c in '0123456789abcdef' for c in hex_data):
                    encoded_data = EnC_AEs(hex_data)
                    self.PaYload = bytes.fromhex(encoded_data)
                else:
                    print("❌ Data not valid for encryption")
                    self.PaYload = self.dT
            except Exception as encoding_error:
                print(f"❌ Encryption error: {encoding_error}")
                self.PaYload = self.dT
        
        except ValueError as e:
            print(f"❌ Data conversion error: {e}")
            self.PaYload = f"uid={Access_Uid}&token={Access_ToKen}".encode()
           # Example payload (replace with your actual body)
            data = {
                'AccessToken': Access_ToKen,
                'AccessUid': Access_Uid
            }

            response = requests.post(self.UrL, data=data, headers=self.HeadErs)
            print(response.status_code)
            print(response.text)
        try:
            self.ResPonse = requests.post(self.UrL, headers=self.HeadErs, data=self.PaYload, verify=False, timeout=30)
            
            if self.ResPonse.status_code == 200 and len(self.ResPonse.text) > 10:
                try:
                    if self.ResPonse.content:
                        hex_content = self.ResPonse.content.hex()
                        self.BesTo_data = json.loads(DeCode_PackEt(hex_content))
                        self.JwT_ToKen = self.BesTo_data['8']['data']           
                        self.combined_timestamp , self.key , self.iv = self.GeT_Key_Iv(self.ResPonse.content)
                        ip , port , ip2 , port2 = self.GeT_LoGin_PorTs(self.JwT_ToKen , self.PaYload)            
                        return self.JwT_ToKen , self.key , self.iv, self.combined_timestamp , ip , port , ip2 , port2
                    else:
                        print("❌ No data in the token response")
                        raise Exception("No data in token response")
                except Exception as e:
                    print(f"❌ Error in parsing the token response: {e}")
                    time.sleep(2)
                    return self.ToKen_GeneRaTe(Access_ToKen, Access_Uid)
            else:
                print(f"❌ Token response error, status: {self.ResPonse.status_code}")
                time.sleep(2)
                return self.ToKen_GeneRaTe(Access_ToKen, Access_Uid)
                
        except requests.RequestException as e:
            print(f"❌ Token request error: {e}")
            time.sleep(5)
            return self.ToKen_GeneRaTe(Access_ToKen, Access_Uid)
        except Exception as e:
            print(f"❌ Unexpected error in token request: {e}")
            time.sleep(2)
            return self.ToKen_GeneRaTe(Access_ToKen, Access_Uid)
      
    def Get_FiNal_ToKen_0115(self):
        try:
            result = self.Guest_GeneRaTe(self.id , self.password)
            if not result:
                print("❌ Failed to obtain tokens, try again...")
                time.sleep(2)
                return self.Get_FiNal_ToKen_0115()
                
            token , key , iv , Timestamp , ip , port , ip2 , port2 = result
            
            if not all([ip, port, ip2, port2]):
                print("❌ Failed to obtain ports, please try again...")
                time.sleep(2)
                return self.Get_FiNal_ToKen_0115()
                
            self.JwT_ToKen = token        
            try:
                self.AfTer_DeC_JwT = jwt.decode(token, options={"verify_signature": False})
                self.AccounT_Uid = self.AfTer_DeC_JwT.get('account_id')
                self.EncoDed_AccounT = hex(self.AccounT_Uid)[2:]
                self.HeX_VaLue = DecodE_HeX(Timestamp)
                self.TimE_HEx = self.HeX_VaLue
                self.JwT_ToKen_ = token.encode().hex()
            except Exception as e:
                print(f"❌ Token decoding error: {e}")
                time.sleep(2)
                return self.Get_FiNal_ToKen_0115()
                
            try:
                self.Header = hex(len(EnC_PacKeT(self.JwT_ToKen_, key, iv)) // 2)[2:]
                length = len(self.EncoDed_AccounT)
                self.__ = '00000000'
                if length == 9: self.__ = '0000000'
                elif length == 8: self.__ = '00000000'
                elif length == 10: self.__ = '000000'
                elif length == 7: self.__ = '000000000'
                else:
                    print('Unexpected length encountered')                
                self.Header = f'0115{self.__}{self.EncoDed_AccounT}{self.TimE_HEx}00000{self.Header}'
                self.FiNal_ToKen_0115 = self.Header + EnC_PacKeT(self.JwT_ToKen_ , key , iv)
            except Exception as e:
                print(f"❌ Error in the final token: {e}")
                time.sleep(5)
                return self.Get_FiNal_ToKen_0115()
                
            self.AutH_ToKen = self.FiNal_ToKen_0115
            self.Connect_SerVer(self.JwT_ToKen , self.AutH_ToKen , ip , port , key , iv , ip2 , port2)        
            return self.AutH_ToKen , key , iv
            
        except Exception as e:
            print(f"❌ Error in Get_FiNal_ToKen_0115: {e}")
            time.sleep(10)
            return self.Get_FiNal_ToKen_0115()

#AcSS MeRo SeT
ACCOUNTS = []

def load_accounts_from_file(filename="accs.txt"):
    accounts = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    if ":" in line:
                        parts = line.split(":")
                        if len(parts) >= 2:
                            account_id = parts[0].strip()
                            password = parts[1].strip()
                            accounts.append({'id': account_id, 'password': password})
                    else:
                        accounts.append({'id': line.strip(), 'password': ''})
        print(f"{len(accounts)} account was uploaded from {filename}")
    except FileNotFoundError:
        print(f"The file {filename} does not exist!")
    except Exception as e:
        print(f"An error occurred while reading the file.: {e}")
    
    return accounts

ACCOUNTS = load_accounts_from_file()

if not ACCOUNTS:
    ACCOUNTS = [{'id': '4580134664', 'password': '5B5D54CACA62B4DD5A86FA85EE5988AF9FC5BD782BDA501AFC7E471435002713'}]

def start_account(account):
    try:
        FF_CLient(account['id'], account['password'])
    except Exception as e:
        print(f"❌ Error starting account {account['id']}: {e}")
        time.sleep(2)
        start_account(account)

# 5 Sq & 6 Sq SeT
def execute_5x_command(client, target_id, user_id, client_number):
    success = False
    try:
        
        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key and hasattr(client, 'iv') and client.iv:
            
            account_uid = getattr(client, 'AccounT_Uid', client.id)
            
            client.CliEnts2.send(OpEnSq(client.key, client.iv))
            time.sleep(0.5)
            
            client.CliEnts2.send(cHSq(5, account_uid, client.key, client.iv))
            time.sleep(0.5)
            
            client.CliEnts2.send(SEnd_InV(1, target_id, client.key, client.iv))
            time.sleep(5)
            client.CliEnts2.send(ExitBot('000000' , client.key, client.iv))                 
            success = True
            
        else:
            pass
            
    except Exception as e:
        pass
    
    return success

def execute_6x_command(client, target_id, user_id, client_number):
    success = False
    try:
        
        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key and hasattr(client, 'iv') and client.iv:
            
            account_uid = getattr(client, 'AccounT_Uid', client.id)
            
            client.CliEnts2.send(OpEnSq(client.key, client.iv))
            time.sleep(0.5)
            
            client.CliEnts2.send(cHSq(6, account_uid, client.key, client.iv))
            time.sleep(0.5)
            
            client.CliEnts2.send(SEnd_InV(1, target_id, client.key, client.iv))
            time.sleep(5)
            client.CliEnts2.send(ExitBot('000000' , client.key, client.iv))       
            success = True
            
        else:
            pass
            
    except Exception as e:
        pass
    
    return success

# BaCk TaSk MeRo SeT
def background_tasks():
    while True:
        try:
            expired_activations = check_expired_activations()
            check_and_leave_expired_groups()
            time.sleep(60 * 30) 

        except Exception as e:
            time.sleep(60)

# BoT TeLeGrAm SeT
def silent_ignore(message):
    pass

# LoGin CoDe SeT
def handle_activation_code(message):
    user_id = message.from_user.id
    code = message.text.upper()
    
    # الحصول على معلومات المستخدم الحقيقية
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # بناء اسم المستخدم
    if username:
        display_username = f"@{username}"
    else:
        display_username = first_name or "user"
        if last_name:
            display_username += f" {last_name}"
    
    # إضافة المستخدم إذا لم يكن موجوداً
    if not load_data(USERS_FILE).get(str(user_id)):
        add_user(user_id, display_username)
    
    try:
        success, message_text = use_activation_code(code, user_id)
        
        if success:
            activation_info = get_activation_info(user_id)
            expire_date = datetime.fromtimestamp(activation_info['expire_at']).strftime('%Y-%m-%d %H:%M:%S')
            
            response_text = f"""
✅ <b>Your account has been successfully activated!</b>

📝 <b>Activation details:</b>
👤 User: {display_username}
🆔 ID: <code>{user_id}</code>
⏰ Expiry date: {expire_date}
🔑 code used: <code>{code}</code>
💎 <b>Now you can use all bot commands</b>
            """
        else:
            response_text = f"❌ <b>{message_text}</b>"
        
        bot.send_message(message.chat.id, response_text, reply_to_message_id=message.message_id)
        update_user_activity(user_id)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>An error occurred during activation.:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("DIRECT_ACTIVATION_ERROR", user_id, str(e))

# xC MsG SeT
def is_command(message, command_name):
    text = message.text.lower().strip()
    command_name = command_name.lower()
    
    if text.startswith(f'/{command_name}') or f'/{command_name}' in text:
        return True
        
    return False
    
# HeLp MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'help'))
def handle_help_command(message):
    if not should_respond(message):
        return silent_ignore(message)
        
    user_id = message.from_user.id
    
    help_text = """
<b>Usages:</b>
<code>/rio {TeamCode}</code> - Lag Attack On Team
    """
#<code>/ghost {TeAm CoDe}</code> - Ghosts enter the team
#<code>/blrx {TeAm CoDe}</code> - Ghost attack on the team
#<code>/hex {PlAyEr Id}</code> - The graveyard starts on the player
#<code>/stop {PlAyEr Id}</code> - Cemetery closure
#<code>/5 {PlAyEr Id}</code> - Sending a team 5
#<code>/add {PlAyEr Id} {TiMe}</code> - Adding the bot to the player
#<code>/remove {PlAyEr Id}</code> - Removing the bot from the player
#<code>/report {TeXt}</code> - Send feedback to the owner
#<code>/6 {PlAyEr Id}</code> - Sending a team 6 
    
    if is_owner(user_id):
        help_text += """
        
<b>👑 Developer commands:</b>

<code>/login {TiMe}</code> - Create activation code
<code>/allow {Id GrOuP} {TiMe}</code> - Activate the group
<code>/unallow {Id GrOuP}</code> - Deactivate
<code>/addowner {UsEr_Id}</code> - Add owner
<code>/removeowner {UsEr_Id}</code> - Remove owner
<code>/listowners</code> - Owners' List
<code>/restart</code> - Restart
<code>/status</code> - Bot status
<code>/accounts</code> - Connected accounts
<code>/list</code> - Displaying the bot's added IDs
<code>/removeall</code> - Delete all IDs
        """
    
    bot.send_message(message.chat.id, help_text, parse_mode='HTML', reply_to_message_id=message.message_id)
    log_action("HELP_REQUESTED", user_id)
    update_user_activity(user_id)
    
# RePoRt MsG SeT    
@bot.message_handler(func=lambda message: is_command(message, 'report'))
def handle_report_command(message):
    if not should_respond(message):
        return silent_ignore(message)
        
    user_id = message.from_user.id
    
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, 
                "⚠️ <b>Please enter the text of the report.</b>\n"
                "📝 <b>example:</b> <code>/report There is a problem with the bot.</code>", 
                reply_to_message_id=message.message_id)
            return
            
        report_text = parts[1]
        
        clean_report = clean_text(report_text)
        
       #GeT UeSr InFo XXXXXX
        user_info = bot.get_chat(user_id)
        username = f"@{user_info.username}" if user_info.username else user_info.first_name
        
        report_message = f"""
🚨 <b>NeW RePoRt MsG</b>

👤 <b>UsEr:</b> {username}
🆔 <b>UsEr Id:</b> <code>{user_id}</code>
⏰ <b>TiMe:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📝 <b>TeXt RePoRt:</b>
{clean_report}
        """
        
        owners = load_owners()
        sent_count = 0
        
        for owner_id in owners.keys():
            try:
                bot.send_message(int(owner_id), report_message)
                sent_count += 1
                time.sleep(0.5)  # WaRNiNg WaRNiNg WaRNiNg  WaRNiNg  WaRNiNg To NoT BaN BoT FrOm TeLe
            except Exception as e:
                print(f"❌ He was unable to send the notification to the owner. {owner_id}: {e}")
        
        if sent_count > 0:
            bot.send_message(message.chat.id, 
                f"✅ <b>Your report has been successfully sent to the owners.</b>\n"
                f"📝 Your report will be reviewed as soon as possible.",
                reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, 
                "❌ <b>Your report was not sent - no active owner accounts.</b>",
                reply_to_message_id=message.message_id)
        
        log_action("REPORT_SENT", user_id, f"Recipients: {sent_count}, Text: {clean_report[:100]}...")
        update_user_activity(user_id)
        
    except Exception as e:
        bot.send_message(message.chat.id, 
            f"❌ <b>An error occurred while sending the message.:</b> {str(e)}", 
            reply_to_message_id=message.message_id)
        log_action("REPORT_COMMAND_ERROR", user_id, str(e))
# TeMp MsG SeT
def send_temp_message(chat_id, text, reply_to_message_id=None):
    try:
        sent_message = bot.send_message(chat_id, text, reply_to_message_id=reply_to_message_id)
        return sent_message.message_id
    except Exception as e:
        print(f"❌ Error sending temporary message: {e}")
        return None
# DeLeT MsG SeT
def delete_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
        return True
    except Exception as e:
        print(f"❌ Error deleting the message: {e}")
        return False
# GhOsT MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'ghost'))
def handle_ghost_command(message):
    if not should_respond(message):
        return silent_ignore(message)
        
    user_id = message.from_user.id
    temp_message_id = None
    
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.send_message(message.chat.id, 
                "⚠️ <b>Please enter teamcode و name</b>\n"
                "📝 <b>Example:</b> <code>/ghost 12345678 mero</code>", 
                reply_to_message_id=message.message_id)
            return
            
        teamcode = parts[1]
        name = ' '.join(parts[2:])
        
        if not ChEck_Commande(teamcode):
            bot.send_message(message.chat.id, "❌ <b>teamcode غير صالح</b>", reply_to_message_id=message.message_id)
            return
        

        temp_message_id = send_temp_message(message.chat.id, 
            f"⏳ <b>Ghost Order is being executed...</b>\n"
            f"🏷️ team: <code>{teamcode}</code>\n"
            f"👻 the name: {name}",
            reply_to_message_id=message.message_id)
        
        clients_list = get_random_accounts(4)
        
        if not clients_list:
            if temp_message_id:
                delete_message(message.chat.id, temp_message_id)
            bot.send_message(message.chat.id, "❌ <b>No accounts are currently online.</b>", reply_to_message_id=message.message_id)
            return
            
        success_count = 0
        threads = []
        results = []
        
        for i, client in enumerate(clients_list, 1):
            thread = threading.Thread(target=lambda c=client, r=results: r.append(execute_ghost_command(c, teamcode, name, user_id, i, clients_list)))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=10)
        
        success_count = sum(results)
        
        if temp_message_id:
            delete_message(message.chat.id, temp_message_id)
        
        bot.send_message(message.chat.id, 
            f"✅ <b>Operation Ghost has been completed</b>\n"
            f"🏷️ team: <code>{teamcode}</code>\n"
            f"👻 the name: {name}\n",
            reply_to_message_id=message.message_id)
        
        update_user_activity(user_id)
        
    except Exception as e:
        if temp_message_id:
            delete_message(message.chat.id, temp_message_id)
        bot.send_message(message.chat.id, f"❌ <b>An error occurred:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("GHOST_COMMAND_ERROR", user_id, str(e))
# BlRx MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'blrx'))
def handle_blrx_command(message):
    if not should_respond(message):
        return silent_ignore(message)
        
    user_id = message.from_user.id
    temp_message_id = None
    
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.send_message(message.chat.id, 
                "⚠️ <b>Please enter teamcode و name</b>\n"
                "📝 <b>Example:</b> <code>/blrx 12345678 mero</code>", 
                reply_to_message_id=message.message_id)
            return
            
        teamcode = parts[1]
        name = ' '.join(parts[2:])
        
        if not ChEck_Commande(teamcode):
            bot.send_message(message.chat.id, "❌ <b>teamcode Invalid</b>", reply_to_message_id=message.message_id)
            return
        
        temp_message_id = send_temp_message(message.chat.id, 
            f"⏳ <b>Order being executed...</b>\n"
            f"🏷️ team: <code>{teamcode}</code>\n"
            f"👻 the name: {name}",
            reply_to_message_id=message.message_id)
        
        clients_list = get_random_accounts(3)
        
        if not clients_list:
            if temp_message_id:
                delete_message(message.chat.id, temp_message_id)
            bot.send_message(message.chat.id, "❌ <b>No accounts are currently online.</b>", reply_to_message_id=message.message_id)
            return
            
        success_count = 0
        threads = []
        results = []
        
        for i, client in enumerate(clients_list, 1):
            thread = threading.Thread(target=lambda c=client, r=results: r.append(execute_blrx_command(c, teamcode, name, user_id, i)))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=60)
        
        success_count = sum(results)
        
        if temp_message_id:
            delete_message(message.chat.id, temp_message_id)
        
        bot.send_message(message.chat.id, 
            f"✅ <b>The process has been completed Blrx</b>\n"
            f"🏷️ team: <code>{teamcode}</code>\n"
            f"👻 the name: {name}\n",
            reply_to_message_id=message.message_id)
        
        update_user_activity(user_id)
        
    except Exception as e:
        if temp_message_id:
            delete_message(message.chat.id, temp_message_id)
        bot.send_message(message.chat.id, f"❌ <b>An error occurred:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("BLRX_COMMAND_ERROR", user_id, str(e))
# LaG MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'rio'))
def handle_lag_command(message):
    if not should_respond(message):
        return silent_ignore(message)
        
    user_id = message.from_user.id
    temp_message_id = None
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, 
                "⚠️ <b>Please enter teamcode</b>\n"
                "📝 <b>Example:</b> <code>/rio 12345678</code>", 
                reply_to_message_id=message.message_id)
            return
            
        teamcode = parts[1]
        
        if not ChEck_Commande(teamcode):
            bot.send_message(message.chat.id, "❌ <b>teamcode Invalid</b>", reply_to_message_id=message.message_id)
            return
        
        temp_message_id = send_temp_message(message.chat.id, 
            f"⏳ <b>Order being executed Lag...</b>\n"
            f"🏷️ team: <code>{teamcode}</code>",
            reply_to_message_id=message.message_id)
        
        clients_list = get_random_accounts(3)
        
        if not clients_list:
            if temp_message_id:
                delete_message(message.chat.id, temp_message_id)
            bot.send_message(message.chat.id, "❌ <b>No accounts are currently online.</b>", reply_to_message_id=message.message_id)
            return
            
        success_count = 0
        threads = []
        
        for i, client in enumerate(clients_list, 1):
            thread = threading.Thread(target=lambda c=client, sc=success_count: execute_lag_command(c, teamcode, user_id, i))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=30)
        
        if temp_message_id:
            delete_message(message.chat.id, temp_message_id)
        
        bot.send_message(message.chat.id, 
            f"✅ <b>The process has been completed Lag</b>\n"
            f"🏷️ team: <code>{teamcode}</code>\n"
            f"🔧 Accounts used: {len(clients_list)}",
            reply_to_message_id=message.message_id)
        
        update_user_activity(user_id)
        
    except Exception as e:
        if temp_message_id:
            delete_message(message.chat.id, temp_message_id)
        bot.send_message(message.chat.id, f"❌ <b>An error occurred:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("LAG_COMMAND_ERROR", user_id, str(e))
# 5 & 6 MsG SeT

# 🔥 SPAM VIP COMMAND
@bot.message_handler(func=lambda message: is_command(message, 'spamvip'))
def handle_spamvip_command(message):
    if not should_respond(message):
        return silent_ignore(message)
        
    user_id = message.from_user.id
    temp_message_id = None
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(
                message.chat.id,
                "⚠️ <b>Please enter UID</b>\n"
                "📝 <b>Example:</b> <code>/spamvip 168274223</code>",
                reply_to_message_id=message.message_id
            )
            return
            
        uid = parts[1]
        
        if not uid.isdigit():
            bot.send_message(
                message.chat.id,
                "❌ <b>Invalid UID</b>",
                reply_to_message_id=message.message_id
            )
            return
        
        temp_message_id = send_temp_message(
            message.chat.id,
            f"⏳ <b>SpamVip in progress...</b>\n"
            f"👤 UID: <code>{uid}</code>",
            reply_to_message_id=message.message_id
        )
        
        success_count = 0
        
        for i in range(3):
            try:
                response = requests.get(
                    f"https://ff-ave4.onrender.com/spm?uid={uid}",
                    timeout=15
                )
                
                if response.status_code == 200:
                    success_count += 1
                    
            except:
                pass
            
            # ⏳ Espera 3 segundos entre chamadas
            if i < 2:
                time.sleep(3)
        
        if temp_message_id:
            delete_message(message.chat.id, temp_message_id)
        
        bot.send_message(
            message.chat.id,
            f"✅ <b>SpamVip Completed</b>\n"
            f"👤 UID: <code>{uid}</code>\n"
            f"🚀 Requests Sent: 3\n"
            f"✔️ Success: {success_count}",
            reply_to_message_id=message.message_id
        )
        
        update_user_activity(user_id)
        
    except Exception as e:
        if temp_message_id:
            delete_message(message.chat.id, temp_message_id)
            
        bot.send_message(
            message.chat.id,
            f"❌ <b>An error occurred:</b> {str(e)}",
            reply_to_message_id=message.message_id
        )
        
        log_action("SPAMVIP_COMMAND_ERROR", user_id, str(e))
@bot.message_handler(func=lambda message: is_command(message, '5') or is_command(message, '6'))
def handle_team_commands(message):
    if not should_respond(message):
        return silent_ignore(message)
        
    user_id = message.from_user.id
    temp_message_id = None
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, 
                "⚠️ <b>Please enter player_id</b>\n"
                "📝 <b>Example:</b> <code>/5 123456789</code>", 
                reply_to_message_id=message.message_id)
            return
            
        target_id = parts[1]
        
        if not ChEck_Commande(target_id):
            bot.send_message(message.chat.id, "❌ <b>user_id Invalid</b>", reply_to_message_id=message.message_id)
            return
        
        command = message.text.split()[0]
        team_type = "5" if "/5" in command else "6"
        
        temp_message_id = send_temp_message(message.chat.id, 
            f"⏳ <b>A team is being dispatched {team_type}...</b>\n"
            f"🎯 the goal: <code>{target_id}</code>",
            reply_to_message_id=message.message_id)
        
        clients_list = get_random_accounts(1)
        
        if not clients_list:
            if temp_message_id:
                delete_message(message.chat.id, temp_message_id)
            bot.send_message(message.chat.id, "❌ <b>No accounts are currently online.</b>", reply_to_message_id=message.message_id)
            return
            
        client = clients_list[0]
        
        if "/5" in command:
            success = execute_5x_command(client, target_id, user_id, 1)
        else:
            success = execute_6x_command(client, target_id, user_id, 1)
        
        if temp_message_id:
            delete_message(message.chat.id, temp_message_id)
        
        if success:
            bot.send_message(message.chat.id, 
                f"✅ <b>A team was sent {team_type} Successfully</b>\n"
                f"🎯 the goal: <code>{target_id}</code>", 
                reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, 
                f"❌ <b>Failed to send a team {team_type}</b>\n"
                f"🎯 the goal: <code>{target_id}</code>", 
                reply_to_message_id=message.message_id)
        
        update_user_activity(user_id)
        
    except Exception as e:
        if temp_message_id:
            delete_message(message.chat.id, temp_message_id)
        bot.send_message(message.chat.id, f"❌ <b>An error occurred:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("TEAM_COMMAND_ERROR", user_id, str(e))
# HeX MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'hex'))
def handle_hex_command(message):
    if not should_respond(message):
        return silent_ignore(message)
        
    user_id = message.from_user.id
    temp_message_id = None
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, 
                "⚠️ <b>Please enter player_id</b>\n"
                "📝 <b>Example:</b> <code>/hex 123456789</code>", 
                reply_to_message_id=message.message_id)
            return
            
        target_id = parts[1]
        
        if not ChEck_Commande(target_id):
            bot.send_message(message.chat.id, "❌ <b>player_id Invalid/b>", reply_to_message_id=message.message_id)
            return
        
        attempts_remaining = get_user_attempts(user_id, 'spam')
        
        if attempts_remaining <= 0 and not has_unlimited_attempts(user_id):
            bot.send_message(
                message.chat.id,
                (
                    "❌ <b>You have exhausted all your attempts!</b>\n"
                    "⏰ Please wait two hours to restore attempts.\n"
                    "💎 Get an activation code for unlimited attempts."
                ),
                reply_to_message_id=message.message_id
            )
            return
        
        if not use_attempt(user_id, 'spam') and not has_unlimited_attempts(user_id):
            bot.send_message(message.chat.id,( 
                "❌ <b>No attempts are available!</b>\n"
                "⏰ Please wait two hours for attempts to be restored."),
                reply_to_message_id=message.message_id)
            return
        
        with active_spam_lock:
            if target_id not in active_spam_targets:
                active_spam_targets[target_id] = True
                threading.Thread(target=infinite_spam_worker, args=(target_id,), daemon=True).start()
                
                if has_unlimited_attempts(user_id):
                    message_text = f"✅ <b>A 24-hour graveyard has been started on the user.</b>\n👤 player: <code>{target_id}</code>\n♾️ Unlimited attempts"
                else:
                    remaining_attempts = get_user_attempts(user_id, 'spam')
                    message_text = f"✅ <b>A 24-hour graveyard has been started on the user./b>\n👤 player: <code>{target_id}</code>\n🔄 <b>Remaining attempts:</b> {remaining_attempts}/3"  
            else:
                message_text = f"⚠️ <b>The graveyard is already working on the user.</b>"
                
        bot.send_message(message.chat.id, message_text, reply_to_message_id=message.message_id)
        update_user_activity(user_id)
        
    except Exception as e:
        if temp_message_id:
            delete_message(message.chat.id, temp_message_id)
        bot.send_message(message.chat.id, f"❌ <b>An error occurred:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("HEX_COMMAND_ERROR", user_id, str(e))
#StOp MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'stop'))
def handle_stop_command(message):
    if not should_respond(message):
        return silent_ignore(message)
        
    user_id = message.from_user.id
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, 
                "⚠️ <b>Please enter player_id</b>\n"
                "📝 <b>Example:</b> <code>/stop 123456789</code>", 
                reply_to_message_id=message.message_id)
            return
            
        target_id = parts[1]
        
        with active_spam_lock:
            if target_id in active_spam_targets:
                del active_spam_targets[target_id]
                message_text = f"🛑 <b>The cemetery has been disabled for the user.:</b> <code>{target_id}</code>"
            else:
                message_text = f"ℹ️ <b>There is no active graveyard for the user:</b> <code>{target_id}</code>"
                
        bot.send_message(message.chat.id, message_text, reply_to_message_id=message.message_id)
        update_user_activity(user_id)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>An error occurred:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("STOP_COMMAND_ERROR", user_id, str(e))

# UeSeRs LoGiN CoDe SeT
@bot.message_handler(func=lambda message: len(message.text) == 16 and message.text.isalnum() and message.text.isupper())
def handle_activation_codes(message):
    handle_activation_code(message)

# LoGiN MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'login'))
def handle_login_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return silent_ignore(message)
        
    try:
        parts = message.text.split()
        
        # التحقق من وجود عدد الأيام
        if len(parts) < 2:
            bot.send_message(message.chat.id, 
                "⚠️ <b>Please enter the number of days./b>\n"
                "📝 <b>Example:</b> <code>/login 30</code>\n",
                reply_to_message_id=message.message_id)
            return
        
        days = int(parts[1])
        
        if days <= 0:
            bot.send_message(message.chat.id, 
                "❌ <b>The number of days must be greater than the rowر!</b>\n"
                "📝 <b>A correct example:</b> <code>/login 30</code>", 
                reply_to_message_id=message.message_id)
            return
        
        # الحد الأقصى للأيام (اختياري)
        if days > 3650:  # 10 سنوات كحد أقصى
            bot.send_message(message.chat.id, 
                "❌ <b>The number of days is very large!</b>\n"
                "📝 <b>maximum:</b> 3650 day (10 years)", 
                reply_to_message_id=message.message_id)
            return
        
        code = generate_activation_code(days)
        expire_date = datetime.fromtimestamp(time.time() + (365 * 24 * 60 * 60)).strftime('%Y-%m-%d %H:%M:%S')
        
        response_text = f"""
✅ <b>The activation code was successfully generated.</b>

📝 <b>Code details:</b>
🔑 Code: <code>{code}</code>
⏰ Duration: {days} day
📅 The code ends in: {expire_date}

💡 <b>How to use:</b>
Send the code to the user to activate their account:
<code>{code}</code>
        """
        
        bot.send_message(message.chat.id, response_text, reply_to_message_id=message.message_id)
        log_action("LOGIN_CODE_GENERATED", user_id, f"Code: {code}, Days: {days}")
        update_user_activity(user_id)
        
    except ValueError:
        bot.send_message(message.chat.id, 
            "❌ <b>The entered value is incorrect!</b>\n"
            "📝 <b>Make sure:</b>\n"
            "• إEnter only integers\n"
            "• <b>A correct example:</b> <code>/login 30</code>\n"
            "• <b>Incorrect example:</b> <code>/login ثلاثين</code>", 
            reply_to_message_id=message.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, 
            f"❌ <b>An unexpected error occurred:</b> {str(e)}\n"
            f"📝 <b>Please try again</b>", 
            reply_to_message_id=message.message_id)
        log_action("LOGIN_COMMAND_ERROR", user_id, str(e))
# GrOuP MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'allow'))
def handle_allow_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return silent_ignore(message)
        
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, 
                "⚠️ <b>Please enter group_id</b>\n"
                "📝 <b>Example:</b> <code>/allow -100123456789</code>", 
                reply_to_message_id=message.message_id)
            return
            
        group_id = parts[1]
        
        if len(parts) < 3:
            days = 365
        else:
            days = int(parts[2])
        
        if days <= 0:
            bot.send_message(message.chat.id, "❌ <b>The number of days must be greater than zero!</b>", reply_to_message_id=message.message_id)
            return
        
        expire_time = add_allowed_group(group_id, days)
        expire_date = datetime.fromtimestamp(expire_time).strftime('%Y-%m-%d %H:%M:%S')
        
        response_text = f"""
✅ <b>The group has been successfully activated.</b>

📝 <b>Activation details:</b>
👥 The group: <code>{group_id}</code>
⏰ Duration: {days} day
📅 Expiry date: {expire_date}
        """
        
        bot.send_message(message.chat.id, response_text, reply_to_message_id=message.message_id)
        update_user_activity(user_id)
        
    except ValueError:
        bot.send_message(message.chat.id, 
            "❌ <b>The entered value is incorrect!</b>\n"
            "📝 Make sure you enter the correct numbers", 
            reply_to_message_id=message.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>An error occurred:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("ALLOW_COMMAND_ERROR", user_id, str(e))
# GrOuP MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'unallow'))
def handle_unallow_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return silent_ignore(message)
        
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, 
                "⚠️ <b>Please enter group_id</b>\n"
                "📝 <b>Example:</b> <code>/unallow -100123456789</code>", 
                reply_to_message_id=message.message_id)
            return
            
        group_id = parts[1]
        
        if remove_allowed_group(group_id):
            response_text = f"✅ <bThe group has been deactivated:</b> <code>{group_id}</code>"
        else:
            response_text = f"❌ <b>The group is not listed:</b> <code>{group_id}</code>"
        
        bot.send_message(message.chat.id, response_text, reply_to_message_id=message.message_id)
        update_user_activity(user_id)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>An error occurred:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("UNALLOW_COMMAND_ERROR", user_id, str(e))
# OwNeR MsG  SeT
@bot.message_handler(func=lambda message: is_command(message, 'addowner'))
def handle_addowner_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return silent_ignore(message)
        
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, 
                "⚠️ <b>Please enter user_id</b>\n"
                "📝 <b>Example:</b> <code>/addowner 123456789</code>", 
                reply_to_message_id=message.message_id)
            return

        new_owner_id = parts[1]
        if not new_owner_id.isdigit():
            bot.send_message(message.chat.id, "❌ <b>It should be user_id Number</b>", reply_to_message_id=message.message_id)
            return

        new_owner_id = int(new_owner_id)
        if is_owner(new_owner_id):
            bot.send_message(message.chat.id, f"❌ <b>user <code>{new_owner_id}</code> owner already</b>", reply_to_message_id=message.message_id)
            return

        add_owner(new_owner_id)
        bot.send_message(message.chat.id, f"✅ <b>The new owner has been added:</b> <code>{new_owner_id}</code>", reply_to_message_id=message.message_id)
        update_user_activity(user_id)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>An error occurred:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("ADDOWNER_COMMAND_ERROR", user_id, str(e))
# OwNeR MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'removeowner'))
def handle_removeowner_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return silent_ignore(message)
        
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, 
                "⚠️ <b>Please enter user_id</b>\n"
                "📝 <b>Example:</b> <code>/removeowner 123456789</code>", 
                reply_to_message_id=message.message_id)
            return

        owner_id_to_remove = parts[1]
        if not owner_id_to_remove.isdigit():
            bot.send_message(message.chat.id, "❌ <b>It should be user_id Number</b>", reply_to_message_id=message.message_id)
            return

        owner_id_to_remove = int(owner_id_to_remove)
        if not is_owner(owner_id_to_remove):
            bot.send_message(message.chat.id, f"❌ <b>user <code>{owner_id_to_remove}</code> Not an owner</b>", reply_to_message_id=message.message_id)
            return

        if owner_id_to_remove == user_id:
            bot.send_message(message.chat.id, "❌ <b>You cannot remove yourself</b>", reply_to_message_id=message.message_id)
            return

        remove_owner(owner_id_to_remove)
        bot.send_message(message.chat.id, f"✅ <b>Owner removed:</b> <code>{owner_id_to_remove}</code>", reply_to_message_id=message.message_id)
        update_user_activity(user_id)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>حدث خطأ:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("REMOVEOWNER_COMMAND_ERROR", user_id, str(e))
# StAtUs BoT iNfO MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'status'))
def handle_status_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return silent_ignore(message)
        
    try:
        with active_spam_lock:
            active_targets = list(active_spam_targets.keys())
            
        with connected_clients_lock:
            accounts_count = len(connected_clients)
            accounts_list = list(connected_clients.keys())
        
        users = load_data(USERS_FILE)
        total_users = len(users)
        active_users = sum(1 for user_data in users.values() 
                          if datetime.now().timestamp() - datetime.strptime(user_data.get('last_active', '2000-01-01 00:00:00'), '%Y-%m-%d %H:%M:%S').timestamp() < 24 * 60 * 60)
        
        activations = load_data(ACTIVATIONS_FILE)
        active_activations = sum(1 for activation in activations.values() 
                                if activation.get('expire_at', 0) > time.time())
        
        allowed_groups = load_allowed_groups()
        active_groups = sum(1 for group_data in allowed_groups.values() 
                           if group_data.get('expire_at', 0) > time.time())
        
        owners = load_owners()
        status_text = f"""
📊 <b>Bot status MERO KInG</b>

<b>👥 User statistics:</b>
👤 Total users: {total_users}
🟢 Active users: {active_users}
💎 Active activations: {active_activations}
👑 Number of owners: {len(owners)}

<b>🎯 Active goals:</b> {len(active_targets)}
🔸 {', '.join(active_targets) if active_targets else 'No active targets'}

<b>👥 Connected accounts:</b> {accounts_count}
🔸 {', '.join(accounts_list[:10]) if accounts_list else 'No accounts connected'}

<b>👥 Allowed groups:</b> {active_groups}
        """
        
        bot.send_message(message.chat.id, status_text, reply_to_message_id=message.message_id)
        update_user_activity(user_id)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>An error occurred:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("STATUS_COMMAND_ERROR", user_id, str(e))
#AcCs StAtUs MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'accounts'))
def handle_accounts_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return silent_ignore(message)
        
    try:
        with connected_clients_lock:
            accounts_count = len(connected_clients)
            accounts_list = list(connected_clients.keys())
            
        accounts_text = f"👥 <b>Connected accounts:</b> {accounts_count}\n\n"
        accounts_text += "<b>List of accounts:</b>"
        for i, account in enumerate(accounts_list, 1):
            accounts_text += f"\n🔹 {i}. <code>{account}</code>"
            
        bot.send_message(message.chat.id, accounts_text, reply_to_message_id=message.message_id)
        update_user_activity(user_id)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>An error occurred:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("ACCOUNTS_COMMAND_ERROR", user_id, str(e))

# OwNeRs StAtuS MsG SeT
@bot.message_handler(func=lambda message: is_command(message, 'listowners'))
def handle_listowners_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return silent_ignore(message)
        
    try:
        owners = load_owners()
        owners_text = "<b>👑 List of owners:</b>\n\n"
        for i, (owner_id, owner_data) in enumerate(owners.items(), 1):
            try:
                user_info = bot.get_chat(int(owner_id))
                username = f"@{user_info.username}" if user_info.username else user_info.first_name
                added_at = owner_data.get('added_at', 'unknown')
                owners_text += f"{i}. {username} - <code>{owner_id}</code>\n   ⏰ Added in: {added_at}\n"
            except Exception as e:
                owners_text += f"{i}. unknown - <code>{owner_id}</code>\n   ⏰ Added in: {owner_data.get('added_at', 'unknown')}\n"
                log_action("FETCH_OWNER_INFO_ERROR", user_id, f"Owner: {owner_id} | Error: {str(e)}")

        owners_text += f"\n<b>Total:</b> {len(owners)} What is with you"
        
        bot.send_message(message.chat.id, owners_text, reply_to_message_id=message.message_id)
        update_user_activity(user_id)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>An error occurred:</b> {str(e)}", reply_to_message_id=message.message_id)
        log_action("LISTOWNERS_COMMAND_ERROR", user_id, str(e))

#MsG SeT
@bot.message_handler(func=lambda message: True)
def handle_all_other_messages(message):
    silent_ignore(message)
# FiLeS DaTa
def initialize_data_files():
    
    files_to_initialize = [
        USERS_FILE,
        ACTIVATIONS_FILE, 
        ACTIVATION_CODES_FILE,
        ALLOWED_GROUPS_FILE,
        OWNERS_FILE
    ]
    
    for filename in files_to_initialize:
        if not os.path.exists(filename):
            print(f"📁 Create a file: {filename}")
            save_data({}, filename)
        else:
            data = load_data(filename)
            print(f"✅ Loaded {filename}: {len(data)} component")
    
    restored = restore_expired_attempts()
    print(f"🔄 Attempts were restored {restored} User at start")
    

    owners = load_owners()
    if not owners:
        for owner_id in ADMIN_USER_IDS:
            owners[str(owner_id)] = {
                "added_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "added_by": "system"
            }
        save_owners(owners)
        print(f"✅ Default owners have been added: {ADMIN_USER_IDS}")
# TeLe BoT
def start_telegram_bot():
    print("🚀 Starting the Telegram bot...")
    try:
        bot_info = bot.get_me()
        print(f"🤖 Bot name: {bot_info.username}")
        print(f"🆔 Bot ID: {bot_info.id}")
        print("✅ The Telegram bot is working successfully!")
        
        allowed_groups = load_allowed_groups()
        print(f"👥 Number of groups allowed: {len(allowed_groups)}")
        for group_id, group_data in allowed_groups.items():
            expire_date = group_data.get('expire_date', 'unknown')
            print(f"   - {group_id} (It ends: {expire_date})")
            
        return True
    except Exception as e:
        print(f"❌ Error running the Telegram bot: {e}")
        return False
# AcCs
def start_accounts():
    print("⏳ Account activation is underway....")
    
    if not ACCOUNTS:
        print("❌ No accounts to start!")
        return
    
    accounts_to_start = ACCOUNTS[:99999999999]
    print(f"🔧 It will be turned on {len(accounts_to_start)} account of origin {len(ACCOUNTS)}")
    
    for i, account in enumerate(accounts_to_start, 1):
        try:
            print(f"🚀 Start account {i}: {account['id']}")
            threading.Thread(target=start_account, args=(account,), daemon=True).start()
            time.sleep(0.1)  # تأخير بين تشغيل كل حساب
        except Exception as e:
            print(f"❌ Account start error {account['id']}: {e}")
# xMeRo KiNgx
def StarT_SerVer():
    initialize_data_files()

    if not start_telegram_bot():
        print("❌ Telegram bot failed to launch, please try again....")
        time.sleep(5)
        return StarT_SerVer()

    start_accounts()

    threading.Thread(target=background_tasks, daemon=True).start()
    threading.Thread(target=AuTo_ResTartinG, daemon=True).start()
    
    print(f"✅ The system has been fully started and operated successfully.")
    print(f"🕒 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👑 Number of owners: {len(load_owners())}")
    print(f"📊 Number of uploaded accounts: {len(ACCOUNTS)}")
    print(f"🔧 Number of active accounts: {min(5, len(ACCOUNTS))}")
    
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"❌ Error in the Telegram bot: {e}")
        print("🔄 Restart the system...")
        time.sleep(5)
        ResTarT_BoT()

if __name__ == "__main__":
    StarT_SerVer()