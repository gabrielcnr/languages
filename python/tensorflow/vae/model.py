import tensorflow as tf

class VAE(object):

    def __init__(self, x, mid_dim=100):
        """
        Attributes:
          x: tf.placeholder
            dimension of x 2-d whose shape is [None, 784] in case of MNIST
          dims (int): dimension of intermidiate layers
        """

        self._initialized = True
        self._x = x
        self._in_dim = self._x.get_shape()[1].value
        self._mid_dim = mid_dim
        
        self.encode = None
        self.decode = None
        self.obj = None

        self._variables = set()
        
        self._mean = None
        self._std = None

        # Build Graph 
        self._build_graph()

    def _MLP(self, x, in_dim, out_dim, scope):
        with scope: 
            # Parameter
            W = tf.Variable(
                tf.truncated_normal(shape=[in_dim, out_dim]))
            b = tf.Variable(
                tf.truncated_normal(shape=[out_dim]))

        # Add to the set of variables
        self._variables.add(W)
        self._variables.add(b)

        h = tf.matmul(x, W) + b

        return h

    def _encode(self, ):
        # MLP
        enc_scope = tf.variable_scope("encoder")
        h = self._MLP(self._x, self._in_dim, self._mid_dim, enc_scope)

        # Compute stats
        self._compute_stats(h)

        # Reparamiterization trick
        noise = tf.truncated_normal(shape=[self._mid_dim])
        z = self._mu + self._sigma * noise

        self.encode = z

    def _compute_stats(self, h):
        # MLP for mu
        enc_scope = tf.variable_scope("encoder")
        mu = self._MLP(h, self._mid_dim, self._mid_dim, enc_scope)
        self._mu = mu

        # MLP for sigma
        enc_scope = tf.variable_scope("encoder")
        sigma = self._MLP(h, self._mid_dim, self._mid_dim, enc_scope)
        self._sigma = sigma
            
    def _decode(self):
        # MLP
        dec_scopea = tf.variable_scope("decoder")
        h0 = self._MLP(self.encode, self._mid_dim, self._mid_dim, dec_scopea)

        dec_scopea = tf.variable_scope("decoder")
        h1 = self._MLP(h0, self._mid_dim, self._in_dim, dec_scopea)
        y = tf.nn.sigmoid(h1)

        self.decode = y
        
    def _compute_loss(self, ):
        # Encoder loss
        mu_square = self._mu**2
        sigma_square = self._sigma**2
        kl_divergence = \
          tf.reduce_sum(1 + tf.log(sigma_square) - mu_square - sigma_square, 
              reduction_indices=[1])
        encoder_loss = tf.reduce_mean(kl_divergence)

        # Decoder loss
        x = self._x
        y = self.decode
        #binary_cross_entropy = \  # this code will be overflow
        #  tf.reduce_sum(x * tf.log(y) + (1 - x) * tf.log(1 - y), reduction_indices=[1])

        # Note tf.nn.sigmoid_cross_entropy_with_logits returns `minus`
        binary_cross_entropy = - tf.nn.sigmoid_cross_entropy_with_logits(y, x)
        decoder_loss = tf.reduce_mean(binary_cross_entropy)
        
        self.obj = encoder_loss + decoder_loss

    def _build_graph(self):

        # Bulid encoder network
        self._encode()

        # Bulid decoder network
        self._decode()

        # Compute loss
        self._compute_loss()
        