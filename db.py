import pymysql
import string
import aiomysql


updates = 0
    
    
async def add_client(client, ip, broker, mode, cursor):
    Broker = {'1': 'FOREX4YOU', '2': 'ROBOFOREX'}
    Mode = {'2': 'UltraConservative', '6': 'Conservative', '12': 'Normal', '18': 'Agressive', '20': 'User'}
    query = "INSERT INTO `control` (`client_id`, `ip`, `broker_id`, `mode`) VALUES ({},'{}','{}','{}')".format(client, ip, Broker[broker.strip()], Mode[mode.strip()])
    cursor.execute(query)
    # cursor.commit()
    try:
        data = len(cursor.fetchone())
        return data
    except:
        return 0


async def get_updates(cursor):
    query = "SELECT * FROM `control` WHERE `client_id` IS NOT NULL"
    cursor.execute(query)
    return cursor.fetchall()
    
    
async def get_updates_trade(cursor):
    query = "SELECT * FROM `control` WHERE `client_id` IS NULL AND `apply` = 'run' AND `trade` IS NOT NULL"
    cursor.execute(query)
    upd = cursor.fetchall()
    while len(upd) > 0:
            if upd is not None:
                #print (upd)
                if 'ULTRA' in upd[0]['mode']:
                    query = "UPDATE `control` SET `apply` = '{}', `trade` = '{}' WHERE `client_id` IS NOT NULL AND `broker_id` = '{}'".format(upd[0]['apply'], upd[0]['trade'], upd[0]['broker_id'])
                else:
                    query = "UPDATE `control` SET `apply` = '{}', `trade` = '{}' WHERE `broker_id` = '{}' and `mode` = '{}'".format(upd[0]['apply'], upd[0]['trade'], upd[0]['broker_id'], upd[0]['mode'])
                #print (query)
                cursor.execute(query)
                query = "UPDATE `control` SET `apply` = NULL, `trade` = NULL WHERE `id` = '{}'".format(upd[0]['id'])
                cursor.execute(query)
                upd.pop(0)
                
                
async def get_updates_param(cursor):
    query = "SELECT * FROM `control` WHERE `client_id` IS NULL AND `apply` = 'run' AND `trade` IS NULL"
    cursor.execute(query)
    upd = cursor.fetchall()
    while len(upd) > 0:
            if upd is not None:
                Mode = {'UltraConservative':1, 'Conservative':3, 'Normal':6, 'Agressive':9}
                if 'ULTRA' in upd[0]['mode']:
                    query = """UPDATE `control` SET `apply` = 'run', `broker_mode` = '{}', `risk` = '{}', `tp` = '{}', `sl` = '{}', `time_protect` = '{}', `a` = '{}', `b` = '{}', `c` = '{}' WHERE `client_id` IS NULL AND `mode` <> 'ULTRA' AND `broker_id` = '{}' """.format(upd[0]['broker_mode'],upd[0]['risk'], upd[0]['tp'], upd[0]['sl'], upd[0]['time_protect'], upd[0]['a'], upd[0]['b'], upd[0]['c'],upd[0]['broker_id'])
                else:
                    query = """UPDATE `control` SET `apply` = 'run', `broker_mode` = '{}', `risk` = '{}', `tp` = '{}', `sl` = '{}', `time_protect` = '{}', `a` = '{}', `b` = '{}', `c` = '{}' WHERE `broker_id` = '{}' and `mode` = '{}'""".format(upd[0]['broker_mode'],upd[0]['risk']*Mode[upd[0]['mode']],upd[0]['tp'],upd[0]['sl'],upd[0]['time_protect'],upd[0]['a'],upd[0]['b'],upd[0]['c'],upd[0]['broker_id'],upd[0]['mode'])
                #print (query)
                cursor.execute(query)
                query = "UPDATE `control` SET `apply` = NULL, `trade` = NULL WHERE `id` = '{}'".format(upd[0]['id'])
                res = cursor.execute(query)
                upd.pop(0)


async def get_params(broker, mode, cursor):
    Broker = {'1': 'FOREX4YOU', '2': 'ROBOFOREX'}
    Mode = {'2': 'UltraConservative', '6': 'Conservative', '12': 'Normal', '18': 'Agressive', '20': 'User'}
    query = "SELECT * FROM `control` WHERE `broker_id` = '{}' and `mode` = '{}' and `client_id` IS NULL".format(Broker[broker.strip()], Mode[mode.strip()])
    cursor.execute(query)
    # cursor.commit()
    try:
        data = cursor.fetchone()
        return data
    except:
        return None


async def remove_client(ip, cursor):
    query = "DELETE FROM `control` WHERE `ip` = '{}'".format(ip)
    cursor.execute(query)

    query = "UPDATE `trades` SET `client_status` = 'offline', `ip` = '' WHERE `ip` = '{}'".format(ip)
    cursor.execute(query)



async def command_complete(ip, cursor):
    query = "UPDATE `control` SET `apply` = NULL, `trade` = NULL WHERE `ip` = '{}'".format(ip)
    cursor.execute(query)


async def command_param_update(ip, command, cursor):
    data = command.split(":")
    query = "UPDATE `control` SET `{}` = '{}' WHERE `ip` = '{}'".format(data[1], data[2].strip(), ip)
    cursor.execute(query)

    

async def clean_trades(client, cursor):
    query = "DELETE FROM `trades` WHERE `client` = '{}'".format(client)
    cursor.execute(query)


async def command_order_update(client, command, ip, cursor):
    OrderType = {"1":"sell","0":"buy","2":"buy_limit","3":"sell_limit","4":"buy_stop","5":"sell_stop","6":"closed"}
    data = command.split("#")
    order_type = OrderType[data[1]]
    print (str(client)+" "+order_type)
    magic = data[2]
    ticket = data[3]
    lots = data[4]
    open_price = data[5]
    open_time = data[6]
    symbol = data[7]
    #is_init = data[8]
    
    query = "SELECT id FROM `trades` WHERE `order_id` = '{}' and `client` = '{}'".format(ticket, client)
    cursor.execute(query)
    
    if (len(cursor.fetchall()) < 1):
        query = """INSERT INTO `trades` (`ip`, `client`, `client_status`, `symbol`, `type`, `open_price`, `open_time`, `order_id`, `magic`, `lots`) 
                            VALUES ('{}', '{}', 'online', '{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(ip, client, symbol, order_type, open_price, open_time, ticket, magic, lots)
    else:
        query = """UPDATE `trades` SET `type` = '{}', `ip` = '{}', `client_status` = 'online', `lots` = '{}' WHERE `order_id` ='{}' and `client` = '{}'""".format(order_type, ip, lots, ticket, client)
    cursor.execute(query)
    
    
async def command_status_update(ip, command, cursor):
    status = ''
    if 'long' in command:
        status = "= 'long'"
    if 'short' in command:
        status = "= 'short'"
    if 'closed' in command:
        status = "= NULL"
    query = "UPDATE `control` SET `status` {} WHERE `ip` = '{}'".format(status, ip)
    cursor.execute(query)


def main():
    global db
    print(select_client('5037369'))
    db.close()


async def select_client(client, cursor):
    query = "SELECT SQL_NO_CACHE id,valid FROM `users` WHERE `client` = '{}'".format(client)
    cursor.execute(query)
    try:
        data = cursor.fetchone()
        return data
    except:
        return None


if __name__ == '__main__':
    main()