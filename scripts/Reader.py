import MFRC522


class Reader:
    def __init__(self):
        # Create an object of the class MFRC522
        self.reader = MFRC522.MFRC522()

    def read_card(self):
        # Scan for cards
        status, tag_type = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)

        # If a card is found
        if status == self.reader.MI_OK:
            print "Card detected"

        # Get the UID of the card
        (status, uid) = self.reader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == self.reader.MI_OK:
            return ''.join((str(x) for x in uid))
        else:
            return None
