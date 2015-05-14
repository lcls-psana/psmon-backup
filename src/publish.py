import sys
from psmon import app, config, client


class _Publish(object):
    """
    Class for handling the functionality of the publish module.

    A single instance of this class is created on import of the module. It 
    then replaces the module reference in sys.modules. 

    Attributes:
     - local: Used to set the local publishing state of the module. If the local 
            flag of the publish module is set then all plots are published to 
            a client launched locally.
     - disabled: Indicates if  autoconnection on send attempts for the publish 
            module have been disabled.
     - port: The tcp port to use for the ZMQ data connection.
     - client_opts: An instance of the ClientInfo class that is used for 
            determining the configuration settings for ZMQ connections.
     - plot_opts: An instance of the PlotInfo class used by local plotting 
            clients when launched. Individual clients will not pick up changes 
            to the plot_opts made after they are spawned.
     - active_clients: Dictionary of current local plot clients.
    """
    def __init__(
            self,
            port=config.APP_PORT,
            bufsize=config.APP_BUFFER,
            local=config.APP_LOCAL,
            renderer=config.APP_CLIENT,
            rate=config.APP_RATE,
            recv_limit=config.APP_RECV_LIMIT
        ):
        self.local = local
        self.disabled = False
        self.port = port
        self._publisher = app.ZMQPublisher()
        self._reset_listener = app.ZMQListener(self._publisher.comm_socket)
        self.client_opts = app.ClientInfo(
            None,
            None,
            bufsize,
            rate,
            recv_limit,
            None,
            renderer,
            False
        )
        self.plot_opts = app.PlotInfo()
        self.active_clients = {}

    @property
    def initialized(self):
        return self._publisher.initialized

    def send(self, topic, data):
        """
        Publishes a data object to all clients suscribed to the topic.

        Arguments
         - topic: The name of the topic to which the data is being published.
         - data: The data object to be published to suscribers.
        """
        if not self.initialized and not self.disabled:
            try:
                from mpi4py import MPI
                if MPI.COMM_WORLD.Get_rank() == 0:
                    self.init()
                else:
                    raise app.PublishError('Cannot send messages on a non-rank-zero MPI process without explicitly calling publish.init')
            except ImportError:
                self.init()

        if self.local:
            if topic in self.active_clients:
                if not self.active_clients[topic].is_alive():
                    self._create_client(topic)
            else:
                self._create_client(topic)

        self._publisher.send(topic, data)

    def _create_client(self, topic):
        """
        Spawns a local client listening to the specified topic.
        """
        client_opts.data_socket_url = self._publisher.data_endpoint
        client_opts.comm_socket_url = self._publisher.comm_endpoint
        client_opts.topic = topic
        self.active_clients[topic] = client.spawn_process(client_opts, self.plot_opts)

    def init(self, port=None, bufsize=None, local=None):
        """
        Initializes the publish module.

        Optional arguments
         - port: The tcp port number to use with the publish module.
         - bufsize: The zmq buffer size to use with the publish module.
         - local: When true all plots are published to a client launched locally.
        """
        if port is not None:
            self.port = port
        if bufsize is not None:
            self.client_opts.buffer = bufsize
        if local is not None:
            self.local = local
        self._publisher.initialize(self.port, self.client_opts.buffer, self.local)
        self._reset_listener.start()
        # turn off further autoconnect attempts
        self.disabled = True

    def reset(self):
        """
        Resets the publish module to an uninitialized state. All socket 
        connections are closed and the port bindings released.
        """
        pass

    def register_handler(name, **kwargs):
        """
        Registers a message handler for recieving messages from suscribed clients.

        Arguments
         - name: all messages sent from clients with this header will be handled by
        this message handler

        Returns a refernce to the newly created handler.
        """
        return self._reset_listener.register_handler(name, **kwargs)

    def get_handler(name):
        """
        Returns a referenced to the named message handler.

        Arguments:
         - name: the header string/identifier of the requested handler
        """
        return self._reset_listener.message_handler.get(name)

    def get_reset_flag():
        """
        Gets the state of the client reset flag. This will be set if any client 
        has sent a reset message, and will remain set until cleared.
        """
        return self._reset_listener.get_flag()

    def clear_reset_flag():
        """
        Clears any set reset flags.
        """
        self._reset_listener.clear_flag()


sys.modules[__name__] = _Publish()
