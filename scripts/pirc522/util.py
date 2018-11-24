
class RFIDUtil(object):
    rfid = None
    method = None
    key = None
    uid = None
    last_auth = None

    debug = False

    def __init__(self, rfid):
        self.rfid = rfid

    def block_addr(self, sector, block):
        """
        Returns block address of spec. block in spec. sector.
        """
        return sector * 4 + block

    def sector_string(self, block_address):
        """
        Returns sector and it's block representation of block address, e.g.
        S01B03 for sector trailer in second sector.
        """
        return "S" + str((block_address - (block_address % 4)) / 4) + "B" + str(block_address % 4)

    def set_tag(self, uid):
        """
        Sets tag for further operations.
        Calls deauth() if card is already set.
        Calls RFID select_tag().
        Returns called select_tag() error state.
        """
        if self.debug:
            print("Selecting UID " + str(uid))

        if self.uid != None:
            self.deauth()

        self.uid = uid
        return self.rfid.select_tag(uid)

    def auth(self, auth_method, key):
        """
        Sets authentication info for current tag
        """
        self.method = auth_method
        self.key = key

        if self.debug:
            print("Changing used auth key to " + str(key) + " using method " + ("A" if auth_method == self.rfid.auth_a else "B"))

    def deauth(self):
        """
        Resets authentication info. Calls stop_crypto() if RFID is in auth state
        """
        self.method = None
        self.key = None
        self.last_auth = None

        if self.debug:
            print("Changing auth key and method to None")

        if self.rfid.authed:
            self.rfid.stop_crypto()
            if self.debug:
                print("Stopping crypto1")

    def is_tag_set_auth(self):
        return (self.uid != None) and (self.key != None) and (self.method != None)

    def do_auth(self, block_address, force=False):
        """
        Calls RFID card_auth() with saved auth information if needed.
        Returns error state from method call.
        """
        auth_data = (block_address, self.method, self.key, self.uid)
        if (self.last_auth != auth_data) or force:
            if self.debug:
                print("Calling card_auth on UID " + str(self.uid))

            self.last_auth = auth_data
            return self.rfid.card_auth(self.method, block_address, self.key, self.uid)
        else:
            if self.debug:
                print("Not calling card_auth - already authed")
            return False

    def write_trailer(self, sector, key_a=(0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF), auth_bits=(0xFF, 0x07, 0x80), 
                      user_data=0x69, key_b=(0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF)):
        """
        Writes sector trailer of specified sector. Tag and auth must be set - does auth.
        If value is None, value of byte is kept.
        Returns error state.
        """
        addr = self.block_addr(sector, 3)
        return self.rewrite(addr, key_a[:6] + auth_bits[:3] + (user_data, ) + key_b[:6])

    def rewrite(self, block_address, new_bytes):
        """
        Rewrites block with new bytes, keeping the old ones if None is passed. Tag and auth must be set - does auth.
        Returns error state.
        """
        if not self.is_tag_set_auth():
            return True

        error = self.do_auth(block_address)
        if not error:
            (error, data) = self.rfid.read(block_address)
            if not error:
                for i in range(len(new_bytes)):
                    if new_bytes[i] != None:
                        if self.debug:
                            print("Changing pos " + str(i) + " with current value " + str(data[i]) + " to " + str(new_bytes[i]))

                        data[i] = new_bytes[i]

                error = self.rfid.write(block_address, data)
                if self.debug:
                    print("Writing " + str(data) + " to " + self.sector_string(block_address))

        return error

    def read_out(self, block_address):
        """
        Prints sector/block number and contents of block. Tag and auth must be set - does auth.
        """
        if not self.is_tag_set_auth():
            return True

        error = self.do_auth(block_address)
        if not error:
            (error, data) = self.rfid.read(block_address)
            print(self.sector_string(block_address) + ": " + str(data))
        else:
            print("Error on " + self.sector_string(block_address))

    def get_access_bits(self, c1, c2, c3):
        """
        Calculates the access bits for a sector trailer based on their access conditions
        c1, c2, c3, c4 are 4 items tuples containing the values for each block
        returns the 3 bytes for the sector trailer
        """
        byte_6 = ((~c2[3] & 1) << 7) + ((~c2[2] & 1) << 6) + ((~c2[1] & 1) << 5) + ((~c2[0] & 1) << 4) + \
                 ((~c1[3] & 1) << 3) + ((~c1[2] & 1) << 2) + ((~c1[1] & 1) << 1) + (~c1[0] & 1)
        byte_7 = ((c1[3] & 1) << 7) + ((c1[2] & 1) << 6) + ((c1[1] & 1) << 5) + ((c1[0] & 1) << 4) + \
                 ((~c3[3] & 1) << 3) + ((~c3[2] & 1) << 2) + ((~c3[1] & 1) << 1) + (~c3[0] & 1)
        byte_8 = ((c3[3] & 1) << 7) + ((c3[2] & 1) << 6) + ((c3[1] & 1) << 5) + ((c3[0] & 1) << 4) + \
                 ((c2[3] & 1) << 3) + ((c2[2] & 1) << 2) + ((c2[1] & 1) << 1) + (c2[0] & 1)
        return byte_6, byte_7, byte_8

    def dump(self, sectors=16):
        for i in range(sectors * 4):
            self.read_out(i)
