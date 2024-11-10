import struct

class MessageDecoderError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return f"Error MessageDecoder: {self.message}"

class MessageDecoder:

    @staticmethod
    async def decode(msg):
        try:
            msg_len, msg_id = struct.unpack('>Ib', msg[:5])
        except Exception as e:
             print("unpacking error")
        
        dict_msg_id = {
            0: 'Choke',
            1: 'UnChoke',
            2: 'Interested',
            3: 'NotInterested',
            4: 'Have',
            5: 'BitField',
            6: 'Request',
            7: 'Piece',
            8: 'Cancel',
            9: 'Port'
        }
        
        if msg_id not in list(dict_msg_id.keys()):
            if msg_len == 0:
                pass
            else:
                raise MessageDecoderError("invalid message id error")

        return msg_id

        