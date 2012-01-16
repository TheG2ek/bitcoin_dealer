import sys, os, time, datetime
import urllib2
from django.core.management import setup_environ
from django import db
from decimal import *

sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../bitcoin_dealer'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'bitcoin_dealer.settings'

from bitcoin_dealer.exchange.exchange.mtgox import MtGox
from bitcoin_dealer.exchange.models import Trade, TradeLog
import bitcoin_dealer.settings as settings

def console_log(message):
    now = datetime.datetime.now()
    print "%s - %s" % (now.strftime("%Y-%m-%d %H:%M:%S"), message)

def trade(trades, last_price):
    if not 'ticker' in last_price: return
    if not 'last' in last_price['ticker']: return

    for trade in trades:
        try:
            # we are BUYING, when last price is higher or equal to watch price (lp_higher == True) and there is no related "sell" order
            if trade.active == True and trade.lp_higher == True and trade.buy_or_sell == True and trade.related is None:
                if Decimal(last_price['ticker']['last']) >= Decimal(trade.watch_price):
                    trade.active = False
                    trade.status = "buying"
                    trade.save()

                    response = mtgox.buy(str(Decimal(trade.price)), str(Decimal(trade.amount)))

                    trade_log = TradeLog(trade=trade, log="buying", log_desc="Buying %s." % (trade.pk))
                    trade_log.save()

                    if settings.bd_debug == True:
                        console_log("buying, when last price (%s) is higher or equal than watch price (%s) and there is no related sell order (buying at price: %s, amount: %s)" % (last_price['ticker']['last'], trade.watch_price, trade.price, trade.amount))
                        # console_log(str(response))

            # we are BUYING, when last price is lower or equal to watch price (lp_higher == False) and there is no related "sell" order
            elif trade.active == True and trade.lp_higher == False and trade.buy_or_sell == True and trade.related is None:
                if Decimal(last_price['ticker']['last']) <= Decimal(trade.watch_price):
                    trade.active = False
                    trade.status = "buying"
                    trade.save()

                    response = mtgox.buy(str(Decimal(trade.price)), str(Decimal(trade.amount)))

                    trade_log = TradeLog(trade=trade, log="buying", log_desc="Buying %s." % (trade.pk))
                    trade_log.save()

                    if settings.bd_debug == True:
                        console_log("buying, when last price (%s) is lower or equal that watch price (%s) and there is no related sell order (buying at price: %s, amount: %s)" % (last_price['ticker']['last'], trade.watch_price, trade.price, trade.amount))
                        # console_log(str(response))

            # we are BUYING, when last price is higher or equal to watch price (lp_higher == True) and related "sell" order has been fully "sold"
            elif trade.active == True and trade.lp_higher == True and trade.buy_or_sell == True and trade.related is not None:
                if trade.related.status == "sold" and trade.status == "waiting":
                    if Decimal(last_price['ticker']['last']) >= Decimal(trade.watch_price):
                        trade.active = False
                        trade.status = "buying"
                        trade.save()

                        response = mtgox.buy(str(Decimal(trade.price)), str(Decimal(trade.amount)))

                        trade_log = TradeLog(trade=trade, log="buying", log_desc="Buying %s (related %s sold)." % (trade.pk, trade.related.pk))
                        trade_log.save()

                        if settings.bd_debug == True:
                            console_log("buying, when last price (%s) is higher or equal to watch price (%s) and related sell order was sold (buying at price: %s, amount: %s, related: %s)" % (last_price['ticker']['last'], trade.watch_price, trade.price, trade.amount, trade.related.pk))
                            # console_log(str(response))

            # we are BUYING, when last price is lower or equal to watch price (lp_hihger == False) and related "sell" order has been fully "sold"
            elif trade.active == True and trade.lp_higher == False and trade.buy_or_sell == True and trade.related is not None:
                if trade.related.status == "sold" and trade.status == "waiting":
                    if Decimal(last_price['ticker']['last']) <= Decimal(trade.watch_price):
                        trade.active = False
                        trade.status = "buying"
                        trade.save()

                        response = mtgox.buy(str(Decimal(trade.price)), str(Decimal(trade.amount)))

                        trade_log = TradeLog(trade=trade, log="buying", log_desc="Buying %s (related %s sold)." % (trade.pk, trade.related.pk))
                        trade_log.save()

                        if settings.bd_debug == True:
                            console_log("buying, when last price (%s) is lower or equal to watch price (%s) and related sell order was sold (buying at price: %s, amount: %s, related: %s)" % (last_price['ticker']['last'], trade.watch_price, trade.price, trade.amount, trade.related.pk))
                            # console_log(str(response))

            # we are SELLING, when last price is higher or equal to watch price (lp_higher == True) and there is no related "buy" order
            elif trade.active == True and trade.lp_higher == True and trade.buy_or_sell == False and trade.related is None:
                if Decimal(last_price['ticker']['last']) >= Decimal(trade.watch_price):
                    trade.active = False
                    trade.status = "selling"
                    trade.save()

                    response = mtgox.sell(str(Decimal(trade.price)), str(Decimal(trade.amount)))

                    trade_log = TradeLog(trade=trade, log="selling", log_desc="Selling %s." % (trade.pk))
                    trade_log.save()

                    if settings.bd_debug == True:
                        console_log("selling, when last price (%s) is higher or equal to watch price (%s) and there is no related buy order (selling at price: %s, amount: %s)" % (last_price['ticker']['last'], trade.watch_price, trade.price, trade.amount))
                        # console_log(str(response))

            # we are SELLING, when last price is lower or equal to watch price (lp_higher == False) and there is no related "buy" order
            elif trade.active == True and trade.lp_higher == False and trade.buy_or_sell == False and trade.related is None:
                if Decimal(last_price['ticker']['last']) <= Decimal(trade.watch_price):
                    trade.active = False
                    trade.status = "selling"
                    trade.save()

                    response = mtgox.sell(str(Decimal(trade.price)), str(Decimal(trade.amount)))

                    trade_log = TradeLog(trade=trade, log="selling", log_desc="Selling %s." % (trade.pk))
                    trade_log.save()

                    if settings.bd_debug == True:
                        console_log("selling, when last price (%s) is lower or equal to watch price (%s) and there is no related buy order (selling at price: %s, amount: %s)" % (last_price['ticker']['last'], trade.watch_price, trade.price, trade.amount))
                        # console_log(str(response))

            # we are SELLING, when last price is higher or equal to watch price (lp_higher == True) and related "buy" order has been fully "bought"
            elif trade.active == True and trade.lp_higher == True and trade.buy_or_sell == False and trade.related is not None:
                if trade.related.status == "bought" and trade.status == "waiting":
                    if Decimal(last_price['ticker']['last']) >= Decimal(trade.watch_price):
                        trade.active = False
                        trade.status = "selling"
                        trade.save()

                        response = mtgox.sell(str(Decimal(trade.price)), str(Decimal(trade.amount)))

                        trade_log = TradeLog(trade=trade, log="selling", log_desc="Selling %s (related %s bought)." % (trade.pk, trade.related.pk))
                        trade_log.save()

                        if settings.bd_debug == True:
                            console_log("selling, when last price (%s) is higher or equal to watch price (%s) and related buy was bought (selling at price: %s, amount: %s, related: %s)" % (last_price['ticker']['last'], trade.watch_price, trade.price, trade.amount, trade.related.pk))
                            # console_log(str(response))

            # we are SELLING, when last price is lower or equal to watch price and related "buy" order has been fully "bought"
            elif trade.active == True and trade.lp_higher == False and trade.buy_or_sell == False and trade.related is not None:
                if trade.related.status == "bought" and trade.status == "waiting":
                    if Decimal(last_price['ticker']['last']) <= Decimal(trade.watch_price):
                        trade.active = False
                        trade.status = "selling"
                        trade.save()

                        response = mtgox.sell(str(Decimal(trade.price)), str(Decimal(trade.amount)))

                        trade_log = TradeLog(trade=trade, log="selling", log_desc="Selling %s (related %s bought)." % (trade.pk, trade.related.pk))
                        trade_log.save()

                        if settings.bd_debug == True:
                            console_log("selling, when last price (%s) is lower or equal to watch price (%s) and related buy was bought (selling at price: %s, amount: %s, related: %s)" % (last_price['ticker']['last'], trade.watch_price, trade.price, trade.amount, trade.related.pk))
                            # console_log(str(response))
        except:
            raise
"""
id: Order ID
type: 1 for sell order or 2 for buy order
status: 1 for active, 2 for not enough funds
"""
def check_status(trades, orders):
    for trade in trades:
        found = None
        for order in orders:
            if Decimal(trade.price) == Decimal(order["price"]):
                found = order
                break
        if found is not None:
            if trade.status == "selling" and found["type"] == "1" and found["status"] == "2":
                trade.status = "not enough funds"
                trade.save()

                trade_log = TradeLog(trade=trade, log="not enough funds", log_desc="Not enough funds for trade %s." % (trade.pk))
                trade_log.save()
                if (settings.bd_debug == True):
					console_log("not enoguh funds for selling...")
            if trade.status == "buying" and found["type"] == "2" and found["status"] == "2":
                trade.status = "not enough funds"
                trade.save()

                trade_log = TradeLog(trade=trade, log="not enough funds", log_desc="Not enough funds for trade %s." % (trade.pk))
                trade_log.save()
                if (settings.bd_debug == True):
					console_log("not enoguh funds for buying...")
        else:
            if trade.status == "selling":
                trade.status = "sold"
                trade.save()

                trade_log = TradeLog(trade=trade, log="sold", log_desc="Sold trade %s." % (trade.pk))
                trade_log.save()
                if (settings.bd_debug == True):
				    console_log("sold %s bitcoins for %s dollars" % (trade.amount, trade.price))
            elif trade.status == "buying":
                trade.status = "bought"
                trade.save()

                trade_log = TradeLog(trade=trade, log="bought", log_desc="Bought trade %s." % (trade.pk))
                trade_log.save()
                if (settings.bd_debug == True):
					console_log("bought %s bitcoins for %s dollars" % (trade.amount, trade.price))

def check_price():
    if (('ticker' in result) and ('last' in result['ticker'])):
        last_price = result['ticker']['last']
        check_orders(result[last_price])
    
mtgox = MtGox({"username": settings.mtgox_username, "password": settings.mtgox_password, "key": settings.mtgox_key, "secret": settings.mtgox_secret, "currency": settings.mtgox_currency})

while True:
    time.sleep(settings.check_interval)
    try:
        my_trades = Trade.objects.filter(active=True)
        if (settings.bd_debug == True):
            # print my_trades
            pass

        price = mtgox.get_price()
        if (settings.bd_debug == True):
            # print price
            pass

        trade(my_trades, price)
        all_my_trades = Trade.objects.all()
        my_orders = mtgox.get_orders()
        if all_my_trades is not None and len(all_my_trades) > 0 and my_orders is not None and "orders" in my_orders:
            check_status(all_my_trades, my_orders["orders"])
            if (settings.bd_debug == True):
	            console_log("just checked statuses of orders...")

        if (settings.bd_debug == True):
            console_log("sleeping %d seconds..." % settings.check_interval)

    except urllib2.URLError as err:
        console_log("could not connect to some url: %s" % (err))
        pass
    except ValueError as (err):
        # got this error once
        console_log("No JSON object could be decoded ???: %s " % (err))
        pass 
    except:
        raise
    
    db.reset_queries()