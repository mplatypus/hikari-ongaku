class OngakuBaseException(Exception):
    """
    The base exception for all Ongaku exceptions.
    """


class ResponseException(OngakuBaseException):
    """
    Raised when a 4XX or 5XX error gets recieved.
    """


class BuildException(OngakuBaseException):
    """
    Raised when a model fails to build correctly.
    """


class LavalinkException(OngakuBaseException):
    """
    Raised when an error is returned on the websocket, or a rest command.
    """


class NodeException(OngakuBaseException):
    """
    Base node exception.
    """


class NodeMissingException(NodeException):
    """
    Raised when a node is missing.
    """


class SessionNotStartedException(LavalinkException):
    """
    Raised when the session id is needed, but is null.
    """


class PlayerException(OngakuBaseException):
    """
    Base player related exceptions
    """


class PlayerVolumeLevelException(PlayerException):
    """
    Raised when an invalid volume is set.
    """

class PlayerMissingException(PlayerException):
    """
    Raised when the player does not exist.
    """