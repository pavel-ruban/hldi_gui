# This is abstract generic communication class & is used by factory to provide communication plugins
# e.g. Uart Usb Ethernet Wifi & the rest.

class Abstract:
    def connect(self, **options):
       NotImplementedError("Class %s doesn't implement aMethod()" % (self.__class__.__name__))

    def close(self):
       NotImplementedError("Class %s doesn't implement aMethod()" % (self.__class__.__name__))

    def send(self, input):
       NotImplementedError("Class %s doesn't implement aMethod()" % (self.__class__.__name__))

    def listen(self, **kwargs):
       NotImplementedError("Class %s doesn't implement aMethod()" % (self.__class__.__name__))

    def isOpen(self, **kwargs):
       NotImplementedError("Class %s doesn't implement aMethod()" % (self.__class__.__name__))
