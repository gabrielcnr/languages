import theano
from theano import tensor as T

def power_of_2(previous_power, max_value):
    return previous_power*2, theano.scan_module.until(previous_power*2 > max_value)

max_value = T.scalar()
values, _ = theano.scan(power_of_2,
                        outputs_info=T.constant(1.),
                        non_sequences=max_value,
                        n_steps=1024)

f = theano.function([max_value], values)

print(f(45))
