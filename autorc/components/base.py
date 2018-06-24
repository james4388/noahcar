class Component(object):
    ''' Base class for car components '''
    is_threading = False         # This component runing in its own thread

    def __init__(self, *args, **kwargs):
        super(Component, self).__init__(*args, **kwargs)

    def process(self, context, *args):
        ''' This method is call by main loop to update data '''
        raise NotImplementedError

    def get_output(self, context, *args):
        ''' Get output from component '''
        if not self.is_threading:
            return self.process(context, *args)
        return self.output

    def start(self, stop_event, context, *args):
        ''' This method is call by Thread to start a new loop '''
        while not stop_event.is_set():  # Listen for stop event
            self.output = self.process(context, *args)

        if callable(getattr(self, 'shutdown', None)):
            self.shutdown()

    def shutdown(self):
        ''' Free all resource '''
        self.output = None
