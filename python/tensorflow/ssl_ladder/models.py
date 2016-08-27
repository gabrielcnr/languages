import tensorflow as tf
import numpy as np

class SSLLadder(object):
    """
    Attributes
    ---------------
    x: tf.placeholder
    y: tf.placeholder
    phase_train: tf.placeholder of bool used in BN
    pred: pred op
    corrupted_encoder:
    clean_encoder: 
    decoder: 
    loss: loss op, or objective function op
    accuracy: accuracy op
    """

    def __init__(self, x_l, y, x_u, L, n_cls, phase_train):
        """
        Parameters
        -----------------
        x_l: tf.placeholder of sample
        y: tf.placeholder of label
        x_u: tf.placeholder of unlabeled sample
        L: number of layers
        n_cls: number of classes
        phase_train: tf.placeholder of bool used in BN
        """
        self._x = x
        self._y = y
        self._x_u = x_u
        self._L = L
        self._n_cls = n_cls
        self._phase_train = phase_train
        
        self.pred = None
        self.corrupted_encoder = None
        self.clean_encoder = None
        self.decoder = None
        self.loss = None
        self.accuracy = None

        # Build Graph
        self._construct_ssl_ladder()

    def _get_variable_by_name(self, name):

        variables = tf.get_collection(tf.GraphKeys.VARIABLES)
        for v in varialbes:
            if v.name == name:
                return v

        return None
        
    def _conv_2d(self, x, name,
                     ksize=[3, 3, 64, 64], strides=[1, 1, 1, 1], padding="SAME",
                     scope_name="conv_2d"):
        """
        Parameters
        -----------------
        x: tf.Tensor
        name: str
        ksize: list
        strides: list
        padding: str
        """
        w_name = "w-{}".format(name )
        #b_name = "b-{}".format(name)

        with tf.variable_scope(scope_name):
            v = self._get_variable_by_name(w_name)
            W = tf.get_variable(name=w_name, shape=ksize) \
              if v is None else v
            v = self._get_variable_by_name(b_name)
            #b = tf.get_variable(name=b_name, shape=[ksize[-1]]) \
            #  if v is None else v
              
        conv2d_op = tf.nn.conv2d(x, W, strides=strides, padding=padding)
        return conv2d_op
        
    def _max_pooling_2d(self, x, name,
                            ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME"):
        """
        Parameters
        -----------------
        x: tf.Tensor
        name: str
        ksize: list
        strides: list
        padding: str
        """

        max_pooling_2d_op = \
          tf.nn.max_pool(x, ksize=ksize, strides=strides, padding=padding)
        return max_pooling_2d_op

    def _linear(self, x, name, out_dim, scope_name="linear"):
        in_dim = 1
        for dim in x.get_shape()[1:]:
            in_dim *= dim.value

        w_name = "w-{}".format(name)
        #b_name = "b-{}".format(name)

        with tf.variable_scope(scope_name):
            v = self._get_variable_by_name(w_name)
            if v is None:
            W = tf.get_variable(name=w_name, shape=[in_dim, out_dim]) \
              if v is None else v
            #v = tf.get_variable(name=b_name, shape=[out_dim])
            #b = self._get_variable_by_name(w_name) \
            #  if v is None else v
            
        x_ = tf.reshape(x, [-1, in_dim])
        linear_op = tf.matmul(x_, W)

        return linear_op

    def _g(self, z_noise, u):
        pass

    def _scaling_and_bias(self, x, name,
                              scope_name="scaling_and_bias"):
        # Determine affine or conv
        shape = x.get_shape()
        depth = shape[-1].value
        if len(shape) == 4:  # NHWC
            axes = [0, 1, 2]
        else:
            axes = [0]

        beta_name = "beta-{}".format(name)
        gamma_name= "gamma-{}".format(name)

        with tf.variable_scope(scope_name):
            v = self._get_variable_by_name(beta_name)
            beta = tf.get_variable(name=beta_name, shape=[depth]) \
              if v is None else v
            v = self._get_variable_by_name(gamma_name)
            gamma = tf.get_variable(name=gamma_name, shape=[depth]) \
              if v is None else v

        return gamma * (x - beta)

    def _moments(self, x):
        """Compute mean and variance

        Compute mean and variance but return std.
        In addition, update running mean. 

        Returns
        -----------
        tuple of op: mean and std
        """
        
        # Batch mean/var and gamma/beta
        batch_mean, batch_var = tf.nn.moments(x, axes=axes)

        # Moving average
        ema = tf.train.ExponentialMovingAverage(decay=0.5)

        # Train phase
        def mean_var_with_update():
            ema_apply_op = ema.apply([batch_mean, batch_var])
            with tf.control_dependencies([ema_apply_op]):  # ema op computed here
                return tf.identity(batch_mean), tf.identity(batch_var)
            
        mean, var = tf.cond(self._phase_train,
                                mean_var_with_update,
                                lambda: (ema.average(batch_mean), ema.average(batch_var)))

        return mean, tf.sqrt(var)

    def _batch_norm(self, x, mu, std):
        return (x - mu) / std
        
    def _compute_loss(self, ):
        loss = tf.nn.softmax_cross_entropy_with_logits(self.pred, self._y)
        self.loss = tf.reduce_mean(loss)

    def _accuracy(self, ):

        pred = self.pred
        y = self._y

        correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        self.accuracy = accuracy

    def _construct_ssl_ladder(self, x, y=None):
        """Construct SSL Ladder Network

        If y is None, reonstruction cost is only computed;
        otherwise add the classification loss.
        
        """
        
        mu_list = []
        std_list = []
        z_list = []
        z_noise_list = []
        z_recon_list = []
        lambda_list = [1] * self._L

        #TODO: code loss
        #TODO: code classifier
        #TODO: code accuracy
        #TODO: separate labeled and unlabeled sample
        
        # Encoder
        h = x
        h_noise = h + tf.truncated_normal(h.get_shape())
        for i in range(self._L):
            # Clean encoder
            scope_linear = tf.variable_scope("linear")
            z_pre = self._linear(h, name="{}-th".format(i), 100, scope_linear)
            scope_linear.reuse = True

            mu, std = self._moments(z_pre)
            mu_list.append(mu)
            std_list.append(std)

            z = self._batch_norm(z_pre, mu, std)
            z_list.append(z)
            scope_scaling_and_bias = tf.variable_scope("scaling_and_bias")
            h = tf.nn.tanh(self._scaling_and_bias(z, name="{}-th".format(i)),
                               scope_scaling_and_bias)
            scope_scaling_and_bias.reuse= True

            # Corrupted encoder
            Wh = self._linear(h_noise, name="{}-th".format(i), 100, scope_linear)
            mu, std = self._moments(Wh)
            z_noize = self._batch_norm(Wh, mu, std) \
              + tf.truncated_normal(Wh.get_shape())
            z_noise_list.append(z_noize)
            h_noise = tf.nn.tanh(self._scaling_and_bias(z_noise, name="{}-th".format(i)),
                                     scope_scaling_and_bias)
            
        # Decoder
        for i in range(self._L).reverse():
            if i == self._L - 1:
                mu, std = self._moments(h_noise)
                u = self._batch_norm(h_noise, mu, std)
            else:
                Vz_recon = self._linear(z_recon, name="{}-th".format(i), 100)
                mu, std = self._moments(Vz_recon)
                u = self._batch_norm(Vz_recon, mu, std)

            z_noise = z_noise_list[i]
            z_recon = self._g(z_noize, u)

            mu = mu_list[i]
            std = std_list[i]
            z_recon_bn = self._batch_norm(z_recon, mu, std)

        # Loss

        # Acc
        

        