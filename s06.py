import asyncio
import pymysql
from db import select_client
from db import add_client
from db import remove_client
from db import get_updates
from db import get_updates_trade
from db import get_updates_param
from db import command_complete
from db import command_status_update
from db import command_param_update
from db import get_params
from db import command_order_update
from db import clean_trades
from datetime import datetime


async def clean_clients(ip, cursor):
    global clients
    client = (ip.split(':')[0], int(ip.split(':')[1]))
    #print(client, clients)
    if not client in clients:
        try:
            await remove_client(ip, cursor)
            return 1
        except:
            return None
    return None


async def handle_echo(reader, writer):
    start_time = datetime.now()
    #param_updates = ['broker_mode', 'risk', 'volatility', 'tp', 'sl', 'time_protect', 'a', 'b', 'c']
    client_id = ''
    modes = ''
    check_time = ''
    auth = None
    global command
    global clients
    while True:
        client = writer.get_extra_info('peername')
        if not client in clients:
            clients.append(client)
            check_time = datetime.fromtimestamp(datetime.now().timestamp() + 60 * 10 * 1)
            db = pymysql.connect("db", "lic", "6M9j9P4q", "lic", charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor,autocommit=True)
            cursor = db.cursor()
            
        try:
            data = await reader.readline()
        except:
            #rint("Close the connection" + str(client))
            clients.pop(clients.index(client))
            await asyncio.sleep(5)
            writer.close()
            try:
                await remove_client(ip, cursor)
                db.close()
            except:
                break
            break
        try:
            message = data.decode()
        except:
            message = ""
        
        if datetime.now() > check_time:
            #print ("Check license")
            message = "exit"
            
        #if len(message.split()) > 0:
            #print (str(client)+": "+str(message.split()))

        ip = str(client[0]) + ":" + str(client[1])
        
        if not auth is None and "authaccept" in auth:
            if ip in command:
                db.ping()
                try:
                    if command[ip]['trade'] is not None:
                        msg = command[ip]['trade'] + "\r\n"
                        msg += 'broker_mode:'+str(command[ip]['broker_mode'])+ "\r\n"
                        msg += 'risk:'+str(command[ip]['risk'])+ "\r\n"
                        msg += 'volatility:'+str(command[ip]['volatility'])+ "\r\n"
                        msg += 'tp:'+str(command[ip]['tp'])+ "\r\n"
                        msg += 'sl:'+str(command[ip]['sl'])+ "\r\n"
                        msg += 'time_protect:'+str(command[ip]['time_protect'])+ "\r\n"
                        msg += 'a:'+str(command[ip]['a'])+ "\r\n"
                        msg += 'b:'+str(command[ip]['b'])+ "\r\n"
                        msg += 'c:'+str(command[ip]['c'])+ "\r\n"
                        
                        
                        try:
                            writer.write(msg.encode())
                            await writer.drain()
                        except:
                            #print("Close the connection" + str(client))
                            clients.pop(clients.index(client))
                            await asyncio.sleep(5)
                            writer.close()
                            try:
                                await remove_client(ip, cursor)
                                db.close()
                            except:
                                break
                            break
                        
                        
                    else:
                        print("param command "+str(client))
                        msg = 'broker_mode:'+str(command[ip]['broker_mode'])+ "\r\n"
                        msg += 'risk:'+str(command[ip]['risk'])+ "\r\n"
                        msg += 'volatility:'+str(command[ip]['volatility'])+ "\r\n"
                        msg += 'tp:'+str(command[ip]['tp'])+ "\r\n"
                        msg += 'sl:'+str(command[ip]['sl'])+ "\r\n"
                        msg += 'time_protect:'+str(command[ip]['time_protect'])+ "\r\n"
                        msg += 'a:'+str(command[ip]['a'])+ "\r\n"
                        msg += 'b:'+str(command[ip]['b'])+ "\r\n"
                        msg += 'c:'+str(command[ip]['c'])+ "\r\n"
                        
                        try:
                            writer.write(msg.encode())
                            await writer.drain()
                        except:
                            #print("Close the connection" + str(client))
                            clients.pop(clients.index(client))
                            await asyncio.sleep(5)
                            await writer.close()
                            try:
                                remove_client(ip, cursor)
                                db.close()
                            except:
                                break
                            break
                            
                        
                    await command_complete(ip, cursor)
                    command.pop(ip)
                except:
                    pass
        
        if 'order' in message:
            db.ping()
            await command_order_update(client_id, message, ip, cursor)
            
        if 'update' in message:
            db.ping()
            if len(message.split(":")) > 2:
                await command_param_update(ip, message, cursor)
            else:
                await command_status_update(ip, message, cursor)

        if 'exit' in message:
            db.ping()
            #print("Close the connection" + str(client))
            clients.pop(clients.index(client))
            await asyncio.sleep(5)
            writer.close()
            try:
                await remove_client(ip, cursor)
                db.close()
            except:
                break
            break

        if 'auth' in message and not auth:
            db.ping()
            client_id = message.split(":")[1]
            
            try:
                ver = message.split(":")[5]
            except:
                ver = None
            if ver is not None and "2.0.0" in ver:
                ver = "ok"
            else:
                ver = None
                
            dbid = await select_client(client_id, cursor)
            print (str(dbid))
            if (dbid and ver and dbid['valid'] > datetime.now()):
                #print("New connection: "+ip)
                broker = message.split(":")[3]
                mode = message.split(":")[2]
                auth = 'authaccept\r\n'
                data = await get_params(broker, mode, cursor)
                await clean_trades(client_id, cursor)
                if data is not None:
                    auth += 'broker_mode:'+str(data['broker_mode'])+'\r\n'
                    auth += 'risk:'+str(data['risk'])+'\r\n'
                    auth += 'volatility:'+str(data['volatility'])+'\r\n'
                    auth += 'tp:'+str(data['tp'])+'\r\n'
                    auth += 'sl:'+str(data['sl'])+'\r\n'
                    auth += 'time_protect:'+str(data['time_protect'])+'\r\n'
                    auth += 'a:'+str(data['a'])+'\r\n'
                    auth += 'b:'+str(data['b'])+'\r\n'
                    auth += 'c:'+str(data['c'])+'\r\n'
                    auth += 'valid:'+str(dbid['valid'].strftime("%d-%m-%Y"))+'\r\n'
                    #print (str(dbid['valid'].strftime("%d.%m.%Y")))
                
                try:
                    writer.write(auth.encode())
                    await writer.drain()
                except:
                    #print("Close the connection" + str(client))
                    clients.pop(clients.index(client))
                    await asyncio.sleep(5)
                    writer.close()
                    try:
                        await remove_client(ip, cursor)
                        db.close()
                    except:
                        break
                    break
                try:
                    await add_client(client_id, ip, broker, mode, cursor)
                except:
                    print("ERROR", client_id, ip, broker, mode)
                    clients.pop(clients.index(client))
                    await asyncio.sleep(5)
                    writer.close()
                    try:
                        await remove_client(ip, cursor)
                        db.close()
                    except:
                        break
                    break
            else:
                #print("Close the connection" + str(client))
                auth = "authlic\r\n"
                try:
                    dbid
                except:
                    if dbid['valid'] < datetime.now():
                        auth = "authlic\r\n"
                    
                if ver is None:
                    auth = "authver\r\n"
                #print(str(auth))
                writer.write(auth.encode())
                await writer.drain()
                #print (auth)
                clients.pop(clients.index(client))
                await asyncio.sleep(300)
                writer.close()
                try:
                    await remove_client(ip, cursor)
                    db.close()
                except:
                    break
                break
        
        try:
            writer.write("\r\n".encode())
            await writer.drain()
        except:
            #print("Close the connection" + str(client))
            clients.pop(clients.index(client))
            await asyncio.sleep(5)
            writer.close()
            try:
                await remove_client(ip, cursor)
                db.close()
            except:
                break
            break



async def commands():
    db = pymysql.connect("db", "lic", "6M9j9P4q", "lic", charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor,autocommit=True)
    db.ping()
    cursor = db.cursor()
    global command
    while True:
        upd = await get_updates(cursor)
        while len(upd) > 0:
            if upd is not None:
                if not await clean_clients(upd[0]['ip'], cursor):
                    if upd[0]['apply']:
                        #print("UPD " + str(len(upd)))
                        command[upd[0]['ip']] = upd[0]
                upd.pop(0)
        #print(command)
        await get_updates_trade(cursor)
        await get_updates_param(cursor)
        await asyncio.sleep(0.4)


async def start():
    server = await asyncio.start_server(
        handle_echo, '0.0.0.0', 9999)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


async def main():
    await asyncio.gather(start(), commands())


command = {}
clients = []
asyncio.run(main())
asyncio.create_task(commands())
