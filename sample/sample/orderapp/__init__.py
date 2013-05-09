from rbkmoney.signals import result_received

def on_result_received(sender, **kwargs):
    if sender.paymentStatus == 5:
        print 'OK'
    elif sender.paymentStatus == 3:
        print 'WAIT'

result_received.connect(on_result_received)